import os
import pytest

from tilecloud import Tile, TileCoord
from tilecloud.store.redis import RedisTileStore

url = os.environ.get('REDIS_URL')

skip_no_redis = pytest.mark.skipif(url is None, reason="skipped because of missing REDIS_URL")


@pytest.fixture()
def store():
    store = RedisTileStore(url, name="test", stop_if_empty=True, timeout=1)
    store.delete_all()
    yield store


@skip_no_redis
def test_list(store):
    for y in range(10):
        store.put_one(Tile(TileCoord(0, 0, y)))

    count = 0
    for y, tile in enumerate(store.list()):
        print(repr(tile))
        assert y == tile.tilecoord.y
        count += 1
    assert 10 == count


@skip_no_redis
def test_put(store):
    tiles = [Tile(TileCoord(0, 0, y)) for y in range(20)]

    count = 0
    for y, tile in enumerate(store.put(tiles)):
        assert y == tile.tilecoord.y
        count += 1
    assert 20 == count

    count = 0
    for y, tile in enumerate(store.list()):
        assert y == tile.tilecoord.y
        count += 1
    assert 20 == count
