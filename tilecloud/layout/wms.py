from tilecloud import TileLayout


class WMSTileLayout(TileLayout):

    def __init__(self, url, layers, srid, image_format, grid, buffer=0):
        self.grid = grid
        self.url = url
        self.layers = layers
        self.srid = srid
        self.image_format = image_format
        self.buffer = buffer

    def filename(self, tilecoord):
        bbox = self.grid.bounds(tilecoord, self.buffer)
        width = (bbox[0].stop - bbox[0].start) / self.grid.resolutions[tilecoord.z]
        height = (bbox[1].stop - bbox[1].start) / self.grid.resolutions[tilecoord.z]
        query = (
                ('LAYERS', self.layers),
                ('FORMAT', 'image/png' if self.image_format == 'png' else 'image/jpeg'),
                ('TRANSPARENT', 'TRUE' if self.image_format == 'png' else 'FALSE'),
                ('SERVICE', 'WMS'),
                ('VERSION', '1.1.1'),
                ('REQUEST', 'GetMap'),
                ('STYLES', ''),
                ('SRS', 'EPSG:%i' % self.srid),
                ('BBOX', '%f,%f,%f,%f' % (bbox[0].start, bbox[1].start, bbox[0].stop, bbox[1].stop)),
                ('WIDTH', '%i' % round(width)),
                ('HEIGHT', '%i' % round(height)),
        )
        return self.url + '?' + '&'.join('='.join(p) for p in query)
