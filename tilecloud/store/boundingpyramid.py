from tilecloud import BoundingPyramid, TileStore


class BoundingPyramidTileStore(TileStore):
    """All tiles in a bounding box"""

    def __init__(self, bounding_pyramid=None, **kwargs):
        TileStore.__init__(self, **kwargs)
        self.bounding_pyramid = bounding_pyramid or BoundingPyramid()

    def get_one(self, tile):
        if tile and tile.tilecoord in self.bounding_pyramid:
            return tile
        else:
            return None

    def get_cheap_bounding_pyramid(self):
        return self.bounding_pyramid

    def put_one(self, tile):
        self.bounding_pyramid.add(tile.tilecoord)
        return tile
