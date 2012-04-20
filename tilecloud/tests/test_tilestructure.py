import unittest

from tilecloud import TileCoord
from tilecloud.structure.quad import QuadTileStructure


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
