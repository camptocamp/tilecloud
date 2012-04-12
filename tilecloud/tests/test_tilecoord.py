import unittest

from tilecloud import TileCoord


class TestTileCoord(unittest.TestCase):

    def test_init(self):
        tc = TileCoord(1, 2, 3)
        self.assertEqual(tc.z, 1)
        self.assertEqual(tc.x, 2)
        self.assertEqual(tc.y, 3)

    def test_cmp(self):
        self.assertTrue(TileCoord(1, 3, 4) < TileCoord(2, 3, 4))
        self.assertTrue(TileCoord(2, 2, 4) < TileCoord(2, 3, 4))
        self.assertTrue(TileCoord(2, 3, 3) < TileCoord(2, 3, 4))
        self.assertTrue(TileCoord(2, 3, 4) == TileCoord(2, 3, 4))

    def test_hash(self):
        self.assertEqual(hash(TileCoord(1, 0, 0)), 0)
        self.assertNotEqual(hash(TileCoord(1, 0, 0)), hash(TileCoord(1, 0, 1)))

    def test_str(self):
        self.assertEqual(str(TileCoord(1, 2, 3)), '1/2/3')

    def test_children(self):
        tc = TileCoord(1, 2, 3)
        self.assertEqual(sorted(tc.children()), [TileCoord(2, 4, 6), TileCoord(2, 4, 7), TileCoord(2, 5, 6), TileCoord(2, 5, 7)])

    def test_normalize(self):
        self.assertEqual(TileCoord(2, 2, 2).normalize(), (0.5, 0.5))

    def test_parent(self):
        self.assertEqual(TileCoord(5, 11, 21).parent(), TileCoord(4, 5, 10))

    def test_parent_root(self):
        self.assertEqual(TileCoord(0, 0, 0).parent(), None)

    def test_tuple(self):
        self.assertEqual(TileCoord(1, 2, 3).tuple(), (1, 2, 3))

    def test_from_normalized_coord(self):
        self.assertEqual(TileCoord.from_normalized_coord(2, (0.5, 0.5)), TileCoord(2, 2, 2))

    def test_from_string(self):
        self.assertEqual(TileCoord.from_string('1/2/3'), TileCoord(1, 2, 3))

    def test_from_tuple(self):
        self.assertEqual(TileCoord.from_tuple((1, 2, 3)), TileCoord(1, 2, 3))

    def test_from_wgs84(self):
        self.assertEqual(TileCoord.from_wgs84(0, 0, 0), TileCoord(0, 0, 0))
        self.assertEqual(TileCoord.from_wgs84(1, -90, 45), TileCoord(1, 0, 0))
        self.assertEqual(TileCoord.from_wgs84(1, -90, -45), TileCoord(1, 0, 1))
        self.assertEqual(TileCoord.from_wgs84(1, 90, 45), TileCoord(1, 1, 0))
        self.assertEqual(TileCoord.from_wgs84(1, 90, -45), TileCoord(1, 1, 1))
