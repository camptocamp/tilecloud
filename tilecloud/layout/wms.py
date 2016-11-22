from six.moves.urllib.parse import urlencode

from tilecloud import TileLayout


class WMSTileLayout(TileLayout):

    def __init__(self, url, layers, srs, format, tilegrid, border=0, params=None):
        if params is None:
            params = {}
        self.tilegrid = tilegrid
        self.url = url
        self.border = border
        self.params = {
            'LAYERS': layers,
            'FORMAT': format,
            'TRANSPARENT': 'TRUE' if format == 'image/png' else 'FALSE',
            'SERVICE': 'WMS',
            'VERSION': '1.1.1',
            'REQUEST': 'GetMap',
            'STYLES': '',
            'SRS': srs,
        }
        for key, value in params.items():
            self.params[key] = value

    def filename(self, tilecoord):
        bbox = self.tilegrid.extent(tilecoord, self.border)
        size = tilecoord.n * self.tilegrid.tile_size + 2 * self.border
        params = self.params.copy()
        params['BBOX'] = '{0:f},{1:f},{2:f},{3:f}'.format(*bbox)
        params['WIDTH'] = size
        params['HEIGHT'] = size
        return self.url + '?' + urlencode(params)
