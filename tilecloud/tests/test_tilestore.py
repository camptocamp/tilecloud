import sqlite3
import unittest

from tilecloud import BoundingPyramid, Bounds, Tile, TileCoord, TileStore, consume
from tilecloud.store.dict import DictTileStore
from tilecloud.store.mbtiles import MBTilesTileStore
from tilecloud.store.null import NullTileStore


class TestTileStore(unittest.TestCase):
    def test_empty(self) -> None:
        ts = TileStore()
        self.assertEqual(ts.bounding_pyramid, None)
        self.assertEqual(ts.content_type, None)
        self.assertEqual(len(ts), 0)
        self.assertRaises(NotImplementedError, next, ts.delete((Tile(TileCoord(0, 0, 0)),)))
        self.assertRaises(NotImplementedError, ts.delete_one, None)
        self.assertEqual(ts.get_cheap_bounding_pyramid(), None)
        self.assertRaises(NotImplementedError, next, ts.get((Tile(TileCoord(0, 0, 0)),)))
        self.assertEqual(list(ts.get_all()), [])
        self.assertRaises(NotImplementedError, ts.get_one, None)
        self.assertEqual(list(ts.list()), [])
        self.assertRaises(NotImplementedError, next, ts.put((Tile(TileCoord(0, 0, 0)),)))
        self.assertRaises(NotImplementedError, ts.put_one, None)
        self.assertFalse(None in ts)
        self.assertEqual(ts.get_bounding_pyramid(), BoundingPyramid())

    def test_init_kwargs(self) -> None:
        ts = TileStore(kwarg=None)
        self.assertEqual(ts.kwarg, None)

    def test_init_boundingpyramid(self) -> None:
        ts = TileStore(bounding_pyramid=BoundingPyramid.from_string("1/0/0:1/1"))
        self.assertTrue(Tile(TileCoord(1, 0, 0)) in ts)
        tiles = list(ts.list())
        self.assertEqual(len(tiles), 1)
        self.assertEqual(tiles[0].tilecoord, TileCoord(1, 0, 0))

    def test_load_null(self) -> None:
        self.assertTrue(isinstance(TileStore.load("null://"), NullTileStore))

    def test_load_http(self) -> None:
        from tilecloud.store.url import URLTileStore

        self.assertTrue(isinstance(TileStore.load("http://"), URLTileStore))

    def test_load_https(self) -> None:
        from tilecloud.store.url import URLTileStore

        self.assertTrue(isinstance(TileStore.load("https://"), URLTileStore))

    def test_load_s3(self) -> None:
        from tilecloud.store.s3 import S3TileStore

        self.assertTrue(isinstance(TileStore.load("s3://bucket/template"), S3TileStore))


class TestDictTileStore(unittest.TestCase):
    def test_empty(self) -> None:
        tilestore = DictTileStore()
        self.assertEqual(len(tilestore), 0)
        self.assertEqual(list(tilestore.list()), [])

    def test_one(self) -> None:
        tilestore = DictTileStore()
        self.assertEqual(len(tilestore), 0)
        tilestream = [Tile(TileCoord(1, 0, 0), data="data"), None, Tile(TileCoord(1, 0, 1), error=True)]
        tilestream = tilestore.put(tilestream)
        tiles = list(tilestream)
        self.assertEqual(len(tiles), 2)
        self.assertEqual(tiles[0].tilecoord, TileCoord(1, 0, 0))
        self.assertEqual(tiles[0].data, "data")
        self.assertEqual(tiles[1].tilecoord, TileCoord(1, 0, 1))
        self.assertEqual(tiles[1].error, True)
        self.assertTrue(Tile(TileCoord(1, 0, 0)) in tilestore)
        self.assertTrue(Tile(TileCoord(1, 0, 1)) in tilestore)
        tilestream = [Tile(TileCoord(1, 0, 0)), Tile(TileCoord(1, 0, 1))]
        tilestream = tilestore.get(tilestream)
        consume(tilestream, None)
        tiles = list(tilestore.get_all())
        self.assertEqual(len(tiles), 2)
        self.assertEqual(tiles[0].tilecoord, TileCoord(1, 0, 0))
        self.assertEqual(tiles[0].data, "data")
        self.assertEqual(tiles[1].tilecoord, TileCoord(1, 0, 1))
        self.assertEqual(tiles[1].error, True)
        tilestream = [Tile(TileCoord(1, 0, 0))]
        tilestream = tilestore.delete(tilestream)
        consume(tilestream, None)
        tiles = list(tilestore.get_all())
        self.assertEqual(len(tiles), 1)
        self.assertFalse(Tile(TileCoord(1, 0, 0)) in tilestore)
        self.assertTrue(Tile(TileCoord(1, 0, 1)) in tilestore)

    def test_get_one(self) -> None:
        tilestore = DictTileStore()
        self.assertEqual(tilestore.get_one(Tile(TileCoord(0, 0, 0))), None)


class TestMBTilesTileStore(unittest.TestCase):
    def test_one(self) -> None:
        tilestore = MBTilesTileStore(sqlite3.connect(":memory:"), content_type="image/png")
        self.assertEqual(len(tilestore), 0)
        tilestream = [Tile(TileCoord(1, 0, 0), data=b"data"), None, Tile(TileCoord(1, 0, 1), error=True)]
        tilestream = tilestore.put(tilestream)
        tiles = list(tilestream)
        self.assertEqual(len(tilestore), 2)
        self.assertEqual(len(tiles), 2)
        self.assertEqual(tiles[0].tilecoord, TileCoord(1, 0, 0))
        self.assertEqual(tiles[0].data, b"data")
        self.assertEqual(tiles[1].tilecoord, TileCoord(1, 0, 1))
        self.assertEqual(tiles[1].error, True)
        self.assertTrue(Tile(TileCoord(1, 0, 0)) in tilestore)
        self.assertTrue(Tile(TileCoord(1, 0, 1)) in tilestore)
        tilestream = [Tile(TileCoord(1, 0, 0)), Tile(TileCoord(1, 0, 1))]
        tilestream = tilestore.get(tilestream)
        consume(tilestream, None)
        self.assertEqual(
            tilestore.get_cheap_bounding_pyramid(), BoundingPyramid({1: (Bounds(0, 1), Bounds(0, 2))})
        )
        self.assertEqual(len(tilestore), 2)
        tiles = list(tilestore.list())
        self.assertEqual(len(tiles), 2)
        tiles = sorted(tilestore.get_all())
        self.assertEqual(len(tiles), 2)
        self.assertEqual(tiles[0].tilecoord, TileCoord(1, 0, 0))
        self.assertEqual(bytes(tiles[0].data), b"data")
        self.assertEqual(tiles[1].tilecoord, TileCoord(1, 0, 1))
        self.assertEqual(tiles[1].data, None)
        tilestream = [Tile(TileCoord(1, 0, 0))]
        tilestream = tilestore.delete(tilestream)
        consume(tilestream, None)
        self.assertEqual(len(tilestore), 1)
        tiles = list(tilestore.get_all())
        self.assertEqual(len(tiles), 1)
        self.assertFalse(Tile(TileCoord(1, 0, 0)) in tilestore)
        self.assertTrue(Tile(TileCoord(1, 0, 1)) in tilestore)

    def test_metadata(self) -> None:
        tilestore = MBTilesTileStore(sqlite3.connect(":memory:"))
        tilestore.put_one(Tile(TileCoord(1, 0, 0)))
        tilestore.put_one(Tile(TileCoord(2, 0, 0)))
        tilestore.set_metadata_zooms()
        self.assertEqual(int(tilestore.metadata["minzoom"]), 1)
        self.assertEqual(int(tilestore.metadata["maxzoom"]), 2)
        self.assertEqual(sorted(tilestore.metadata.itervalues()), ["1", "2"])
        self.assertEqual(sorted(tilestore.metadata.keys()), ["maxzoom", "minzoom"])

    def test_content_type(self) -> None:
        connection = sqlite3.connect(":memory:")
        tilestore1 = MBTilesTileStore(connection)
        tilestore1.metadata["format"] = "png"
        tilestore2 = MBTilesTileStore(connection)
        self.assertEqual(tilestore2.content_type, "image/png")

    def test_empty(self) -> None:
        connection = sqlite3.connect(":memory:")
        tilestore = MBTilesTileStore(connection)
        self.assertEqual(len(tilestore), 0)
        self.assertEqual(tilestore.get_one(Tile(TileCoord(0, 0, 0))), Tile(TileCoord(0, 0, 0)))


class TestNullTileStore(unittest.TestCase):
    def test(self) -> None:
        tilestore = NullTileStore()
        tile = Tile(TileCoord(0, 0, 0))
        self.assertFalse(tile in tilestore)
        self.assertEqual(list(tilestore.delete([tile])), [tile])
        self.assertEqual(list(tilestore.list()), [])
        self.assertEqual(list(tilestore.get([tile])), [tile])
        self.assertEqual(list(tilestore.put([tile])), [tile])
