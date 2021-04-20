import unittest

from tilecloud import BoundingPyramid, Bounds, TileCoord


class TestTileCoord(unittest.TestCase):
    def test_init(self) -> None:
        tc = TileCoord(1, 2, 3)
        self.assertEqual(tc.z, 1)
        self.assertEqual(tc.x, 2)
        self.assertEqual(tc.y, 3)

    def test_cmp(self) -> None:
        self.assertTrue(TileCoord(1, 3, 4) < TileCoord(2, 3, 4))
        self.assertTrue(TileCoord(2, 2, 4) < TileCoord(2, 3, 4))
        self.assertTrue(TileCoord(2, 3, 3) < TileCoord(2, 3, 4))
        self.assertTrue(TileCoord(2, 3, 4) == TileCoord(2, 3, 4))

    def test_hash(self) -> None:
        self.assertEqual(hash(TileCoord(1, 0, 0)), 0)
        self.assertNotEqual(hash(TileCoord(1, 0, 0)), hash(TileCoord(1, 0, 1)))

    def test_hash_metatile(self) -> None:
        bp = BoundingPyramid({4: (Bounds(0, 16), Bounds(0, 16))})
        metatilecoords = list(bp.metatilecoords(2))
        hashes = map(hash, metatilecoords)
        self.assertEqual(len(metatilecoords), len(set(hashes)))

    def test_iter(self) -> None:
        tilecoords = iter(TileCoord(3, 4, 6, 2))
        self.assertEqual(TileCoord(3, 4, 6), next(tilecoords))
        self.assertEqual(TileCoord(3, 4, 7), next(tilecoords))
        self.assertEqual(TileCoord(3, 5, 6), next(tilecoords))
        self.assertEqual(TileCoord(3, 5, 7), next(tilecoords))
        self.assertRaises(StopIteration, next, tilecoords)

    def test_str(self) -> None:
        self.assertEqual(str(TileCoord(1, 2, 3)), "1/2/3")

    def test_str_metatile(self) -> None:
        self.assertEqual("3/4/6:+2/+2", str(TileCoord(3, 4, 6, 2)))

    def test_str_metatile_error(self) -> None:
        self.assertRaises(ValueError, TileCoord.from_string, "3/4/6:+2/+3")

    def test_tuple(self) -> None:
        self.assertEqual(TileCoord(1, 2, 3).tuple(), (1, 2, 3, 1))

    def test_tuple_metatile(self) -> None:
        self.assertEqual(TileCoord(1, 2, 3, 2).tuple(), (1, 2, 3, 2))

    def test_from_string(self) -> None:
        self.assertEqual(TileCoord.from_string("1/2/3"), TileCoord(1, 2, 3))

    def test_from_string_metatile(self) -> None:
        self.assertEqual(TileCoord.from_string("1/2/3:+2/+2"), TileCoord(1, 2, 3, 2))

    def test_from_tuple(self) -> None:
        self.assertEqual(TileCoord.from_tuple((1, 2, 3)), TileCoord(1, 2, 3))
