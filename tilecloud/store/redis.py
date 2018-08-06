from __future__ import absolute_import
import logging
import redis

from tilecloud import TileStore
from tilecloud.store import sqs
from tilecloud.store.queue import encode_message, decode_message


logger = logging.getLogger(__name__)


class RedisTileStore(TileStore):
    """
    Very crude implementation of a Redis queue.

    Limitations:

    - if a slave crashes while working on a tile, the tile is lost (won't be taken over by another slave)
    """
    def __init__(self, url, name='tilecloud', stop_if_empty=True, timeout=5, **kwargs):
        super(RedisTileStore, self).__init__(**kwargs)
        self._redis = redis.StrictRedis.from_url(url)
        self._name = name
        self._stop_if_empty = stop_if_empty
        self._timeout = timeout
        if not self._name.startswith('queue_'):
            self._name = 'queue_' + self._name

    def __contains__(self, tile):
        return False

    @staticmethod
    def get_one(tile):
        return tile

    def list(self):
        while True:
            redis_message = self._redis.blpop(self._name, timeout=self._timeout)

            if not redis_message:
                if self._stop_if_empty:
                    break
            else:
                try:
                    tile = decode_message(redis_message[1], from_redis=True)
                    yield tile
                except Exception:
                    logger.warning('Failed decoding the Redis message', exc_info=True)

    def put_one(self, tile):
        try:
            self._redis.rpush(self._name, encode_message(tile))
        except Exception as e:
            logger.warning('Failed sending SQS message', exc_info=True)
            tile.error = e

    def put(self, tiles):
        buffered_tiles = []
        try:
            for tile in tiles:
                buffered_tiles.append(tile)
                if len(buffered_tiles) >= sqs.BATCH_SIZE:
                    self._send_buffer(buffered_tiles)
                    buffered_tiles = []
                yield tile
        finally:
            if len(buffered_tiles) > 0:
                self._send_buffer(buffered_tiles)

    @staticmethod
    def delete_one(tile):
        # Once consumed from redis, we don't have to delete the tile from the queue.
        assert hasattr(tile, 'from_redis')
        assert tile.from_redis is True
        return tile

    def delete_all(self):
        self._redis.delete(self._name)

    def _send_buffer(self, tiles):
        try:
            messages = [encode_message(tile) for tile in tiles]
            self._redis.rpush(self._name, *messages)
        except Exception as e:
            logger.warning('Failed sending Redis messages', exc_info=True)
            for tile in tiles:
                tile.error = e
