import unittest

from tilecloud import BoundingPyramid, Bounds, MetaTileCoord, TileCoord


class TestMetaTileCoord(unittest.TestCase):

    def test_hash(self):
        bp = BoundingPyramid({4: (Bounds(0, 16), Bounds(0, 16))})
        metatilecoords = list(bp.metatilecoords(2))
        hashes = map(hash, metatilecoords)
        self.assertEqual(len(metatilecoords), len(set(hashes)))

    def test_iter(self):
        tilecoords = iter(MetaTileCoord(2, 3, 4, 6))
        self.assertEqual(TileCoord(3, 4, 6), next(tilecoords))
        self.assertEqual(TileCoord(3, 4, 7), next(tilecoords))
        self.assertEqual(TileCoord(3, 5, 6), next(tilecoords))
        self.assertEqual(TileCoord(3, 5, 7), next(tilecoords))
        self.assertRaises(StopIteration, next, tilecoords)

    def test_str(self):
        self.assertEqual('3/4/6:+2/+2', str(MetaTileCoord(2, 3, 4, 6)))
