from collections.abc import Iterable, Iterator
from itertools import count
from typing import Optional

from tilecloud import Bounds, TileCoord, TileGrid


class QuadTileGrid(TileGrid):
    def __init__(
        self,
        max_extent: Optional[tuple[float, float, float, float]] = None,
        tile_size: Optional[int] = None,
        max_zoom: Optional[int] = None,
        flip_y: bool = False,
    ) -> None:
        TileGrid.__init__(self, max_extent=max_extent, tile_size=tile_size, flip_y=flip_y)
        self.max_zoom = max_zoom

    def children(self, tilecoord: TileCoord) -> Iterator[TileCoord]:
        if self.max_zoom is None or tilecoord.z < self.max_zoom:
            yield TileCoord(tilecoord.z + 1, 2 * tilecoord.x, 2 * tilecoord.y)
            yield TileCoord(tilecoord.z + 1, 2 * tilecoord.x + 1, 2 * tilecoord.y)
            yield TileCoord(tilecoord.z + 1, 2 * tilecoord.x, 2 * tilecoord.y + 1)
            yield TileCoord(tilecoord.z + 1, 2 * tilecoord.x + 1, 2 * tilecoord.y + 1)

    def extent(self, tilecoord: TileCoord, border: float = 0) -> tuple[float, float, float, float]:
        y = tilecoord.y  # pylint: disable=invalid-name
        if not self.flip_y:
            y = (1 << tilecoord.z) - y - tilecoord.n  # pylint: disable=invalid-name
        delta = float(border) / self.tile_size if border else 0
        min_x = self.max_extent[0] + (self.max_extent[2] - self.max_extent[0]) * (tilecoord.x - delta) / (
            1 << tilecoord.z
        )
        min_y = self.max_extent[1] + (self.max_extent[3] - self.max_extent[1]) * (y - delta) / (
            1 << tilecoord.z
        )
        max_x = self.max_extent[0] + (self.max_extent[2] - self.max_extent[0]) * (
            tilecoord.x + tilecoord.n + delta
        ) / (1 << tilecoord.z)
        max_y = self.max_extent[1] + (self.max_extent[3] - self.max_extent[1]) * (y + tilecoord.n + delta) / (
            1 << tilecoord.z
        )
        return (min_x, min_y, max_x, max_y)

    def fill_down(self, z: int, bounds: tuple[Bounds, Bounds]) -> tuple[Bounds, Bounds]:
        xbounds, ybounds = bounds
        assert xbounds.start is not None
        assert xbounds.stop is not None
        assert ybounds.start is not None
        assert ybounds.stop is not None
        return (Bounds(2 * xbounds.start, 2 * xbounds.stop), Bounds(2 * ybounds.start, 2 * ybounds.stop))

    def fill_up(self, z: int, bounds: tuple[Bounds, Bounds]) -> tuple[Bounds, Bounds]:
        assert z > 0
        xbounds, ybounds = bounds
        assert xbounds.start is not None
        assert xbounds.stop is not None
        assert ybounds.start is not None
        assert ybounds.stop is not None
        return (
            Bounds(xbounds.start // 2, max(xbounds.stop // 2, 1)),
            Bounds(ybounds.start // 2, max(ybounds.stop // 2, 1)),
        )

    def parent(self, tilecoord: TileCoord) -> Optional[TileCoord]:
        if tilecoord.z == 0:
            return None
        return TileCoord(tilecoord.z - 1, int(tilecoord.x // 2), int(tilecoord.y // 2))

    def roots(self) -> Iterator[TileCoord]:
        yield TileCoord(0, 0, 0)

    def tilecoord(self, z: int, x: float, y: float) -> TileCoord:
        tilecoord_x = int((x - self.max_extent[0]) * (1 << z) / (self.max_extent[2] - self.max_extent[0]))
        tilecoord_y = int((y - self.max_extent[1]) * (1 << z) / (self.max_extent[3] - self.max_extent[1]))
        if not self.flip_y:
            tilecoord_y = (1 << z) - tilecoord_y - 1
        return TileCoord(z, tilecoord_x, tilecoord_y)

    def zs(self) -> Iterable[int]:
        if self.max_zoom:
            return range(0, self.max_zoom + 1)
        return count(0)
