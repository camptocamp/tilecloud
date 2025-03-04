from typing import Any

from tilecloud import BoundingPyramid, NotSupportedOperation, Tile, TileStore


class BoundingPyramidTileStore(TileStore):
    """All tiles in a bounding box."""

    def __init__(self, bounding_pyramid: BoundingPyramid | None = None, **kwargs: Any) -> None:
        TileStore.__init__(self, **kwargs)
        self.bounding_pyramid = bounding_pyramid or BoundingPyramid()

    def get_one(self, tile: Tile) -> Tile | None:
        if tile and tile.tilecoord in self.get_cheap_bounding_pyramid():
            return tile
        return None

    def get_cheap_bounding_pyramid(self) -> BoundingPyramid:
        assert self.bounding_pyramid is not None
        return self.bounding_pyramid

    def put_one(self, tile: Tile) -> Tile:
        self.get_cheap_bounding_pyramid().add(tile.tilecoord)
        return tile

    def delete_one(self, tile: Tile) -> Tile:
        raise NotSupportedOperation
