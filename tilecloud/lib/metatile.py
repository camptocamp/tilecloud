
class MetaTileConfiguration:

    def __init__(self, resolutions, max_extent, tile_size=256, size=8, buffer=0):
        self.resolutions = resolutions
        self.max_extent = max_extent
        self.tile_size = tile_size
        self.size = size
        self.buffer = buffer
