import logging
import os
import socket
import sys
import time
from collections.abc import Iterable, Iterator
from typing import TYPE_CHECKING, Any, Optional, Union

import redis.sentinel
from prometheus_client import Counter, Gauge

from tilecloud import Tile, TileStore
from tilecloud.store.queue import decode_message, encode_message

if TYPE_CHECKING:
    Redis = redis.Redis[str]
else:
    Redis = redis.Redis

STREAM_GROUP = "tilecloud"
CONSUMER_NAME = socket.gethostname() + "-" + str(os.getpid())

logger = logging.getLogger(__name__)

_NB_MESSAGE_COUNTER = Gauge("tilecloud_redis_nb_messages", "Number of messages in Redis", ["name"])
_PENDING_COUNTER = Gauge("tilecloud_redis_pending", "Number of pending messages in Redis", ["name"])
_DECODE_ERROR_COUNTER = Counter("tilecloud_redis_decode_error", "Number of decode errors on Redis", ["name"])
_READ_ERROR_COUNTER = Counter("tilecloud_redis_read_error", "Number of read errors on Redis", ["name"])
_DROPPED_COUNTER = Counter("tilecloud_redis_dropped", "Number of dropped messages on Redis", ["name"])
_STOLEN_COUNTER = Counter("tilecloud_redis_stolen", "Number of stolen messages on Redis", ["name"])


class RedisTileStore(TileStore):
    """
    Redis queue.
    """

    _master: Redis
    _slave: Redis

    def __init__(
        self,
        url: Optional[str] = None,
        name: str = "tilecloud",
        stop_if_empty: bool = True,
        timeout: int = 5,
        pending_timeout: int = 5 * 60,
        max_retries: int = 5,
        max_errors_age: int = 24 * 3600,
        max_errors_nb: int = 100,
        pending_count: int = 10,
        pending_max_count: int = sys.maxsize,
        sentinels: Optional[list[tuple[str, int]]] = None,
        service_name: str = "mymaster",
        sentinel_kwargs: Any = None,
        connection_kwargs: Any = None,
        **kwargs: Any,
    ):
        super().__init__(**kwargs)

        connection_kwargs = connection_kwargs or {}

        if sentinels is not None:
            logger.debug("Initialize using sentinels")
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
        self._pending_count = pending_count
        self._pending_max_count = pending_max_count
        if not name.startswith("queue_"):
            name = "queue_" + name
        self._name_str = name
        self._name = name.encode("utf-8")
        self._errors_name = self._name + b"_errors"
        try:
            logger.debug(
                "Create the Redis stream name: %s, group name: %s, id: 0-0, MKSTREAM", name, STREAM_GROUP
            )
            self._master.xgroup_create(name=self._name, groupname=STREAM_GROUP, id="0-0", mkstream=True)
        except redis.ResponseError as error:
            if "BUSYGROUP" not in str(error):
                raise

    def __contains__(self, tile: Tile) -> bool:
        return False

    def get_one(self, tile: Tile) -> Tile:
        return tile

    def list(self) -> Iterator[Tile]:
        count = 0
        while True:
            try:
                logger.debug(
                    "Wait for new tiles, group name: %s, consumer name: %s, streams: %s, count: 1, "
                    "block: %s",
                    STREAM_GROUP,
                    CONSUMER_NAME,
                    self._name,
                    round(self._timeout_ms),
                )
                queues = self._master.xreadgroup(
                    groupname=STREAM_GROUP,
                    consumername=CONSUMER_NAME,
                    streams={self._name: ">"},
                    count=1,
                    block=round(self._timeout_ms),
                )
                logger.debug("Get %d new elements", len(queues))

                if not queues:
                    queues, has_pendings = self._claim_olds()
                    if not has_pendings:
                        _NB_MESSAGE_COUNTER.labels(self._name_str).set(0)
                        _PENDING_COUNTER.labels(self._name_str).set(0)
                        if self._stop_if_empty:
                            break
                if queues:
                    for redis_message in queues:
                        queue_name, queue_messages = redis_message
                        assert queue_name == self._name
                        for message in queue_messages:
                            id_, body = message
                            try:
                                tile = decode_message(body[b"message"], from_redis=True, sqs_message=id_)
                                yield tile
                            except Exception:  # pylint: disable=broad-except
                                logger.warning("Failed decoding the Redis message", exc_info=True)
                                _DECODE_ERROR_COUNTER.labels(self._name_str).inc()
                            count += 1

                    if count % 10 == 0:
                        _NB_MESSAGE_COUNTER.labels(self._name_str).set(self._slave.xlen(self._name))
                        pending = self._slave.xpending(  # type: ignore[no-untyped-call]
                            self._name,
                            STREAM_GROUP,
                        )
                        _PENDING_COUNTER.labels(self._name_str).set(pending["pending"])
            except redis.exceptions.TimeoutError:
                logger.warning("Failed reading Redis messages", exc_info=True)
                _READ_ERROR_COUNTER.labels(self._name_str).inc()
                time.sleep(1)

    def put_one(self, tile: Tile) -> Tile:
        try:
            logger.debug(
                "Add tile to the Redis stream name: %s, fields: %s", self._name, encode_message(tile)
            )
            self._master.xadd(name=self._name, fields={"message": encode_message(tile)})
        except Exception as exception:  # pylint: disable=broad-except
            logger.warning("Failed sending Redis message", exc_info=True)
            tile.error = exception
        return tile

    def put(self, tiles: Iterable[Tile]) -> Iterator[Tile]:
        for tile in tiles:
            self.put_one(tile)
            yield tile

    def delete_one(self, tile: Tile) -> Tile:
        # Once consumed from redis, we don't have to delete the tile from the queue.
        assert hasattr(tile, "from_redis")
        assert hasattr(tile, "sqs_message")
        assert tile.from_redis is True
        logger.debug(
            "Acknowledge tile from Redis stream name: %s, group name: %s, sqs message: %s",
            self._name,
            STREAM_GROUP,
            tile.sqs_message,
        )
        self._master.xack(self._name, STREAM_GROUP, tile.sqs_message)  # type: ignore[no-untyped-call]
        logger.debug("Delete tile from Redis stream name: %s, sqs message: %s", self._name, tile.sqs_message)
        self._master.xdel(self._name, tile.sqs_message)
        return tile

    def delete_all(self) -> None:
        """
        Used only by tests.
        """
        logger.debug("Delete all tiles from Redis stream name: %s", self._name)
        self._master.xtrim(name=self._name, maxlen=0)
        # xtrim doesn't empty the group claims. So we have to delete and re-create groups
        logger.debug("Delete all tiles from Redis stream name: %s, group name: %s", self._name, STREAM_GROUP)
        self._master.xgroup_destroy(name=self._name, groupname=STREAM_GROUP)  # type: ignore[no-untyped-call]
        logger.debug(
            "Create the Redis stream name: %s, group name: %s, id: 0-0, MKSTREAM", self._name, STREAM_GROUP
        )
        self._master.xgroup_create(name=self._name, groupname=STREAM_GROUP, id="0-0", mkstream=True)
        logger.debug(
            "Delete all tiles from Redis stream name: %s, group name: %s", self._errors_name, STREAM_GROUP
        )
        self._master.xtrim(name=self._errors_name, maxlen=0)

    def _claim_olds(self) -> tuple[Iterable[tuple[bytes, Any]], bool]:
        logger.debug("Claim old's")
        to_steal: list[int] = []
        to_drop: list[int] = []
        min_ = 1
        has_pendings = False
        while len(to_steal) + len(to_drop) < self._pending_count:
            if min_ > self._pending_max_count:
                break
            logger.debug(
                "Get pending messages, name: %s, group name: %s, min: %d, max: +, count: %d",
                self._name,
                STREAM_GROUP,
                min_,
                self._pending_count,
            )
            pendings = self._master.xpending_range(
                name=self._name, groupname=STREAM_GROUP, min=min_, max="+", count=self._pending_count
            )
            if not pendings:
                logger.debug("Empty pending")
                # None means there is nothing pending
                break
            min_ += self._pending_count
            has_pendings = True

            for pending in pendings:
                logger.debug(
                    "Pending for %d, threshold %d",
                    int(pending["time_since_delivered"]),
                    self._pending_timeout_ms,
                )
                if int(pending["time_since_delivered"]) >= self._pending_timeout_ms:
                    id_ = pending["message_id"]
                    nb_retries = int(pending["times_delivered"])
                    if nb_retries <= self._max_retries:
                        logger.info(
                            "A message has been pending for too long. Stealing it (retry #%d): %s",
                            nb_retries,
                            id_,
                        )
                        to_steal.append(id_)
                    else:
                        logger.warning(
                            "A message has been pending for too long and retried too many times. "
                            "Dropping it: %s",
                            id_,
                        )
                        to_drop.append(id_)

        logger.debug("%d elements to drop", len(to_drop))
        if to_drop:
            logger.debug(
                "Claim old's name: %s, group name: %s, consumer name: %s, min idle time: %d, message ids: %s",
                self._name,
                STREAM_GROUP,
                CONSUMER_NAME,
                self._pending_timeout_ms,
                to_drop,
            )
            drop_messages = self._master.xclaim(  # type: ignore[no-untyped-call]
                name=self._name,
                groupname=STREAM_GROUP,
                consumername=CONSUMER_NAME,
                min_idle_time=self._pending_timeout_ms,
                message_ids=to_drop,
            )
            drop_ids = [drop_message[0] for drop_message in drop_messages]
            logger.debug(
                "Acknowledge old's name: %s, group name: %s, message ids: %s",
                self._name,
                STREAM_GROUP,
                drop_ids,
            )
            self._master.xack(self._name, STREAM_GROUP, *drop_ids)  # type: ignore[no-untyped-call]
            logger.debug("Delete old's name: %s, message ids: %s", self._name, drop_ids)
            self._master.xdel(self._name, *drop_ids)
            for _, drop_message in drop_messages:
                tile = decode_message(drop_message[b"message"])
                logger.debug(
                    "Add to errors name: %s, tile coord: %s, max len: %s",
                    self._errors_name,
                    tile.tilecoord,
                    self._max_errors_nb,
                )
                self._master.xadd(
                    name=self._errors_name,
                    fields={"tilecoord": str(tile.tilecoord)},
                    maxlen=self._max_errors_nb,
                )
            _DROPPED_COUNTER.labels(self._name_str).inc(len(to_drop))

        logger.debug("%d elements to steal", len(to_steal))
        if to_steal:
            logger.debug(
                "Claim old's name: %s, group name: %s, consumer name: %s, min idle time: %d, message ids: %s",
                self._name,
                STREAM_GROUP,
                CONSUMER_NAME,
                self._pending_timeout_ms,
                to_steal,
            )
            messages = self._master.xclaim(  # type: ignore[no-untyped-call]
                name=self._name,
                groupname=STREAM_GROUP,
                consumername=CONSUMER_NAME,
                min_idle_time=self._pending_timeout_ms,
                message_ids=to_steal,
            )
            _STOLEN_COUNTER.labels(self._name_str).inc(len(to_steal))
            return [(self._name, messages)], has_pendings
        # Empty means there are pending jobs, but they are not old enough to be stolen
        return [], has_pendings

    def get_status(self) -> dict[str, Union[str, int]]:
        """
        Returns a map of stats.
        """
        nb_messages = self._slave.xlen(self._name)
        pending = self._slave.xpending(self._name, STREAM_GROUP)  # type: ignore[no-untyped-call]
        tiles_in_error = self._get_errors()

        _NB_MESSAGE_COUNTER.labels(self._name_str).set(nb_messages)
        return {
            "Approximate number of tiles to generate": nb_messages,
            "Approximate number of generating tiles": pending["pending"],
            "Tiles in error": ", ".join(tiles_in_error),
        }

    def _get_errors(self) -> set[str]:
        now, now_us = self._slave.time()
        old_timestamp = (now - self._max_errors_age) * 1000 + now_us / 1000

        errors = self._slave.xrange(name=self._errors_name)
        tiles_in_error = set()
        old_errors = []
        for error_id, error_message in errors:
            timestamp = int(error_id.decode().split("-")[0])
            if timestamp <= old_timestamp:
                old_errors.append(error_id)
            else:
                tiles_in_error.add(error_message[b"tilecoord"].decode())
        if old_errors:
            logger.info("Deleting %d old errors, name: %s", len(old_errors), self._errors_name)
            self._master.xdel(self._errors_name, *old_errors)
        return tiles_in_error
