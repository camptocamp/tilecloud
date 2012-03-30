from tilecloud import TileLayout


class WMSTileLayout(TileLayout):

    def __init__(self, url, layers, srid, image_format, metatile_configuration):
        self.metatile_configuration = metatile_configuration
        self.url = url
        self.layers = layers
        self.srid = srid
        self.image_format = image_format

    def filename(self, tilecoord):
        size = str(self.metatile_configuration.tile_size * self.metatile_configuration.size + 
                2 * self.metatile_configuration.buffer)
        bbox = self.meta_to_bbox(tilecoord)
        query = (
                ('LAYERS', self.layers),
                ('FORMAT', 'image/png' if self.image_format == 'png' else 'image/jpeg'),
                ('TRANSPARENT', 'TRUE' if self.image_format == 'png' else 'FALSE'),
                ('SERVICE', 'WMS'),
                ('VERSION', '1.1.1'),
                ('REQUEST', 'GetMap'),
                ('STYLES', ''),
                ('SRS', 'EPSG:' + str(self.srid)),
                ('BBOX', ','.join([str(b) for b in bbox])),
                ('WIDTH', size),
                ('HEIGHT', size),
        )
        return self.url + '?' + '&'.join('='.join(p) for p in query)

    def px_to_unit(self, px, zoom, origin):
        return px * self.metatile_configuration.resolutions[zoom] + origin

    def meta_to_bbox(self, meta):
        return (
            self.px_to_unit(meta.x * self.metatile_configuration.tile_size * self.metatile_configuration.size - 
                    self.metatile_configuration.buffer, 
                    meta.z, self.metatile_configuration.max_extent[0]),
            self.px_to_unit(meta.y * self.metatile_configuration.tile_size * self.metatile_configuration.size - 
                    self.metatile_configuration.buffer, 
                    meta.z, self.metatile_configuration.max_extent[1]),
            self.px_to_unit((meta.x + 1) * self.metatile_configuration.tile_size * self.metatile_configuration.size + 
                    self.metatile_configuration.buffer, 
                    meta.z, self.metatile_configuration.max_extent[0]),
            self.px_to_unit((meta.y + 1) * self.metatile_configuration.tile_size * self.metatile_configuration.size + 
                    self.metatile_configuration.buffer, 
                    meta.z, self.metatile_configuration.max_extent[1]),
        )
