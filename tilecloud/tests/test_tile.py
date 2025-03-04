import unittest

from tilecloud import Tile, TileCoord


class TestTile(unittest.TestCase):
    def test_empty(self) -> None:
        tile = Tile(TileCoord(0, 0, 0))
        assert tile.content_type is None
        assert tile.content_encoding is None
        assert tile.data is None
        assert tile.error is None

    def test_init_kwargs(self) -> None:
        tile = Tile(TileCoord(0, 0, 0), kwarg=None)
        assert tile.kwarg is None
