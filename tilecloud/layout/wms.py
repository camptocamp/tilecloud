from urllib import urlencode

from tilecloud import TileLayout


class WMSTileLayout(TileLayout):

    def __init__(self, url, layers, srs, format, tilegrid, border=0):
        self.tilegrid = tilegrid
        self.url = url
        self.layers = layers
        self.srs = srs
        self.format = format
        self.border = border

    def filename(self, tilecoord):
        bbox = self.tilegrid.extent(tilecoord, self.border)
        size = tilecoord.n * self.tilegrid.tile_size + 2 * self.border
        return self.url + '?' + urlencode({
            'LAYERS': self.layers,
            'FORMAT': self.format,
            'TRANSPARENT': 'TRUE' if self.format == 'image/png' else 'FALSE',
            'SERVICE': 'WMS',
            'VERSION': '1.1.1',
            'REQUEST': 'GetMap',
            'STYLES': '',
            'SRS': self.srs,
            'BBOX': '%f,%f,%f,%f' % bbox,
            'WIDTH': size,
            'HEIGHT': size})
