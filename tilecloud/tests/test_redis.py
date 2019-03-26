import os
import pytest

from tilecloud import Tile, TileCoord
from tilecloud.store.redis import RedisTileStore

url = os.environ.get('REDIS_URL')

skip_no_redis = pytest.mark.skipif(url is None, reason="skipped because of missing REDIS_URL")


@pytest.fixture()
def store():
    store = RedisTileStore(url, name="test", stop_if_empty=True, timeout=0.1, pending_timeout=0.5, max_retries=2)
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
        store.delete_one(tile)
    assert 10 == count


class SlaveException(RuntimeError):
    pass


@skip_no_redis
def test_recovery_from_failing_slave(store):
    for y in range(10):
        store.put_one(Tile(TileCoord(0, 0, y)))

    with pytest.raises(SlaveException):
        for _ in store.list():
            raise SlaveException  # fail the processing of the first tile

    count = 0
    for y, tile in enumerate(store.list()):
        print(repr(tile))
        # weird computation for the expected value because the first tile is read last since its processing failed
        assert (y + 1) % 10 == tile.tilecoord.y
        count += 1
        store.delete_one(tile)
    assert 10 == count


@skip_no_redis
def test_dropping_too_many_retries(store):
    for y in range(10):
        store.put_one(Tile(TileCoord(0, 0, y)))

    count = 0
    # max_retires=2 => 2 iterations to have the error two times and a third one to drop the message
    for _ in range(3):
        try:
            for tile in store.list():
                if tile.tilecoord.y == 0:  # this tile always fails and will be dropped after two tries
                    raise SlaveException
                count += 1
                store.delete_one(tile)
        except SlaveException:
            pass
    assert 9 == count


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
        store.delete_one(tile)
    assert 20 == count
