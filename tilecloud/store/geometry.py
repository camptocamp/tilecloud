# -*- coding: utf-8 -*- #

from cStringIO import StringIO

from shapely.wkt import loads as loads_wkt
from PIL import Image

from tilecloud import TileStore, Tile, TileCoord, Bounds, BoundingPyramid


class GeometryMetaTileStore(TileStore):

    def __init__(self, metatile_configuration, geom=None, generator=None, image_format='png', **kwargs):
        self.metatile_configuration = metatile_configuration
        self.geom = geom or loads_wkt(self.polygon(self.metatile_configuration.max_extent))
        self.image_format = image_format
        self.generator = generator
        self.meta = None

    def list(self):
        bbox = self.geom.bounds
        bounds = {}
        for zoom in range(0, len(self.metatile_configuration.resolutions)):
            x_bounds = Bounds(self.unit_to_metatile(bbox[0], zoom, self.metatile_configuration.max_extent[0]),
                self.unit_to_metatile(bbox[2], zoom, self.metatile_configuration.max_extent[0]) + 1)
            y_bounds = Bounds(self.unit_to_metatile(bbox[1], zoom, self.metatile_configuration.max_extent[1]),
                self.unit_to_metatile(bbox[3], zoom, self.metatile_configuration.max_extent[1]) + 1)
            bounds[zoom] = (x_bounds, y_bounds)

        bounding_pyramid = BoundingPyramid(bounds)
        for tilecoord in bounding_pyramid:
            zoom, meta_x, meta_y = tilecoord.z, tilecoord.x, tilecoord.y
            for x in range(meta_x * self.metatile_configuration.size,
                    meta_x * self.metatile_configuration.size + self.metatile_configuration.size):
                for y in range(meta_y * self.metatile_configuration.size,
                        meta_y * self.metatile_configuration.size + self.metatile_configuration.size):
                    extent = loads_wkt(self.polygon((
                            self.tile_to_unit(x, zoom, self.metatile_configuration.max_extent[0]),
                            self.tile_to_unit(y, zoom, self.metatile_configuration.max_extent[1]),
                            self.tile_to_unit(x + 1, zoom, self.metatile_configuration.max_extent[0]),
                            self.tile_to_unit(y + 1, zoom, self.metatile_configuration.max_extent[1])
                    )))
                    tile = Tile(TileCoord(zoom, x, y), meta=tilecoord)
                    if extent.intersects(self.geom):
                        yield self.get_one(tile)

    def get_one(self, tile):
        if not self.meta or not self.meta == tile.meta:
            self.meta = tile.meta
            image = self.generator.get_one(Tile(self.meta)).data
            self.image = Image.open(StringIO(image))

        image = self.image.crop(self.bbox_to_crop(self.meta, tile.tilecoord))
        string_io = StringIO()
        image.save(string_io, self.image_format)
        tile.data = string_io.getvalue()
        return tile

    def polygon(self, bbox):
        minx, miny, maxx, maxy = bbox
        return "POLYGON((%(minx)d %(miny)d,%(minx)d %(maxy)d,%(maxx)d %(maxy)d,%(maxx)d %(miny)d,%(minx)d %(miny)d))" % {
            'minx': minx, 'miny': miny, 'maxx': maxx, 'maxy': maxy}

    def tile_to_unit(self, tile, zoom, origin):
        return tile * self.metatile_configuration.tile_size * self.metatile_configuration.resolutions[zoom] + origin

    def unit_to_metatile(self, m, zoom, origin):
        return int((m - origin) // (self.metatile_configuration.resolutions[zoom] * self.metatile_configuration.tile_size * self.metatile_configuration.size))

    def bbox_to_crop(self, meta, tile):
        x = tile.x - meta.x * self.metatile_configuration.size
        y = tile.y - meta.y * self.metatile_configuration.size
        px_x = self.metatile_configuration.buffer + x * self.metatile_configuration.tile_size
        px_y = self.metatile_configuration.buffer + y * self.metatile_configuration.tile_size
        return (px_x, px_y, px_x + self.metatile_configuration.tile_size, px_y + self.metatile_configuration.tile_size)
