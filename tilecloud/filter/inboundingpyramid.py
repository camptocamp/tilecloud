class InBoundingPyramid(object):

    def __init__(self, bounding_pyramid):
        self.bounding_pyramid = bounding_pyramid

    def __call__(self, tile):
        if tile is None or tile.tilecoord not in self.bounding_pyramid:
            return None
        return tile
