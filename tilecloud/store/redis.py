from __future__ import absolute_import
import logging
import os
import redis
import socket

from tilecloud import TileStore
from tilecloud.store.queue import encode_message, decode_message

STREAM_GROUP = 'tilecloud'
CONSUMER_NAME = socket.gethostname() + '-' + str(os.getpid())
PENDING_TIMEOUT_MS = 5 * 60 * 1000

logger = logging.getLogger(__name__)


class RedisTileStore(TileStore):
    """
    Redis queue.
    """
    def __init__(self, url, name='tilecloud', stop_if_empty=True, timeout=5, **kwargs):
        super(RedisTileStore, self).__init__(**kwargs)
        self._redis = redis.Redis.from_url(url)
        self._stop_if_empty = stop_if_empty
        self._timeout = timeout
        if not name.startswith('queue_'):
            name = 'queue_' + name
        self._name = name.encode('utf-8')
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
        while True:
            queues = self._redis.xreadgroup(groupname=STREAM_GROUP, consumername=CONSUMER_NAME,
                                            streams={self._name: '>'}, count=1, block=round(self._timeout * 1000))

            if not queues:
                queues = self._claim_olds()
                if queues is None and self._stop_if_empty:
                    break
            if queues:
                for redis_message in queues:
                    queue_name, queue_messages = redis_message
                    assert queue_name == self._name
                    for message in queue_messages:
                        id_, body = message
                        try:
                            tile = decode_message(body[b'message'], from_redis=True)
                            yield tile
                            self._redis.xack(self._name, STREAM_GROUP, id_)
                            self._redis.xdel(self._name, id_)
                        except Exception:
                            logger.warning('Failed decoding the Redis message', exc_info=True)

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
        assert tile.from_redis is True
        return tile

    def delete_all(self):
        """
        Used only by tests
        """
        self._redis.xtrim(name=self._name, maxlen=0)
        # xtrim doesn't empty the group claims. So we have to delete and re-create groups
        self._redis.xgroup_destroy(name=self._name, groupname=STREAM_GROUP)
        self._redis.xgroup_create(name=self._name, groupname=STREAM_GROUP, id='0-0', mkstream=True)

    def _claim_olds(self):
        pendings = self._redis.xpending_range(name=self._name, groupname=STREAM_GROUP, min='-', max='+', count=10)
        if not pendings:
            return None
        to_steal = []
        for pending in pendings:
            if int(pending['time_since_delivered']) >= PENDING_TIMEOUT_MS:
                id_ = pending['message_id']
                logger.info('A message has been pending for too long. Stealing it: %s', id_)
                to_steal.append(id_)
        if to_steal:
            messages = self._redis.xclaim(name=self._name, groupname=STREAM_GROUP, consumername=CONSUMER_NAME,
                                          min_idle_time=PENDING_TIMEOUT_MS, message_ids=to_steal)
            return [[self._name, messages]]
        else:
            return []
