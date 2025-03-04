import sqlite3
import unittest

from tilecloud import BoundingPyramid, Bounds, Tile, TileCoord, TileStore, consume
from tilecloud.store.dict import DictTileStore
from tilecloud.store.mbtiles import MBTilesTileStore
from tilecloud.store.null import NullTileStore


class TestTileStore(unittest.TestCase):
    def test_empty(self) -> None:
        ts = TileStore()
        assert ts.bounding_pyramid is None
        assert ts.content_type is None
        assert len(ts) == 0
        self.assertRaises(NotImplementedError, next, ts.delete((Tile(TileCoord(0, 0, 0)),)))
        self.assertRaises(NotImplementedError, ts.delete_one, None)
        assert ts.get_cheap_bounding_pyramid() is None
        self.assertRaises(NotImplementedError, next, ts.get((Tile(TileCoord(0, 0, 0)),)))
        assert list(ts.get_all()) == []
        self.assertRaises(NotImplementedError, ts.get_one, None)
        assert list(ts.list()) == []
        self.assertRaises(NotImplementedError, next, ts.put((Tile(TileCoord(0, 0, 0)),)))
        self.assertRaises(NotImplementedError, ts.put_one, None)
        assert None not in ts
        assert ts.get_bounding_pyramid() == BoundingPyramid()

    def test_init_kwargs(self) -> None:
        ts = TileStore(kwarg=None)
        assert ts.kwarg is None

    def test_init_boundingpyramid(self) -> None:
        ts = TileStore(bounding_pyramid=BoundingPyramid.from_string("1/0/0:1/1"))
        assert Tile(TileCoord(1, 0, 0)) in ts
        tiles = list(ts.list())
        assert len(tiles) == 1
        assert tiles[0].tilecoord == TileCoord(1, 0, 0)

    def test_load_null(self) -> None:
        assert isinstance(TileStore.load("null://"), NullTileStore)

    def test_load_http(self) -> None:
        from tilecloud.store.url import URLTileStore

        assert isinstance(TileStore.load("http://"), URLTileStore)

    def test_load_https(self) -> None:
        from tilecloud.store.url import URLTileStore

        assert isinstance(TileStore.load("https://"), URLTileStore)

    def test_load_s3(self) -> None:
        from tilecloud.store.s3 import S3TileStore

        assert isinstance(TileStore.load("s3://bucket/template"), S3TileStore)


class TestDictTileStore(unittest.TestCase):
    def test_empty(self) -> None:
        tilestore = DictTileStore()
        assert len(tilestore) == 0
        assert list(tilestore.list()) == []

    def test_one(self) -> None:
        tilestore = DictTileStore()
        assert len(tilestore) == 0
        tilestream = [Tile(TileCoord(1, 0, 0), data="data"), None, Tile(TileCoord(1, 0, 1), error=True)]
        tilestream = tilestore.put(tilestream)
        tiles = list(tilestream)
        assert len(tiles) == 2
        assert tiles[0].tilecoord == TileCoord(1, 0, 0)
        assert tiles[0].data == "data"
        assert tiles[1].tilecoord == TileCoord(1, 0, 1)
        assert tiles[1].error is True
        assert Tile(TileCoord(1, 0, 0)) in tilestore
        assert Tile(TileCoord(1, 0, 1)) in tilestore
        tilestream = [Tile(TileCoord(1, 0, 0)), Tile(TileCoord(1, 0, 1))]
        tilestream = tilestore.get(tilestream)
        consume(tilestream, None)
        tiles = list(tilestore.get_all())
        assert len(tiles) == 2
        assert tiles[0].tilecoord == TileCoord(1, 0, 0)
        assert tiles[0].data == "data"
        assert tiles[1].tilecoord == TileCoord(1, 0, 1)
        assert tiles[1].error is True
        tilestream = [Tile(TileCoord(1, 0, 0))]
        tilestream = tilestore.delete(tilestream)
        consume(tilestream, None)
        tiles = list(tilestore.get_all())
        assert len(tiles) == 1
        assert Tile(TileCoord(1, 0, 0)) not in tilestore
        assert Tile(TileCoord(1, 0, 1)) in tilestore

    def test_get_one(self) -> None:
        tilestore = DictTileStore()
        assert tilestore.get_one(Tile(TileCoord(0, 0, 0))) is None


class TestMBTilesTileStore(unittest.TestCase):
    def test_one(self) -> None:
        tilestore = MBTilesTileStore(sqlite3.connect(":memory:"), content_type="image/png")
        assert len(tilestore) == 0
        tilestream = [Tile(TileCoord(1, 0, 0), data=b"data"), None, Tile(TileCoord(1, 0, 1), error=True)]
        tilestream = tilestore.put(tilestream)
        tiles = list(tilestream)
        assert len(tilestore) == 2
        assert len(tiles) == 2
        assert tiles[0].tilecoord == TileCoord(1, 0, 0)
        assert tiles[0].data == b"data"
        assert tiles[1].tilecoord == TileCoord(1, 0, 1)
        assert tiles[1].error is True
        assert Tile(TileCoord(1, 0, 0)) in tilestore
        assert Tile(TileCoord(1, 0, 1)) in tilestore
        tilestream = [Tile(TileCoord(1, 0, 0)), Tile(TileCoord(1, 0, 1))]
        tilestream = tilestore.get(tilestream)
        consume(tilestream, None)
        assert tilestore.get_cheap_bounding_pyramid() == BoundingPyramid({1: (Bounds(0, 1), Bounds(0, 2))})
        assert len(tilestore) == 2
        tiles = list(tilestore.list())
        assert len(tiles) == 2
        tiles = sorted(tilestore.get_all())
        assert len(tiles) == 2
        assert tiles[0].tilecoord == TileCoord(1, 0, 0)
        assert bytes(tiles[0].data) == b"data"
        assert tiles[1].tilecoord == TileCoord(1, 0, 1)
        assert tiles[1].data is None
        tilestream = [Tile(TileCoord(1, 0, 0))]
        tilestream = tilestore.delete(tilestream)
        consume(tilestream, None)
        assert len(tilestore) == 1
        tiles = list(tilestore.get_all())
        assert len(tiles) == 1
        assert Tile(TileCoord(1, 0, 0)) not in tilestore
        assert Tile(TileCoord(1, 0, 1)) in tilestore

    def test_metadata(self) -> None:
        tilestore = MBTilesTileStore(sqlite3.connect(":memory:"))
        tilestore.put_one(Tile(TileCoord(1, 0, 0)))
        tilestore.put_one(Tile(TileCoord(2, 0, 0)))
        tilestore.set_metadata_zooms()
        assert int(tilestore.metadata["minzoom"]) == 1
        assert int(tilestore.metadata["maxzoom"]) == 2
        assert sorted(tilestore.metadata.itervalues()) == ["1", "2"]
        assert sorted(tilestore.metadata.keys()) == ["maxzoom", "minzoom"]

    def test_content_type(self) -> None:
        connection = sqlite3.connect(":memory:")
        tilestore1 = MBTilesTileStore(connection)
        tilestore1.metadata["format"] = "png"
        tilestore2 = MBTilesTileStore(connection)
        assert tilestore2.content_type == "image/png"

    def test_empty(self) -> None:
        connection = sqlite3.connect(":memory:")
        tilestore = MBTilesTileStore(connection)
        assert len(tilestore) == 0
        assert tilestore.get_one(Tile(TileCoord(0, 0, 0))) == Tile(TileCoord(0, 0, 0))


class TestNullTileStore(unittest.TestCase):
    def test(self) -> None:
        tilestore = NullTileStore()
        tile = Tile(TileCoord(0, 0, 0))
        assert tile not in tilestore
        assert list(tilestore.delete([tile])) == [tile]
        assert list(tilestore.list()) == []
        assert list(tilestore.get([tile])) == [tile]
        assert list(tilestore.put([tile])) == [tile]
