from collections import defaultdict
import unittest

from tilecloud import TileCoord, TileStructure
from tilecloud.structure.free import FreeTileStructure
from tilecloud.structure.quad import QuadTileStructure


class TestTileStructure(unittest.TestCase):

    def setUp(self):
        self.ts = TileStructure()

    def test_tilestructure(self):
        self.assertRaises(NotImplementedError, self.ts.extent, None)
        self.assertRaises(NotImplementedError, self.ts.children, None)
        self.assertRaises(NotImplementedError, self.ts.parent, None)
        self.assertRaises(NotImplementedError, self.ts.roots)


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


class TestFreeQuadTileStructureEquivalence(unittest.TestCase):

    def setUp(self):
        self.fts = FreeTileStructure([16, 8, 4, 2])  # FIXME resolutions of 1 :-)
        self.qts = QuadTileStructure(max_zoom=3)

    def test_children(self):
        tc = TileCoord(2, 2, 3)
        self.assertEqual(sorted(self.fts.children(tc)), sorted(self.qts.children(tc)))

    def test_children_root(self):
        tc = TileCoord(0, 0, 0)
        self.assertEqual(sorted(self.fts.children(tc)), sorted(self.qts.children(tc)))

    def test_parent(self):
        tc = TileCoord(3, 3, 5)
        self.assertEqual(self.fts.parent(tc), self.qts.parent(tc))

    def test_roots(self):
        self.assertEqual(list(self.fts.roots()), list(self.qts.roots()))


class TestQuadTileStructure(unittest.TestCase):

    def setUp(self):
        self.qts = QuadTileStructure()

    def test_children(self):
        self.assertEqual(sorted(self.qts.children(TileCoord(1, 2, 3))), [TileCoord(2, 4, 6), TileCoord(2, 4, 7), TileCoord(2, 5, 6), TileCoord(2, 5, 7)])

    def test_children_root(self):
        self.assertEqual(sorted(self.qts.children(TileCoord(0, 0, 0))), [TileCoord(1, 0, 0), TileCoord(1, 0, 1), TileCoord(1, 1, 0), TileCoord(1, 1, 1)])

    def test_parent(self):
        self.assertEqual(self.qts.parent(TileCoord(5, 11, 21)), TileCoord(4, 5, 10))

    def test_parent_root(self):
        self.assertEqual(self.qts.parent(TileCoord(0, 0, 0)), None)

    def test_roots(self):
        self.assertEqual(list(self.qts.roots()), [TileCoord(0, 0, 0)])
