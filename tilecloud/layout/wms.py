from tilecloud import TileLayout


class WMSTileLayout(TileLayout):

    def __init__(self, url, layers, srs, format, tilestructure, border=0):
        self.tilestructure = tilestructure
        self.url = url
        self.layers = layers
        self.srs = srs
        self.format = format
        self.border = border

    def filename(self, tilecoord):
        bbox = self.tilestructure.extent(tilecoord, self.border)
        size = tilecoord.n * self.tilestructure.tile_size + 2 * self.border
        query = (
                ('LAYERS', self.layers),
                ('FORMAT', self.format),
                ('TRANSPARENT', 'TRUE' if self.format == 'image/png' else 'FALSE'),
                ('SERVICE', 'WMS'),
                ('VERSION', '1.1.1'),
                ('REQUEST', 'GetMap'),
                ('STYLES', ''),
                ('SRS', self.srs),
                ('BBOX', '%f,%f,%f,%f' % bbox),
                ('WIDTH', str(size)),
                ('HEIGHT', str(size)),
        )
        return self.url + '?' + '&'.join('='.join(p) for p in query)
