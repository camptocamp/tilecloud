from __future__ import absolute_import
from c2cwsgiutils import stats
import logging
import os
import redis
import socket

from tilecloud import TileStore
from tilecloud.store.queue import encode_message, decode_message

STREAM_GROUP = 'tilecloud'
CONSUMER_NAME = socket.gethostname() + '-' + str(os.getpid())

logger = logging.getLogger(__name__)


class RedisTileStore(TileStore):
    """
    Redis queue.
    """
    def __init__(self, url, name='tilecloud', stop_if_empty=True, timeout=5, pending_timeout=5 * 60, max_retries=5,
                 max_errors_age=24 * 3600, max_errors_nb=100, **kwargs):
        super(RedisTileStore, self).__init__(**kwargs)
        self._redis = redis.Redis.from_url(url)
        self._stop_if_empty = stop_if_empty
        self._timeout_ms = int(timeout * 1000)
        self._pending_timeout_ms = int(pending_timeout * 1000)
        self._max_retries = max_retries
        self._max_errors_age = max_errors_age
        self._max_errors_nb = max_errors_nb
        if not name.startswith('queue_'):
            name = 'queue_' + name
        self._name_str = name
        self._name = name.encode('utf-8')
        self._errors_name = self._name + b"_errors"
        try:
            self._redis.xgroup_create(name=self._name, groupname=STREAM_GROUP, id='0-0', mkstream=True)
        except redis.ResponseError as e:
            if 'BUSYGROUP' not in str(e):
                raise

    def __contains__(self, tile):
        return False

    @staticmethod
    def get_one(tile):
        return tile

    def list(self):
        count = 0
        while True:
            queues = self._redis.xreadgroup(groupname=STREAM_GROUP, consumername=CONSUMER_NAME,
                                            streams={self._name: '>'}, count=1, block=round(self._timeout_ms))

            if not queues:
                queues = self._claim_olds()
                stats.set_gauge(['redis', self._name_str, 'nb_messages'], 0)
                if queues is None and self._stop_if_empty:
                    break
            if queues:
                for redis_message in queues:
                    queue_name, queue_messages = redis_message
                    assert queue_name == self._name
                    for message in queue_messages:
                        id_, body = message
                        try:
                            tile = decode_message(body[b'message'], from_redis=True, sqs_message=id_)
                            yield tile
                        except Exception:
                            logger.warning('Failed decoding the Redis message', exc_info=True)
                            stats.increment_counter(['redis', self._name_str, 'decode_error'])
                        count += 1

                if count % 100 == 0:
                    stats.set_gauge(['redis', self._name_str, 'nb_messages'], self._redis.xlen(name=self._name))

    def put_one(self, tile):
        try:
            self._redis.xadd(name=self._name, fields={'message': encode_message(tile)})
        except Exception as e:
            logger.warning('Failed sending SQS message', exc_info=True)
            tile.error = e

    def put(self, tiles):
        for tile in tiles:
            self.put_one(tile)
            yield tile

    def delete_one(self, tile):
        # Once consumed from redis, we don't have to delete the tile from the queue.
        assert hasattr(tile, 'from_redis')
        assert hasattr(tile, 'sqs_message')
        assert tile.from_redis is True
        self._redis.xack(self._name, STREAM_GROUP, tile.sqs_message)
        self._redis.xdel(self._name, tile.sqs_message)
        return tile

    def delete_all(self):
        """
        Used only by tests
        """
        self._redis.xtrim(name=self._name, maxlen=0)
        # xtrim doesn't empty the group claims. So we have to delete and re-create groups
        self._redis.xgroup_destroy(name=self._name, groupname=STREAM_GROUP)
        self._redis.xgroup_create(name=self._name, groupname=STREAM_GROUP, id='0-0', mkstream=True)
        self._redis.xtrim(name=self._errors_name, maxlen=0)

    def _claim_olds(self):
        pendings = self._redis.xpending_range(name=self._name, groupname=STREAM_GROUP, min='-', max='+', count=10)
        if not pendings:
            # None means there is nothing pending at all
            return None
        to_steal = []
        to_drop = []
        for pending in pendings:
            if int(pending['time_since_delivered']) >= self._pending_timeout_ms:
                id_ = pending['message_id']
                nb_retries = int(pending['times_delivered'])
                if nb_retries < self._max_retries:
                    logger.info('A message has been pending for too long. Stealing it (retry #%d): %s', nb_retries, id_)
                    to_steal.append(id_)
                else:
                    logger.warning(
                        'A message has been pending for too long and retried too many times. Dropping it: %s', id_)
                    to_drop.append(id_)

        if to_drop:
            drop_messages = self._redis.xclaim(name=self._name, groupname=STREAM_GROUP, consumername=CONSUMER_NAME,
                                               min_idle_time=self._pending_timeout_ms, message_ids=to_drop)
            drop_ids = [drop_message[0] for drop_message in drop_messages]
            self._redis.xack(self._name, STREAM_GROUP, *drop_ids)
            self._redis.xdel(self._name, *drop_ids)
            for drop_id, drop_message in drop_messages:
                tile = decode_message(drop_message[b'message'])
                self._redis.xadd(name=self._errors_name, fields=dict(tilecoord=str(tile.tilecoord)),
                                 maxlen=self._max_errors_nb)
            stats.increment_counter(['redis', self._name_str, 'dropped'], len(to_drop))

        if to_steal:
            messages = self._redis.xclaim(name=self._name, groupname=STREAM_GROUP, consumername=CONSUMER_NAME,
                                          min_idle_time=self._pending_timeout_ms, message_ids=to_steal)
            stats.increment_counter(['redis', self._name_str, 'stolen'], len(to_steal))
            return [[self._name, messages]]
        else:
            # Empty means there are pending jobs, but they are not old enough to be stolen
            return []

    def get_status(self):
        """
        Returns a map of stats
        """
        nb_messages = self._redis.xlen(self._name)
        pending = self._redis.xpending(self._name, STREAM_GROUP)
        tiles_in_error = self._get_errors()

        return {
            "Approximate number of tiles to generate": nb_messages,
            "Approximate number of generating tiles": pending['pending'],
            "Tiles in error": ', '.join(tiles_in_error)
        }

    def _get_errors(self):
        now, now_us = self._redis.time()
        old_timestamp = (now - self._max_errors_age) * 1000 + now_us / 1000

        errors = self._redis.xrange(name=self._errors_name)
        tiles_in_error = set()
        old_errors = []
        for error_id, error_message in errors:
            timestamp = int(error_id.decode().split('-')[0])
            if timestamp <= old_timestamp:
                old_errors.append(error_id)
            else:
                tiles_in_error.add(error_message[b'tilecoord'].decode())
        if old_errors:
            logger.info("Deleting %d old errors", len(old_errors))
            self._redis.xdel(self._errors_name, *old_errors)
        return tiles_in_error
