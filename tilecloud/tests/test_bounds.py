import unittest

from tilecloud import Bounds


class TestBounds(unittest.TestCase):
    def test_empty(self) -> None:
        bounds = Bounds()
        assert len(bounds) == 0
        assert 1 not in bounds
        self.assertRaises(StopIteration, next, iter(bounds))
        assert bounds == bounds

    def test_init_one_argument(self) -> None:
        bounds = Bounds(1)
        assert list(bounds) == [1]

    def test_init_two_arguments(self) -> None:
        bounds = Bounds(1, 3)
        assert list(bounds) == [1, 2]

    def test_add(self) -> None:
        bounds = Bounds()
        assert len(bounds) == 0
        bounds.add(1)
        assert list(bounds) == [1]
        bounds.add(1)
        assert list(bounds) == [1]
        bounds.add(2)
        assert list(bounds) == [1, 2]

    def test_update(self) -> None:
        bounds1 = Bounds(1, 3)
        bounds2 = Bounds(3, 5)
        assert bounds1.update(bounds2) is bounds1
        assert len(bounds1) == 4
        assert list(bounds1) == [1, 2, 3, 4]

    def test_update_empty(self) -> None:
        bounds1 = Bounds()
        bounds2 = Bounds(3, 5)
        assert bounds1.update(bounds2) is bounds1
        assert list(bounds1) == [3, 4]

    def test_union_empty_empty(self) -> None:
        bounds1 = Bounds()
        bounds2 = Bounds()
        bounds3 = bounds1.union(bounds2)
        assert bounds3 is not bounds1
        assert bounds3 is not bounds2
        assert len(bounds3) == 0

    def test_union_empty_normal(self) -> None:
        bounds1 = Bounds()
        bounds2 = Bounds(3, 5)
        bounds3 = bounds1.union(bounds2)
        assert bounds3 is not bounds1
        assert bounds3 is not bounds2
        assert list(bounds3) == [3, 4]

    def test_union_normal_empty(self) -> None:
        bounds1 = Bounds(1, 3)
        bounds2 = Bounds()
        bounds3 = bounds1.union(bounds2)
        assert bounds3 is not bounds1
        assert bounds3 is not bounds2
        assert list(bounds3) == [1, 2]

    def test_union_normal_normal(self) -> None:
        bounds1 = Bounds(1, 3)
        bounds2 = Bounds(3, 5)
        bounds3 = bounds1.union(bounds2)
        assert bounds3 is not bounds1
        assert bounds3 is not bounds2
        assert list(bounds3) == [1, 2, 3, 4]
