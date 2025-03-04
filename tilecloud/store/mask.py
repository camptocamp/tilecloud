from collections.abc import Iterator
from typing import Any

import PIL.Image
import PIL.ImageFile

from tilecloud import (
    BoundingPyramid,
    Bounds,
    NotSupportedOperation,
    Tile,
    TileCoord,
    TileStore,
)


class MaskTileStore(TileStore):
    """A black and white image representing present and absent tiles."""

    image: PIL.Image.Image | PIL.ImageFile.ImageFile

    def __init__(self, z: int, bounds: tuple[Bounds, Bounds], file: str | None = None, **kwargs: Any) -> None:
        TileStore.__init__(self, **kwargs)
        self.zoom = z
        self.xbounds, self.ybounds = bounds
        assert self.xbounds.start is not None
        assert self.xbounds.stop is not None
        assert self.ybounds.start is not None
        assert self.ybounds.stop is not None
        self.width = self.xbounds.stop - self.xbounds.start
        self.height = self.ybounds.stop - self.ybounds.start
        if "bounding_pyramid" not in kwargs:
            self.bounding_pyramid = BoundingPyramid({self.zoom: (self.xbounds, self.ybounds)})
        if file:
            self.image = PIL.Image.open(file)
            assert self.image.mode == "1"
            assert self.image.size == (self.width, self.height)
        else:
            self.image = PIL.Image.new("1", (self.width, self.height))
        self.pixels = self.image.load()

    def delete_one(self, tile: Tile) -> Tile:
        assert self.xbounds.start is not None
        assert self.ybounds.stop is not None
        if tile.tilecoord.z == self.zoom:
            x = tile.tilecoord.x - self.xbounds.start  # pylint: disable=invalid-name
            y = self.ybounds.stop - tile.tilecoord.y - 1  # pylint: disable=invalid-name
            if 0 <= x < self.width and 0 <= y < self.height:
                self.pixels[x, y] = 0  # type: ignore[index]
        return tile

    def list(self) -> Iterator[Tile]:
        assert self.xbounds.start is not None
        assert self.ybounds.stop is not None
        for x in range(self.width):  # pylint: disable=invalid-name
            for y in range(self.height):  # pylint: disable=invalid-name
                if self.pixels[x, y]:  # type: ignore[index]
                    yield Tile(TileCoord(self.zoom, self.xbounds.start + x, self.ybounds.stop - y - 1))

    def put_one(self, tile: Tile) -> Tile:
        assert self.xbounds.start is not None
        assert self.ybounds.stop is not None
        x = tile.tilecoord.x - self.xbounds.start  # pylint: disable=invalid-name
        y = self.ybounds.stop - tile.tilecoord.y - 1  # pylint: disable=invalid-name
        if 0 <= x < self.width and 0 <= y < self.height:
            self.pixels[x, y] = 1  # type: ignore[index]
        return tile

    def save(self, file: str, format_pattern: str | None, **kwargs: Any) -> None:
        self.image.save(file, format_pattern, **kwargs)

    def get_one(self, tile: Tile) -> Tile | None:
        raise NotSupportedOperation
