import logging
import os
import socket
from typing import Any, Dict, Iterable, Iterator, List, Optional, Set, Tuple, Union

from c2cwsgiutils import stats
import redis.sentinel

from tilecloud import Tile, TileStore
from tilecloud.store.queue import decode_message, encode_message

STREAM_GROUP = "tilecloud"
CONSUMER_NAME = socket.gethostname() + "-" + str(os.getpid())

logger = logging.getLogger(__name__)


class Queue:
    def __init__(self, name_str: str, name: bytes, errors_name: bytes):
        self.name_str = name_str
        self.name = name
        self.errors_name = errors_name


class RedisTileStore(TileStore):
    """
    Redis queue.
    """

    def __init__(
        self,
        url: Optional[str] = None,
        name: Optional[str] = "tilecloud",
        stop_if_empty: bool = True,
        timeout: int = 5,
        pending_timeout: int = 5 * 60,
        max_retries: int = 5,
        max_errors_age: int = 24 * 3600,
        max_errors_nb: int = 100,
        sentinels: Optional[List[Tuple[str, int]]] = None,
        service_name: str = "mymaster",
        sentinel_kwargs: Any = None,
        connection_kwargs: Any = None,
        **kwargs: Any,
    ):
        super().__init__(**kwargs)

        connection_kwargs = connection_kwargs or {}

        if sentinels is not None:
            sentinel = redis.sentinel.Sentinel(
                sentinels, sentinel_kwargs=sentinel_kwargs, **connection_kwargs
            )
            self._master = sentinel.master_for(service_name)
            self._slave = sentinel.slave_for(service_name)
        else:
            assert url is not None
            self._master = redis.Redis.from_url(url, **connection_kwargs)
            self._slave = self._master

        self._stop_if_empty = stop_if_empty
        self._timeout_ms = int(timeout * 1000)
        self._pending_timeout_ms = int(pending_timeout * 1000)
        self._max_retries = max_retries
        self._max_errors_age = max_errors_age
        self._max_errors_nb = max_errors_nb
        self._queues: Dict[str, Queue] = {}
        if name is not None:
            self.add_queue(name)

    def add_queue(self, name: str) -> None:
        if not name.startswith("queue_"):
            name = "queue_" + name
        name_b = name.encode("utf-8")
        self._queues[name] = Queue(name, name_b, name_b + b"_errors")

        try:
            self._master.xgroup_create(name=name_b, groupname=STREAM_GROUP, id="0-0", mkstream=True)
        except redis.ResponseError as e:
            if "BUSYGROUP" not in str(e):
                raise

    def __contains__(self, tile: Tile) -> bool:
        return False

    @staticmethod
    def get_one(tile: Tile) -> Tile:
        return tile

    def list(self) -> Iterator[Tile]:
        count = 0
        while True:
            queues = self._master.xreadgroup(
                groupname=STREAM_GROUP,
                consumername=CONSUMER_NAME,
                streams={list(self._queues.values())[0]: ">"},
                count=1,
                block=round(self._timeout_ms),
            )
            logger.debug("Get %d new elements", len(queues))

            if not queues:
                queues = self._claim_olds()
                if queues is None:
                    stats.set_gauge(["redis", list(self._queues.values())[0].name_str, "nb_messages"], 0)
                    stats.set_gauge(["redis", list(self._queues.values())[0].name_str, "pending"], 0)
                if queues is None and self._stop_if_empty:
                    break
            if queues:
                for redis_message in queues:
                    queue_name, queue_messages = redis_message
                    assert queue_name == list(self._queues.values())[0].name
                    for message in queue_messages:
                        id_, body = message
                        try:
                            tile = decode_message(body[b"message"], from_redis=True, sqs_message=id_)
                            yield tile
                        except Exception:
                            logger.warning("Failed decoding the Redis message", exc_info=True)
                            stats.increment_counter(
                                ["redis", list(self._queues.values())[0].name_str, "decode_error"]
                            )
                        count += 1

                if count % 10 == 0:
                    stats.set_gauge(
                        ["redis", list(self._queues.values())[0].name_str, "nb_messages"],
                        self._slave.xlen(name=list(self._queues.values())[0].name),
                    )
                    pending = self._slave.xpending(list(self._queues.values())[0].name, STREAM_GROUP)
                    stats.set_gauge(
                        ["redis", list(self._queues.values())[0].name_str, "pending"], pending["pending"]
                    )

    def put_one(self, tile: Tile) -> Tile:
        try:
            self._master.xadd(
                name=list(self._queues.values())[0].name, fields={"message": encode_message(tile)}
            )
        except Exception as e:
            logger.warning("Failed sending Redis message", exc_info=True)
            tile.error = e
        return tile

    def put(self, tiles: Iterable[Tile]) -> Iterator[Tile]:
        for tile in tiles:
            self.put_one(tile)
            yield tile

    def delete_one(self, tile: Tile) -> Tile:
        # Once consumed from redis, we don't have to delete the tile from the queue.
        assert hasattr(tile, "from_redis")
        assert hasattr(tile, "sqs_message")
        assert tile.from_redis is True  # type: ignore
        self._master.xack(list(self._queues.values())[0].name, STREAM_GROUP, tile.sqs_message)  # type: ignore
        self._master.xdel(list(self._queues.values())[0].name, tile.sqs_message)  # type: ignore
        return tile

    def delete_all(self) -> None:
        """
        Used only by tests.
        """
        self._master.xtrim(name=list(self._queues.values())[0].name, maxlen=0)
        # xtrim doesn't empty the group claims. So we have to delete and re-create groups
        self._master.xgroup_destroy(name=list(self._queues.values())[0].name, groupname=STREAM_GROUP)
        self._master.xgroup_create(
            name=list(self._queues.values())[0].name, groupname=STREAM_GROUP, id="0-0", mkstream=True
        )
        self._master.xtrim(name=list(self._queues.values())[0].errors_name, maxlen=0)

    def _claim_olds(self) -> Optional[Iterable[Tuple[bytes, Any]]]:
        logger.debug("Claim old's")
        pendings = self._master.xpending_range(
            name=list(self._queues.values())[0].name, groupname=STREAM_GROUP, min="-", max="+", count=10
        )
        if not pendings:
            logger.debug("Empty pendings")
            # None means there is nothing pending at all
            return None
        to_steal = []
        to_drop = []
        for pending in pendings:
            logger.debug(
                "Pending for %d, threshold %d", int(pending["time_since_delivered"]), self._pending_timeout_ms
            )
            if int(pending["time_since_delivered"]) >= self._pending_timeout_ms:
                id_ = pending["message_id"]
                nb_retries = int(pending["times_delivered"])
                if nb_retries < self._max_retries:
                    logger.info(
                        "A message has been pending for too long. Stealing it (retry #%d): %s",
                        nb_retries,
                        id_,
                    )
                    to_steal.append(id_)
                else:
                    logger.warning(
                        "A message has been pending for too long and retried too many times. Dropping it: %s",
                        id_,
                    )
                    to_drop.append(id_)

        logger.debug("%d elements to drop", len(to_drop))
        if to_drop:
            drop_messages = self._master.xclaim(
                name=list(self._queues.values())[0].name,
                groupname=STREAM_GROUP,
                consumername=CONSUMER_NAME,
                min_idle_time=self._pending_timeout_ms,
                message_ids=to_drop,
            )
            drop_ids = [drop_message[0] for drop_message in drop_messages]
            self._master.xack(list(self._queues.values())[0].name, STREAM_GROUP, *drop_ids)
            self._master.xdel(list(self._queues.values())[0].name, *drop_ids)
            for _, drop_message in drop_messages:
                tile = decode_message(drop_message[b"message"])
                self._master.xadd(
                    name=list(self._queues.values())[0].errors_name,
                    fields=dict(tilecoord=str(tile.tilecoord)),
                    maxlen=self._max_errors_nb,
                )
            stats.increment_counter(
                ["redis", list(self._queues.values())[0].name_str, "dropped"], len(to_drop)
            )

        logger.debug("%d elements to steal", len(to_steal))
        if to_steal:
            messages = self._master.xclaim(
                name=list(self._queues.values())[0].name,
                groupname=STREAM_GROUP,
                consumername=CONSUMER_NAME,
                min_idle_time=self._pending_timeout_ms,
                message_ids=to_steal,
            )
            stats.increment_counter(
                ["redis", list(self._queues.values())[0].name_str, "stolen"], len(to_steal)
            )
            return [(list(self._queues.values())[0].name, messages)]
        else:
            # Empty means there are pending jobs, but they are not old enough to be stolen
            return []

    def get_status(self) -> Dict[str, Union[str, int]]:
        """
        Returns a map of stats.
        """
        nb_messages = self._slave.xlen(list(self._queues.values())[0].name)
        pending = self._slave.xpending(list(self._queues.values())[0].name, STREAM_GROUP)
        tiles_in_error = self._get_errors()

        stats.set_gauge(["redis", list(self._queues.values())[0].name_str, "nb_messages"], nb_messages)
        return {
            "Approximate number of tiles to generate": nb_messages,
            "Approximate number of generating tiles": pending["pending"],
            "Tiles in error": ", ".join(tiles_in_error),
        }

    def _get_errors(self) -> Set[str]:
        now, now_us = self._slave.time()
        old_timestamp = (now - self._max_errors_age) * 1000 + now_us / 1000

        errors = self._slave.xrange(name=list(self._queues.values())[0].errors_name)
        tiles_in_error = set()
        old_errors = []
        for error_id, error_message in errors:
            timestamp = int(error_id.decode().split("-")[0])
            if timestamp <= old_timestamp:
                old_errors.append(error_id)
            else:
                tiles_in_error.add(error_message[b"tilecoord"].decode())
        if old_errors:
            logger.info("Deleting %d old errors", len(old_errors))
            self._master.xdel(list(self._queues.values())[0].errors_name, *old_errors)
        return tiles_in_error
