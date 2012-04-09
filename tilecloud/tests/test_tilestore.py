import unittest

from tilecloud import BoundingPyramid, Tile, TileCoord, TileStore, consume
from tilecloud.store.dict import DictTileStore
from tilecloud.store.null import NullTileStore


class TestTileStore(unittest.TestCase):

    def test_empty(self):
        ts = TileStore()
        self.assertEqual(ts.bounding_pyramid, None)
        self.assertEqual(ts.content_type, None)
        self.assertEqual(ts.count(), 0)
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

    def test_init_kwargs(self):
        ts = TileStore(kwarg=None)
        self.assertEqual(ts.kwarg, None)

    def test_init_boundingpyramid(self):
        ts = TileStore(bounding_pyramid=BoundingPyramid.from_string('1/0/0:1/1'))
        self.assertTrue(Tile(TileCoord(1, 0, 0)) in ts)
        tiles = list(ts.list())
        self.assertEqual(len(tiles), 1)
        self.assertEqual(tiles[0].tilecoord, TileCoord(1, 0, 0))

    def test_load_null(self):
        self.assertTrue(isinstance(TileStore.load('null://'), NullTileStore))

    def test_load_http(self):
        from tilecloud.store.url import URLTileStore
        self.assertTrue(isinstance(TileStore.load('http://'), URLTileStore))

    def test_load_https(self):
        from tilecloud.store.url import URLTileStore
        self.assertTrue(isinstance(TileStore.load('https://'), URLTileStore))

    def test_load_s3(self):
        from tilecloud.store.s3 import S3TileStore
        self.assertTrue(isinstance(TileStore.load('s3://bucket/template'), S3TileStore))


class TestDictTileStore(unittest.TestCase):

    def test_empty(self):
        tile_store = DictTileStore()
        self.assertEqual(tile_store.count(), 0)
        self.assertEqual(list(tile_store.list()), [])

    def test_one(self):
        tile_store = DictTileStore()
        self.assertEqual(tile_store.count(), 0)
        tilestream = [Tile(TileCoord(1, 0, 0), data='data'), None, Tile(TileCoord(1, 0, 1), error=True)]
        tilestream = tile_store.put(tilestream)
        tiles = list(tilestream)
        self.assertEqual(len(tiles), 1)
        self.assertEqual(tiles[0].tilecoord, TileCoord(1, 0, 0))
        self.assertEqual(tiles[0].data, 'data')
        self.assertTrue(Tile(TileCoord(1, 0, 0)) in tile_store)
        tilestream = [Tile(TileCoord(1, 0, 0)), Tile(TileCoord(1, 0, 1))]
        tilestream = tile_store.get(tilestream)
        consume(tilestream, None)
        tiles = list(tile_store.get_all())
        self.assertEqual(len(tiles), 1)
        self.assertEqual(tiles[0].tilecoord, TileCoord(1, 0, 0))
        self.assertEqual(tiles[0].data, 'data')
        tilestream = [Tile(TileCoord(1, 0, 0))]
        tilestream = tile_store.delete(tilestream)
        consume(tilestream, None)
        tiles = list(tile_store.get_all())
        self.assertEqual(len(tiles), 0)
        self.assertFalse(Tile(TileCoord(1, 0, 0)) in tile_store)


class TestNullTileStore(unittest.TestCase):

    def test(self):
        tile_store = NullTileStore()
        tile = Tile(TileCoord(0, 0, 0))
        self.assertFalse(tile in tile_store)
        self.assertEqual(list(tile_store.delete([tile])), [tile])
        self.assertEqual(list(tile_store.list()), [])
        self.assertEqual(list(tile_store.get([tile])), [tile])
        self.assertEqual(list(tile_store.put([tile])), [tile])
