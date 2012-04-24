import unittest

from tilecloud import MetaTileCoord, TileCoord, TileStructure
from tilecloud.structure.free import FreeTileStructure
from tilecloud.structure.quad import QuadTileStructure


class TestTileStructure(unittest.TestCase):

    def setUp(self):
        self.ts = TileStructure()

    def test_tilestructure(self):
        self.assertRaises(NotImplementedError, self.ts.extent, None)
        self.assertRaises(NotImplementedError, self.ts.children, None)
        self.assertRaises(NotImplementedError, self.ts.flip_y, None)
        self.assertRaises(NotImplementedError, self.ts.parent, None)
        self.assertRaises(NotImplementedError, self.ts.roots)
        self.assertRaises(NotImplementedError, self.ts.tilecoord, None, None, None)


class TestFreeTileStructure(unittest.TestCase):

    def setUp(self):
        self.resolutions = (1000, 999, 500, 250, 125, 123, 111, 100, 50, 25, 10)
        self.fts = FreeTileStructure(self.resolutions)

    def test_factors(self):
        for i, resolution in enumerate(self.resolutions):
            for child_z in self.fts.child_zs[i]:
                self.assertEquals(self.resolutions[i] % self.resolutions[child_z], 0)

    def test_root_parents(self):
        for root_z in set(root.z for root in self.fts.roots()):
            self.assertEquals(self.fts.parent(TileCoord(root_z, 0, 0)), None)

    def test_root_zero(self):
        self.assertEquals(self.fts.parent(TileCoord(0, 0, 0)), None)


class TestFreeTileStructure2(unittest.TestCase):

    def setUp(self):
        self.fts = FreeTileStructure(resolutions=(40, 20, 10, 5), max_extent=(420000, 330000, 900000, 350000), tile_size=100)

    def test_extent(self):
        self.assertEqual(self.fts.extent(TileCoord(1, 4, 6)), (428000, 342000, 430000, 344000))
        self.assertEqual(self.fts.extent(TileCoord(1, 5, 7)), (430000, 344000, 432000, 346000))

    def test_extent_border(self):
        self.assertEqual(self.fts.extent(TileCoord(1, 4, 6), 5), (427900, 341900, 430100, 344100))

    def test_extent_metatile(self):
        self.assertEqual(self.fts.extent(MetaTileCoord(2, 1, 4, 6)), (428000, 342000, 432000, 346000))

    def test_extent_metatile_border(self):
        self.assertEqual(self.fts.extent(MetaTileCoord(2, 1, 4, 6), 5), (427900, 341900, 432100, 346100))

    def test_tilecoord(self):
        self.assertEqual(self.fts.tilecoord(1, 428000, 342000), TileCoord(1, 4, 6))
        self.assertEqual(self.fts.tilecoord(1, 430000, 344000), TileCoord(1, 5, 7))
        self.assertEqual(self.fts.tilecoord(1, 430000, 344000), TileCoord(1, 5, 7))
        self.assertEqual(self.fts.tilecoord(1, 432000, 346000), TileCoord(1, 6, 8))


class TestFreeTileStructureWithScale(unittest.TestCase):

    def setUp(self):
        self.fts = FreeTileStructure(resolutions=(4000, 2000, 1000, 500), max_extent=(420000, 330000, 900000, 350000), tile_size=100, scale=100)

    def test_extent(self):
        self.assertEqual(self.fts.extent(TileCoord(1, 4, 6)), (428000, 342000, 430000, 344000))
        self.assertEqual(self.fts.extent(TileCoord(1, 5, 7)), (430000, 344000, 432000, 346000))

    def test_extent_border(self):
        self.assertEqual(self.fts.extent(TileCoord(1, 4, 6), 5), (427900, 341900, 430100, 344100))

    def test_extent_metatile(self):
        self.assertEqual(self.fts.extent(MetaTileCoord(2, 1, 4, 6)), (428000, 342000, 432000, 346000))

    def test_extent_metatile_border(self):
        self.assertEqual(self.fts.extent(MetaTileCoord(2, 1, 4, 6), 5), (427900, 341900, 432100, 346100))

    def test_tilecoord(self):
        self.assertEqual(self.fts.tilecoord(1, 428000, 342000), TileCoord(1, 4, 6))
        self.assertEqual(self.fts.tilecoord(1, 430000, 344000), TileCoord(1, 5, 7))
        self.assertEqual(self.fts.tilecoord(1, 430000, 344000), TileCoord(1, 5, 7))
        self.assertEqual(self.fts.tilecoord(1, 432000, 346000), TileCoord(1, 6, 8))


class TestFreeQuadTileStructureEquivalence(unittest.TestCase):

    def setUp(self):
        self.fts = FreeTileStructure([8, 4, 2, 1], tile_size=0.125)
        self.qts = QuadTileStructure(max_zoom=3)

    def test_children(self):
        tc = TileCoord(2, 2, 3)
        self.assertEqual(sorted(self.fts.children(tc)), sorted(self.qts.children(tc)))

    def test_children_root(self):
        tc = TileCoord(0, 0, 0)
        self.assertEqual(sorted(self.fts.children(tc)), sorted(self.qts.children(tc)))

    def test_extent(self):
        for z in xrange(0, 4):
            for x in xrange(0, 1 << z):
                for y in xrange(0, 1 << z):
                    tilecoord = TileCoord(z, x, y)
                    self.assertEqual(self.fts.extent(tilecoord), self.qts.extent(tilecoord))

    def test_flip_y(self):
        for z in xrange(0, 4):
            for x in xrange(0, 1 << z):
                for y in xrange(0, 1 << z):
                    tilecoord = TileCoord(z, x, y)
                    self.assertEqual(self.fts.flip_y(tilecoord), self.qts.flip_y(tilecoord))

    def test_parent(self):
        tc = TileCoord(3, 3, 5)
        self.assertEqual(self.fts.parent(tc), self.qts.parent(tc))

    def test_roots(self):
        self.assertEqual(list(self.fts.roots()), list(self.qts.roots()))


class TestQuadTileStructure(unittest.TestCase):

    def setUp(self):
        self.qts = QuadTileStructure(max_extent=(0.0, 1.0, 2.0, 3.0))

    def test_children(self):
        self.assertEqual(sorted(self.qts.children(TileCoord(1, 2, 3))), [TileCoord(2, 4, 6), TileCoord(2, 4, 7), TileCoord(2, 5, 6), TileCoord(2, 5, 7)])

    def test_children_root(self):
        self.assertEqual(sorted(self.qts.children(TileCoord(0, 0, 0))), [TileCoord(1, 0, 0), TileCoord(1, 0, 1), TileCoord(1, 1, 0), TileCoord(1, 1, 1)])

    def test_extent_z0(self):
        self.assertEqual(self.qts.extent(TileCoord(0, 0, 0)), (0.0, 1.0, 2.0, 3.0))

    def test_extent_z1(self):
        self.assertEqual(self.qts.extent(TileCoord(1, 0, 0)), (0.0, 1.0, 1.0, 2.0))
        self.assertEqual(self.qts.extent(TileCoord(1, 0, 1)), (0.0, 2.0, 1.0, 3.0))
        self.assertEqual(self.qts.extent(TileCoord(1, 1, 0)), (1.0, 1.0, 2.0, 2.0))
        self.assertEqual(self.qts.extent(TileCoord(1, 1, 1)), (1.0, 2.0, 2.0, 3.0))

    def test_extent_z2(self):
        self.assertEqual(self.qts.extent(TileCoord(2, 0, 0)), (0.0, 1.0, 0.5, 1.5))
        self.assertEqual(self.qts.extent(TileCoord(2, 1, 1)), (0.5, 1.5, 1.0, 2.0))
        self.assertEqual(self.qts.extent(TileCoord(2, 2, 2)), (1.0, 2.0, 1.5, 2.5))
        self.assertEqual(self.qts.extent(TileCoord(2, 3, 3)), (1.5, 2.5, 2.0, 3.0))

    def test_flip_y(self):
        self.assertEqual(self.qts.flip_y(TileCoord(2, 1, 0)), TileCoord(2, 1, 3))
        self.assertEqual(self.qts.flip_y(TileCoord(2, 1, 1)), TileCoord(2, 1, 2))
        self.assertEqual(self.qts.flip_y(TileCoord(2, 1, 2)), TileCoord(2, 1, 1))
        self.assertEqual(self.qts.flip_y(TileCoord(2, 1, 3)), TileCoord(2, 1, 0))

    def test_parent(self):
        self.assertEqual(self.qts.parent(TileCoord(5, 11, 21)), TileCoord(4, 5, 10))

    def test_parent_root(self):
        self.assertEqual(self.qts.parent(TileCoord(0, 0, 0)), None)

    def test_roots(self):
        self.assertEqual(list(self.qts.roots()), [TileCoord(0, 0, 0)])

    def test_tilecoord(self):
        for z in xrange(0, 4):
            for x in xrange(0, 1 << z):
                for y in xrange(0, 1 << z):
                    tilecoord = TileCoord(z, x, y)
                    minx, miny, maxx, maxy = self.qts.extent(tilecoord)
                    self.assertEqual(self.qts.tilecoord(z, minx, miny), tilecoord)
