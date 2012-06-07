from itertools import islice
import unittest

from tilecloud import TileCoord, TileGrid
from tilecloud.grid.free import FreeTileGrid
from tilecloud.grid.quad import QuadTileGrid


class TestTileGrid(unittest.TestCase):

    def setUp(self):
        self.tg = TileGrid()

    def test_tilegrid(self):
        self.assertRaises(NotImplementedError, self.tg.extent, None)
        self.assertRaises(NotImplementedError, self.tg.fill_down, None, None)
        self.assertRaises(NotImplementedError, self.tg.fill_up, None, None)
        self.assertRaises(NotImplementedError, self.tg.children, None)
        self.assertRaises(NotImplementedError, self.tg.parent, None)
        self.assertRaises(NotImplementedError, self.tg.roots)
        self.assertRaises(NotImplementedError, self.tg.tilecoord, None, None, None)
        self.assertRaises(NotImplementedError, self.tg.zs)


class TestFreeTileGrid(unittest.TestCase):

    def setUp(self):
        self.resolutions = (1000, 999, 500, 250, 125, 123, 111, 100, 50, 25, 10)
        self.ftg = FreeTileGrid(self.resolutions)

    def test_factors(self):
        for i, resolution in enumerate(self.resolutions):
            for child_z in self.ftg.child_zs[i]:
                self.assertEquals(self.resolutions[i] % self.resolutions[child_z], 0)

    def test_root_parents(self):
        for root_z in set(root.z for root in self.ftg.roots()):
            self.assertEquals(self.ftg.parent(TileCoord(root_z, 0, 0)), None)

    def test_root_zero(self):
        self.assertEquals(self.ftg.parent(TileCoord(0, 0, 0)), None)

    def test_zs(self):
        self.assertEquals(list(self.ftg.zs()), range(len(self.resolutions)))


class TestFreeTileGrid2(unittest.TestCase):

    def setUp(self):
        self.ftg = FreeTileGrid(resolutions=(40, 20, 10, 5), max_extent=(420000, 330000, 900000, 350000), tile_size=100)

    def test_extent(self):
        self.assertEqual(self.ftg.extent(TileCoord(1, 4, 6)), (428000, 336000, 430000, 338000))
        self.assertEqual(self.ftg.extent(TileCoord(1, 5, 7)), (430000, 334000, 432000, 336000))

    def test_extent_border(self):
        self.assertEqual(self.ftg.extent(TileCoord(1, 4, 6), 5), (427900, 335900, 430100, 338100))

    def test_extent_metatile(self):
        self.assertEqual(self.ftg.extent(TileCoord(1, 4, 6, 2)), (428000, 334000, 432000, 338000))

    def test_extent_metatile_border(self):
        self.assertEqual(self.ftg.extent(TileCoord(1, 4, 6, 2), 5), (427900, 333900, 432100, 338100))

    def test_tilecoord(self):
        self.assertEqual(self.ftg.tilecoord(1, 428000, 342000), TileCoord(1, 4, 6))
        self.assertEqual(self.ftg.tilecoord(1, 430000, 344000), TileCoord(1, 5, 7))
        self.assertEqual(self.ftg.tilecoord(1, 430000, 344000), TileCoord(1, 5, 7))
        self.assertEqual(self.ftg.tilecoord(1, 432000, 346000), TileCoord(1, 6, 8))

    def test_zs(self):
        self.assertEqual(list(self.ftg.zs()), [0, 1, 2, 3])


class TestFreeTileGridWithScale(unittest.TestCase):

    def setUp(self):
        self.ftg = FreeTileGrid(resolutions=(4000, 2000, 1000, 500), max_extent=(420000, 330000, 900000, 350000), tile_size=100, scale=100)

    def test_extent(self):
        self.assertEqual(self.ftg.extent(TileCoord(1, 4, 6)), (428000, 336000, 430000, 338000))
        self.assertEqual(self.ftg.extent(TileCoord(1, 5, 7)), (430000, 334000, 432000, 336000))

    def test_extent_border(self):
        self.assertEqual(self.ftg.extent(TileCoord(1, 4, 6), 5), (427900, 335900, 430100, 338100))

    def test_extent_metatile(self):
        self.assertEqual(self.ftg.extent(TileCoord(1, 4, 6, 2)), (428000, 334000, 432000, 338000))

    def test_extent_metatile_border(self):
        self.assertEqual(self.ftg.extent(TileCoord(1, 4, 6, 2), 5), (427900, 333900, 432100, 338100))

    def test_tilecoord(self):
        self.assertEqual(self.ftg.tilecoord(1, 428000, 342000), TileCoord(1, 4, 6))
        self.assertEqual(self.ftg.tilecoord(1, 430000, 344000), TileCoord(1, 5, 7))
        self.assertEqual(self.ftg.tilecoord(1, 430000, 344000), TileCoord(1, 5, 7))
        self.assertEqual(self.ftg.tilecoord(1, 432000, 346000), TileCoord(1, 6, 8))


class TestFreeTileGridFlipY(unittest.TestCase):

    def setUp(self):
        self.ftsn = FreeTileGrid(resolutions=(8, 4, 2, 1), tile_size=0.125)
        self.ftsf = FreeTileGrid(resolutions=(8, 4, 2, 1), tile_size=0.125, flip_y=True)

    def test_flip_y(self):
        self.assertEqual(self.ftsn.extent(TileCoord(2, 0, 0)), self.ftsf.extent(TileCoord(2, 0, 3)))
        self.assertEqual(self.ftsn.extent(TileCoord(2, 1, 1)), self.ftsf.extent(TileCoord(2, 1, 2)))
        self.assertEqual(self.ftsn.extent(TileCoord(2, 2, 2)), self.ftsf.extent(TileCoord(2, 2, 1)))
        self.assertEqual(self.ftsn.extent(TileCoord(2, 3, 3)), self.ftsf.extent(TileCoord(2, 3, 0)))


class TestFreeQuadTileGridEquivalence(unittest.TestCase):

    def setUp(self):
        self.ftg = FreeTileGrid([8, 4, 2, 1], tile_size=0.125)
        self.qtg = QuadTileGrid(max_zoom=3)

    def test_children(self):
        tc = TileCoord(2, 2, 3)
        self.assertEqual(sorted(self.ftg.children(tc)), sorted(self.qtg.children(tc)))

    def test_children_root(self):
        tc = TileCoord(0, 0, 0)
        self.assertEqual(sorted(self.ftg.children(tc)), sorted(self.qtg.children(tc)))

    def test_extent(self):
        for z in xrange(0, 4):
            for x in xrange(0, 1 << z):
                for y in xrange(0, 1 << z):
                    tilecoord = TileCoord(z, x, y)
                    self.assertEqual(self.ftg.extent(tilecoord), self.qtg.extent(tilecoord))

    def test_parent(self):
        tc = TileCoord(3, 3, 5)
        self.assertEqual(self.ftg.parent(tc), self.qtg.parent(tc))

    def test_roots(self):
        self.assertEqual(list(self.ftg.roots()), list(self.qtg.roots()))

    def test_zs(self):
        self.assertEqual(list(self.ftg.zs()), list(self.qtg.zs()))


class TestQuadTileGrid(unittest.TestCase):

    def setUp(self):
        self.qtg = QuadTileGrid(max_extent=(0.0, 1.0, 2.0, 3.0))

    def test_children(self):
        self.assertEqual(sorted(self.qtg.children(TileCoord(1, 2, 3))), [TileCoord(2, 4, 6), TileCoord(2, 4, 7), TileCoord(2, 5, 6), TileCoord(2, 5, 7)])

    def test_children_root(self):
        self.assertEqual(sorted(self.qtg.children(TileCoord(0, 0, 0))), [TileCoord(1, 0, 0), TileCoord(1, 0, 1), TileCoord(1, 1, 0), TileCoord(1, 1, 1)])

    def test_extent_z0(self):
        self.assertEqual(self.qtg.extent(TileCoord(0, 0, 0)), (0.0, 1.0, 2.0, 3.0))

    def test_extent_z1(self):
        self.assertEqual(self.qtg.extent(TileCoord(1, 0, 0)), (0.0, 2.0, 1.0, 3.0))
        self.assertEqual(self.qtg.extent(TileCoord(1, 0, 1)), (0.0, 1.0, 1.0, 2.0))
        self.assertEqual(self.qtg.extent(TileCoord(1, 1, 0)), (1.0, 2.0, 2.0, 3.0))
        self.assertEqual(self.qtg.extent(TileCoord(1, 1, 1)), (1.0, 1.0, 2.0, 2.0))

    def test_extent_z2(self):
        self.assertEqual(self.qtg.extent(TileCoord(2, 0, 0)), (0.0, 2.5, 0.5, 3.0))
        self.assertEqual(self.qtg.extent(TileCoord(2, 1, 1)), (0.5, 2.0, 1.0, 2.5))
        self.assertEqual(self.qtg.extent(TileCoord(2, 2, 2)), (1.0, 1.5, 1.5, 2.0))
        self.assertEqual(self.qtg.extent(TileCoord(2, 3, 3)), (1.5, 1.0, 2.0, 1.5))

    def test_parent(self):
        self.assertEqual(self.qtg.parent(TileCoord(5, 11, 21)), TileCoord(4, 5, 10))

    def test_parent_root(self):
        self.assertEqual(self.qtg.parent(TileCoord(0, 0, 0)), None)

    def test_roots(self):
        self.assertEqual(list(self.qtg.roots()), [TileCoord(0, 0, 0)])

    def test_tilecoord(self):
        for z in xrange(0, 4):
            for x in xrange(0, 1 << z):
                for y in xrange(0, 1 << z):
                    tilecoord = TileCoord(z, x, y)
                    minx, miny, maxx, maxy = self.qtg.extent(tilecoord)
                    self.assertEqual(self.qtg.tilecoord(z, minx, miny), tilecoord)

    def test_zs(self):
        self.assertEqual(list(islice(self.qtg.zs(), 50)), range(50))


class TestQuadTileGridFlipY(unittest.TestCase):

    def setUp(self):
        self.qtsn = QuadTileGrid()
        self.qtsf = QuadTileGrid(flip_y=True)

    def test_flip_y(self):
        self.assertEqual(self.qtsn.extent(TileCoord(2, 0, 0)), self.qtsf.extent(TileCoord(2, 0, 3)))
        self.assertEqual(self.qtsn.extent(TileCoord(2, 1, 1)), self.qtsf.extent(TileCoord(2, 1, 2)))
        self.assertEqual(self.qtsn.extent(TileCoord(2, 2, 2)), self.qtsf.extent(TileCoord(2, 2, 1)))
        self.assertEqual(self.qtsn.extent(TileCoord(2, 3, 3)), self.qtsf.extent(TileCoord(2, 3, 0)))
