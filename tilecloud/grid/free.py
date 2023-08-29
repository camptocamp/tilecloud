from collections.abc import Iterator, Sequence
from math import floor
from typing import Optional, Union

from tilecloud import Bounds, NotSupportedOperation, TileCoord, TileGrid


class FreeTileGrid(TileGrid):
    def __init__(
        self,
        resolutions: Sequence[Union[int, float]],
        max_extent: Optional[Union[tuple[int, int, int, int], tuple[float, float, float, float]]] = None,
        tile_size: Optional[float] = None,
        scale: int = 1,
        flip_y: bool = False,
    ) -> None:
        TileGrid.__init__(self, max_extent=max_extent, tile_size=tile_size, flip_y=flip_y)
        assert list(resolutions) == sorted(resolutions, reverse=True)
        assert all(isinstance(r, (int, float)) for r in resolutions)
        self.resolutions = resolutions
        self.scale = float(scale)
        self.parent_zs: list[Optional[int]] = []
        self.child_zs: list[list[int]] = []
        for i, resolution in enumerate(self.resolutions):
            for parent in range(i - 1, -1, -1):
                if self.resolutions[parent] % resolution == 0:
                    self.parent_zs.append(parent)
                    self.child_zs[parent].append(i)
                    break
            else:
                self.parent_zs.append(None)
            self.child_zs.append([])

    def children(self, tilecoord: TileCoord) -> Iterator[TileCoord]:
        if tilecoord.z < len(self.resolutions):
            for child_z in self.child_zs[tilecoord.z]:
                factor = self.resolutions[tilecoord.z] / self.resolutions[child_z]
                for i in range(0, int(factor)):
                    x = round(factor * tilecoord.x + i)  # pylint: disable=invalid-name
                    for j in range(0, int(factor)):
                        y = round(factor * tilecoord.y + j)  # pylint: disable=invalid-name
                        yield TileCoord(child_z, x, y)

    def extent(self, tilecoord: TileCoord, border: float = 0) -> tuple[float, float, float, float]:
        assert self.max_extent
        y: float = tilecoord.y  # pylint: disable=invalid-name
        if not self.flip_y:
            n = (  # pylint: disable=invalid-name
                self.scale
                * (self.max_extent[3] - self.max_extent[1])
                / float(self.tile_size * self.resolutions[tilecoord.z])
            )
            y = n - y - tilecoord.n  # pylint: disable=invalid-name
        minx = (
            self.max_extent[0]
            + (self.tile_size * tilecoord.x - border) * self.resolutions[tilecoord.z] / self.scale
        )
        miny = self.max_extent[1] + (self.tile_size * y - border) * self.resolutions[tilecoord.z] / self.scale
        maxx = (
            self.max_extent[0]
            + (self.tile_size * (tilecoord.x + tilecoord.n) + border)
            * self.resolutions[tilecoord.z]
            / self.scale
        )
        maxy = (
            self.max_extent[1]
            + (self.tile_size * (y + tilecoord.n) + border) * self.resolutions[tilecoord.z] / self.scale
        )
        return minx, miny, maxx, maxy

    def parent(self, tilecoord: TileCoord) -> Optional[TileCoord]:
        parent_z = self.parent_zs[tilecoord.z]
        if parent_z is None:
            return None
        factor = self.resolutions[parent_z] / self.resolutions[tilecoord.z]
        return TileCoord(parent_z, int(tilecoord.x // factor), int(tilecoord.y // factor))

    def roots(self) -> Iterator[TileCoord]:
        for zoom, parent_zoom in enumerate(self.parent_zs):
            if parent_zoom is None:
                x, s = 0, 0.0  # pylint: disable=invalid-name
                while s < self.resolutions[0]:
                    y, t = 0, 0.0  # pylint: disable=invalid-name
                    while t < self.resolutions[0]:
                        yield TileCoord(zoom, x, y)
                        y += 1  # pylint: disable=invalid-name
                        t += self.resolutions[zoom]  # pylint: disable=invalid-name
                    x += 1  # pylint: disable=invalid-name
                    s += self.resolutions[zoom]  # pylint: disable=invalid-name

    def tilecoord(self, z: int, x: float, y: float) -> TileCoord:
        tx = (  # pylint: disable=invalid-name
            self.scale * (x - self.max_extent[0]) / (self.resolutions[z] * self.tile_size)
        )
        ty = (  # pylint: disable=invalid-name
            self.scale * (y - self.max_extent[1]) / float(self.resolutions[z] * self.tile_size)
        )

        if not self.flip_y:
            n = (  # pylint: disable=invalid-name
                self.scale
                * (self.max_extent[3] - self.max_extent[1])
                / float(self.tile_size * self.resolutions[z])
            )
            ty = n - ty  # pylint: disable=invalid-name

        return TileCoord(z, int(floor(tx)), int(floor(ty)))

    def zs(self) -> range:
        return range(len(self.resolutions))

    def fill_up(self, z: int, bounds: tuple[Bounds, Bounds]) -> tuple[Bounds, Bounds]:
        raise NotSupportedOperation()

    def fill_down(self, z: int, bounds: tuple[Bounds, Bounds]) -> tuple[Bounds, Bounds]:
        raise NotSupportedOperation()
