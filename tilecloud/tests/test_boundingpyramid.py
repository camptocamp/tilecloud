import unittest

from tilecloud import BoundingPyramid, Bounds, TileCoord


class TestBoundingPyramid(unittest.TestCase):
    def test_empty(self) -> None:
        bp = BoundingPyramid()
        self.assertEqual(len(bp), 0)
        self.assertFalse(TileCoord(0, 0, 0) in bp)
        self.assertRaises(StopIteration, next, iter(bp))

    def test_eq(self) -> None:
        self.assertEqual(BoundingPyramid(), BoundingPyramid())
        self.assertEqual(
            BoundingPyramid({5: (Bounds(2, 5), Bounds(6, 15))}),
            BoundingPyramid({5: (Bounds(2, 5), Bounds(6, 15))}),
        )

    def test_add(self) -> None:
        bp = BoundingPyramid()
        bp.add(TileCoord(1, 0, 0))
        self.assertEqual(len(bp), 1)
        self.assertTrue(TileCoord(1, 0, 0) in bp)
        self.assertFalse(TileCoord(1, 0, 1) in bp)
        self.assertFalse(TileCoord(1, 1, 0) in bp)
        self.assertFalse(TileCoord(1, 1, 1) in bp)
        self.assertEqual(list(bp), [TileCoord(1, 0, 0)])

    def test_fill_down(self) -> None:
        bp = BoundingPyramid()
        bp.add(TileCoord(1, 1, 0))
        bp.fill_down(3)
        self.assertEqual(bp.zget(2), (Bounds(2, 4), Bounds(0, 2)))
        self.assertEqual(bp.zget(3), (Bounds(4, 8), Bounds(0, 4)))

    def test_fill_up(self) -> None:
        bp = BoundingPyramid()
        bp.add(TileCoord(2, 1, 3))
        bp.fill_up(0)
        self.assertEqual(bp.zget(1), (Bounds(0, 1), Bounds(1, 2)))
        self.assertEqual(bp.zget(0), (Bounds(0, 1), Bounds(0, 1)))

    def test_fill_up2(self) -> None:
        bp = BoundingPyramid({1: (Bounds(0, 2), Bounds(1, 2))})
        bp.add(TileCoord(2, 1, 3))
        bp.fill_up(0)
        self.assertEqual(bp.zget(1), (Bounds(0, 2), Bounds(1, 2)))
        self.assertEqual(bp.zget(0), (Bounds(0, 1), Bounds(0, 1)))

    def test_iterbottomup(self) -> None:
        bp = BoundingPyramid()
        bp.add(TileCoord(2, 1, 3))
        bp.fill_up(0)
        self.assertEqual(
            list(bp.iterbottomup()), [TileCoord(2, 1, 3), TileCoord(1, 0, 1), TileCoord(0, 0, 0)]
        )

    def test_itertopdown(self) -> None:
        bp = BoundingPyramid()
        bp.add(TileCoord(2, 1, 3))
        bp.fill_up(0)
        self.assertEqual(list(bp.itertopdown()), [TileCoord(0, 0, 0), TileCoord(1, 0, 1), TileCoord(2, 1, 3)])

    def test_ziter(self) -> None:
        bp = BoundingPyramid()
        bp.add(TileCoord(2, 1, 3))
        bp.fill_up(0)
        self.assertEqual(list(bp.ziter(1)), [TileCoord(1, 0, 1)])

    def test_zs(self) -> None:
        bp = BoundingPyramid()
        bp.add(TileCoord(2, 1, 3))
        bp.fill_up(0)
        self.assertEqual(sorted(bp.zs()), [0, 1, 2])

    def test_from_string_star(self) -> None:
        bp = BoundingPyramid.from_string("0/0/0:2/*/*")
        self.assertEqual(bp.zget(0), (Bounds(0, 1), Bounds(0, 1)))
        self.assertEqual(bp.zget(1), (Bounds(0, 2), Bounds(0, 2)))
        self.assertEqual(bp.zget(2), (Bounds(0, 4), Bounds(0, 4)))
        self.assertRaises(KeyError, bp.zget, 3)

    def test_from_string_relative(self) -> None:
        bp = BoundingPyramid.from_string("2/1/3:+1/+1/+1")
        self.assertRaises(KeyError, bp.zget, 1)
        self.assertEqual(bp.zget(2), (Bounds(1, 2), Bounds(3, 4)))
        self.assertEqual(bp.zget(3), (Bounds(2, 4), Bounds(6, 8)))
        self.assertRaises(KeyError, bp.zget, 4)

    def test_from_string_one_level(self) -> None:
        bp = BoundingPyramid.from_string("5/9/13:12/15")
        self.assertRaises(KeyError, bp.zget, 4)
        self.assertEqual(bp.zget(5), (Bounds(9, 12), Bounds(13, 15)))
        self.assertRaises(KeyError, bp.zget, 6)

    def test_from_string_up(self) -> None:
        bp = BoundingPyramid.from_string("2/1/3:0/2/4")
        self.assertEqual(bp.zget(0), (Bounds(0, 1), Bounds(0, 1)))
        self.assertEqual(bp.zget(1), (Bounds(0, 1), Bounds(1, 2)))
        self.assertEqual(bp.zget(2), (Bounds(1, 2), Bounds(3, 4)))
        self.assertRaises(KeyError, bp.zget, 3)

    def test_from_string_error(self) -> None:
        self.assertRaises(ValueError, BoundingPyramid.from_string, "1/2/3:5/A")

    def test_full(self) -> None:
        bp = BoundingPyramid.full(1, 3)
        self.assertRaises(KeyError, bp.zget, 0)
        self.assertEqual(bp.zget(1), (Bounds(0, 2), Bounds(0, 2)))
        self.assertEqual(bp.zget(2), (Bounds(0, 4), Bounds(0, 4)))
        self.assertEqual(bp.zget(3), (Bounds(0, 8), Bounds(0, 8)))
        self.assertRaises(KeyError, bp.zget, 4)

    def test_metatilecoords(self) -> None:
        bp = BoundingPyramid.full(1, 2)
        metatilecoords = bp.metatilecoords(2)
        self.assertEqual(TileCoord(1, 0, 0, 2), next(metatilecoords))
        self.assertEqual(TileCoord(2, 0, 0, 2), next(metatilecoords))
        self.assertEqual(TileCoord(2, 0, 2, 2), next(metatilecoords))
        self.assertEqual(TileCoord(2, 2, 0, 2), next(metatilecoords))
        self.assertEqual(TileCoord(2, 2, 2, 2), next(metatilecoords))
        self.assertRaises(StopIteration, next, metatilecoords)


class TestGoogleTileGrid(unittest.TestCase):
    def test_fill(self) -> None:
        bp = BoundingPyramid()
        bp.fill(range(0, 8), (572215.4395248143, 5684416.95917649, 1277662.36597472, 6145307.39552287))
        self.assertEqual(bp.zget(0), (Bounds(0, 1), Bounds(0, 1)))
        self.assertEqual(bp.zget(1), (Bounds(1, 2), Bounds(0, 1)))
        self.assertEqual(bp.zget(2), (Bounds(2, 3), Bounds(1, 2)))
        self.assertEqual(bp.zget(3), (Bounds(4, 5), Bounds(2, 3)))
        self.assertEqual(bp.zget(4), (Bounds(8, 9), Bounds(5, 6)))
        self.assertEqual(bp.zget(5), (Bounds(16, 18), Bounds(11, 12)))
        self.assertEqual(bp.zget(6), (Bounds(32, 35), Bounds(22, 23)))
        self.assertEqual(bp.zget(7), (Bounds(65, 69), Bounds(44, 46)))
