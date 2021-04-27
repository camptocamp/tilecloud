import unittest

from tilecloud import Tile, TileCoord


class TestTile(unittest.TestCase):
    def test_empty(self) -> None:
        tile = Tile(TileCoord(0, 0, 0))
        self.assertEqual(tile.content_type, None)
        self.assertEqual(tile.content_encoding, None)
        self.assertEqual(tile.data, None)
        self.assertEqual(tile.error, None)

    def test_init_kwargs(self) -> None:
        tile = Tile(TileCoord(0, 0, 0), kwarg=None)
        self.assertEqual(tile.kwarg, None)
