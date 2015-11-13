from itertools import islice
import unittest
from six.moves import xrange

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
        self.assertEquals(list(self.ftg.zs()), [e for e in range(len(self.resolutions))])


class TestFreeTileGrid2(unittest.TestCase):

    def setUp(self):
        self.ftg = FreeTileGrid(resolutions=(750, 20, 10, 5), max_extent=(420000, 30000, 900000, 350000), tile_size=100)

    def test_extent(self):
        self.assertEqual(self.ftg.extent(TileCoord(0, 0, 0)), (420000, 275000, 495000, 350000))
        self.assertEqual(self.ftg.extent(TileCoord(1, 0, 0)), (420000, 348000, 422000, 350000))
        self.assertEqual(self.ftg.extent(TileCoord(2, 0, 0)), (420000, 349000, 421000, 350000))
        self.assertEqual(self.ftg.extent(TileCoord(3, 0, 0)), (420000, 349500, 420500, 350000))
        self.assertEqual(self.ftg.extent(TileCoord(1, 4, 6)), (428000, 336000, 430000, 338000))
        self.assertEqual(self.ftg.extent(TileCoord(1, 5, 7)), (430000, 334000, 432000, 336000))

    def test_extent_border(self):
        self.assertEqual(self.ftg.extent(TileCoord(1, 4, 6), 5), (427900, 335900, 430100, 338100))

    def test_extent_metatile(self):
        self.assertEqual(self.ftg.extent(TileCoord(1, 4, 6, 2)), (428000, 334000, 432000, 338000))

    def test_extent_metatile_border(self):
        self.assertEqual(self.ftg.extent(TileCoord(1, 4, 6, 2), 5), (427900, 333900, 432100, 338100))

    def test_tilecoord(self):
        self.assertEqual(self.ftg.tilecoord(1, 428000, 336000), TileCoord(1, 4, 7))
        self.assertEqual(self.ftg.tilecoord(1, 428000.1, 336000.1), TileCoord(1, 4, 6))
        self.assertEqual(self.ftg.tilecoord(1, 429999.9, 337999.9), TileCoord(1, 4, 6))
        self.assertEqual(self.ftg.tilecoord(1, 430000, 338000), TileCoord(1, 5, 6))
        self.assertEqual(self.ftg.tilecoord(1, 430000, 334000), TileCoord(1, 5, 8))
        self.assertEqual(self.ftg.tilecoord(1, 431000, 335000), TileCoord(1, 5, 7))
        self.assertEqual(self.ftg.tilecoord(1, 432000, 336000), TileCoord(1, 6, 7))
        self.assertEqual(self.ftg.tilecoord(1, 432000, 333000), TileCoord(1, 6, 8))

    def test_zs(self):
        self.assertEqual(list(self.ftg.zs()), [0, 1, 2, 3])


class TestFreeTileGridWithScale(unittest.TestCase):

    def setUp(self):
        self.ftg = FreeTileGrid(resolutions=(4000, 2000, 1000, 500), max_extent=(420000, 30000, 900000, 350000), tile_size=100, scale=100)

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
        self.assertEqual(self.ftg.tilecoord(1, 428000, 336000), TileCoord(1, 4, 7))
        self.assertEqual(self.ftg.tilecoord(1, 430000, 334000), TileCoord(1, 5, 8))
        self.assertEqual(self.ftg.tilecoord(1, 432000, 332000), TileCoord(1, 6, 9))


class TestFreeTileGridWithSubMetrics(unittest.TestCase):

    def setUp(self):
        self.ftg = FreeTileGrid(resolutions=(2, 1), max_extent=(420000, 30000, 900000, 350000), tile_size=100, scale=200)
        self.ftg2 = FreeTileGrid(resolutions=(2, 1), max_extent=(420000, 30000, 900000, 350000), tile_size=256, scale=10)

    def test_extent(self):
        self.assertEqual(self.ftg.extent(TileCoord(0, 0, 0)), (420000, 349999, 420001, 350000))
        self.assertEqual(self.ftg.extent(TileCoord(1, 0, 0)), (420000, 349999.5, 420000.5, 350000))

        self.assertEqual(self.ftg2.extent(TileCoord(0, 0, 0)), (420000, 349948.8, 420051.2, 350000))
        self.assertEqual(self.ftg2.extent(TileCoord(1, 0, 0)), (420000, 349974.4, 420025.6, 350000))

    def test_extent_border(self):
        self.assertEqual(self.ftg.extent(TileCoord(0, 0, 0), 50), (419999.5, 349998.5, 420001.5, 350000.5))
        self.assertEqual(self.ftg.extent(TileCoord(1, 0, 0), 100), (419999.5, 349999, 420001, 350000.5))

        self.assertEqual(self.ftg2.extent(TileCoord(0, 0, 0), 50), (419990.0, 349938.8, 420061.2, 350010))
        self.assertEqual(self.ftg2.extent(TileCoord(1, 0, 0), 50), (419995, 349969.4, 420030.6, 350005))

    def test_extent_metatile(self):
        self.assertEqual(self.ftg.extent(TileCoord(1, 0, 0, 3)), (420000, 349998.5, 420001.5, 350000))

        self.assertEqual(self.ftg2.extent(TileCoord(1, 0, 0, 3)), (420000, 349923.2, 420076.8, 350000))

    def test_extent_metatile_border(self):
        self.assertEqual(self.ftg.extent(TileCoord(1, 0, 0, 3), 50), (419999.75, 349998.25, 420001.75, 350000.25))

        self.assertEqual(self.ftg2.extent(TileCoord(1, 0, 0, 3), 50), (419995, 349918.2, 420081.8, 350005))

    def test_tilecoord(self):
        self.assertEqual(self.ftg.tilecoord(0, 420000.75, 349999.25), TileCoord(0, 0, 0))
        self.assertEqual(self.ftg.tilecoord(1, 420000.25, 349999.75), TileCoord(1, 0, 0))

        self.assertEqual(self.ftg2.tilecoord(0, 420000.01, 349999.99), TileCoord(0, 0, 0))
        self.assertEqual(self.ftg2.tilecoord(0, 420010, 349990), TileCoord(0, 0, 0))
        self.assertEqual(self.ftg2.tilecoord(0, 420051.19, 349948.81), TileCoord(0, 0, 0))
        self.assertEqual(self.ftg2.tilecoord(0, 420051.21, 349948.79), TileCoord(0, 1, 1))


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
        self.assertEqual(list(islice(self.qtg.zs(), 50)), [e for e in range(50)])


class TestQuadTileGridFlipY(unittest.TestCase):

    def setUp(self):
        self.qtsn = QuadTileGrid()
        self.qtsf = QuadTileGrid(flip_y=True)

    def test_flip_y(self):
        self.assertEqual(self.qtsn.extent(TileCoord(2, 0, 0)), self.qtsf.extent(TileCoord(2, 0, 3)))
        self.assertEqual(self.qtsn.extent(TileCoord(2, 1, 1)), self.qtsf.extent(TileCoord(2, 1, 2)))
        self.assertEqual(self.qtsn.extent(TileCoord(2, 2, 2)), self.qtsf.extent(TileCoord(2, 2, 1)))
        self.assertEqual(self.qtsn.extent(TileCoord(2, 3, 3)), self.qtsf.extent(TileCoord(2, 3, 0)))
