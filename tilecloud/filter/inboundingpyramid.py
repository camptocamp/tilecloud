from typing import Optional

from tilecloud import BoundingPyramid, Tile


class InBoundingPyramid:
    """
    Creates a filter that filters out tiles that are not in the specified bounding pyramid. When called the
    filter returns ``None`` if the tile is not in the bounding pyramid.

        bounding_pyramid:
        A :class:`tilecloud.BoundingPyramid` object.
    """

    def __init__(self, bounding_pyramid: BoundingPyramid):
        self.bounding_pyramid = bounding_pyramid

    def __call__(self, tile: Tile) -> Optional[Tile]:
        if tile is None or tile.tilecoord not in self.bounding_pyramid:
            return None
        return tile
