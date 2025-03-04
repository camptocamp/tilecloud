import unittest

from tilecloud import Tile, TileCoord


class TestTile(unittest.TestCase):
    def test_empty(self) -> None:
        tile = Tile(TileCoord(0, 0, 0))
        assert tile.content_type == None
        assert tile.content_encoding == None
        assert tile.data == None
        assert tile.error == None

    def test_init_kwargs(self) -> None:
        tile = Tile(TileCoord(0, 0, 0), kwarg=None)
        assert tile.kwarg == None
