import sys
from cStringIO import StringIO
from math import ceil

from PIL import Image

from tilecloud import TileStore, Tile, MetaTileCoord, Bounds, BoundingPyramid


class MetaTileStore(TileStore):

    def __init__(self, grid, meta_size, extent=None, **kwargs):
        self.grid = grid
        self.extent = extent
        self.meta_size = meta_size
        TileStore.__init__(self, **kwargs)

    def _tile_index_x(self, value, ratio):
        return (value - self.grid.max_extent[0]) / ratio

    def _tile_index_y(self, value, ratio):
        return (value - self.grid.max_extent[1]) / ratio

    def list(self):
        bounds = {}
        for zoom in range(0, len(self.grid.resolutions)):
            ratio = float(self.meta_size * self.grid.tile_size * self.grid.resolutions[zoom])
            if self.extent:
                x_bounds = Bounds(int(self._tile_index_x(self.extent[0], ratio)),
                        int(ceil(self._tile_index_x(self.extent[2], ratio))))
                y_bounds = Bounds(int(self._tile_index_y(self.extent[1], ratio)),
                        int(ceil(self._tile_index_y(self.extent[3], ratio))))
            else:
                x_bounds = Bounds(0, int(ceil(self._tile_index_x(self.grid.max_extent[2], ratio))))
                y_bounds = Bounds(0, int(ceil(self._tile_index_y(self.grid.max_extent[3], ratio))))

            bounds[zoom] = (x_bounds, y_bounds)

        bounding_pyramid = BoundingPyramid(bounds)
        for tilecoord in bounding_pyramid:
            yield Tile(MetaTileCoord(self.meta_size, tilecoord.z, tilecoord.x * self.meta_size, tilecoord.y * self.meta_size))


class MetaTileToTileStore(TileStore):

    def __init__(self, tile_size, buffer, image_format, **kwargs):
        self.tile_size = tile_size
        self.buffer = buffer
        self.image_format = image_format
        TileStore.__init__(self, **kwargs)

    def get(self, tiles):
        for metatile in tiles:
            metaimage = Image.open(StringIO(metatile.data))
            for tilecoord in metatile.tilecoord:
                x = tilecoord.x - metatile.tilecoord.x
                y = tilecoord.y - metatile.tilecoord.y
                px_x = self.buffer + x * self.tile_size
                px_y = self.buffer + y * self.tile_size
                image = metaimage.crop((px_x, px_y, px_x + self.tile_size, px_y + self.tile_size))
                string_io = StringIO()
                image.save(string_io, self.image_format)
                yield Tile(tilecoord, data=string_io.getvalue())
