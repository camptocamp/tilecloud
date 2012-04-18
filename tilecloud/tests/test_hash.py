import unittest

from tilecloud import Tile, TileCoord, TileStore
from tilecloud.filter.hash import HashDropper


class TestHash(unittest.TestCase):

    def test_hash(self):
        tile = Tile(TileCoord(0, 0, 0), data="foobar")
        self.assertFalse(HashDropper(6, 3433925302934160649)(tile))
        # other size
        self.assertTrue(HashDropper(5, 3433925302934160649)(tile))
        # other hash
        self.assertTrue(HashDropper(6, 3433925302934160648)(tile))

    def test_delete(self):
        class TestStore(TileStore):
            deleted = None
            def delete_one(self, tile):
                self.deleted = tile
        test_store = TestStore()
        tile = Tile(TileCoord(0, 0, 0), data="foobar")

        # other size
        self.assertTrue(HashDropper(5, 3433925302934160649, store=test_store)(tile))
        self.assertIsNone(test_store.deleted)

        # other hash
        self.assertTrue(HashDropper(6, 3433925302934160648, store=test_store)(tile))
        self.assertIsNone(test_store.deleted)

        self.assertFalse(HashDropper(6, 3433925302934160649, store=test_store)(tile))
        self.assertIsNotNone(test_store.deleted)
        self.assertEquals(test_store.deleted, tile)
