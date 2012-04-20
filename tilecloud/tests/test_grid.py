import unittest

from tilecloud import Grid, Bounds, TileCoord, MetaTileCoord


class TestGrid(unittest.TestCase):
    def setUp(self):
        self.tms = Grid(
            resolutions=(40, 20, 10, 5),
            max_extent=(420000, 30000, 900000, 350000),
            tile_size=100,
            top=-1)
        self.wmts = Grid(
            resolutions=(40, 20, 10, 5),
            max_extent=(420000, 30000, 900000, 350000),
            tile_size=100,
            top=1)

    def test_tms(self):
        self.assertEqual(self.tms.bounds(MetaTileCoord(2, 1, 4, 6)), (
            Bounds(428000, 432000),
            Bounds(42000, 46000)))
        self.assertEqual(self.tms.bounds(TileCoord(1, 4, 6)), (
            Bounds(428000, 430000),
            Bounds(42000, 44000)))
        self.assertEqual(self.tms.bounds(TileCoord(1, 5, 7)), (
            Bounds(430000, 432000),
            Bounds(44000, 46000)))
        # with buffer
        self.assertEqual(self.tms.bounds(TileCoord(1, 4, 6), 5), (
            Bounds(427900, 430100),
            Bounds(41900, 44100)))
        # backward
        self.assertEqual(self.tms.tilecoord((1, 429000, 43000)),
            TileCoord(1, 4, 6))
        self.assertEqual(self.tms.tilecoord((1, 431000, 45000)),
            TileCoord(1, 5, 7))
        self.assertEqual(self.tms.tilecoord((1, 429000, 43000), 2),
            TileCoord(1, 4, 6))
        self.assertEqual(self.tms.tilecoord((1, 431000, 45000), 2),
            TileCoord(1, 4, 6))

    def test_wmts(self):
        self.assertEqual(self.wmts.bounds(MetaTileCoord(2, 1, 4, 6)), (
            Bounds(428000, 432000),
            Bounds(334000, 338000)))
        self.assertEqual(self.wmts.bounds(TileCoord(1, 4, 6)), (
            Bounds(428000, 430000),
            Bounds(336000, 338000)))
        self.assertEqual(self.wmts.bounds(TileCoord(1, 5, 7)), (
            Bounds(430000, 432000),
            Bounds(334000, 336000)))
        # with buffer
        self.assertEqual(self.wmts.bounds(TileCoord(1, 4, 6), 5), (
            Bounds(427900, 430100),
            Bounds(335900, 338100)))
        # backward
        self.assertEqual(self.wmts.tilecoord((1, 429000, 337000)),
            TileCoord(1, 4, 6))
        self.assertEqual(self.wmts.tilecoord((1, 431000, 335000)),
            TileCoord(1, 5, 7))
        self.assertEqual(self.wmts.tilecoord((1, 429000, 337000), 2),
            TileCoord(1, 4, 6))
        self.assertEqual(self.wmts.tilecoord((1, 431000, 335000), 2),
            TileCoord(1, 4, 6))
