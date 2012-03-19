from tilecloud import TileLayout
from tilecloud.store.url import URLTileStore


class WMTSTileLayout(TileLayout):

    def __init__(self, url=None, layer=None, style=None, format=None, tile_matrix_set=None, tile_matrix=None):
        self.url = url
        self.layer = layer
        self.style = style
        self.format = format
        self.tile_matrix_set = tile_matrix_set
        self.tile_matrix = tile_matrix or str

    def filename(self, tilecoord):
        query = (
                ('Service', 'WMTS'),
                ('Request', 'GetTile'),
                ('Version', '1.0.0'),
                ('Layer', self.layer),
                ('Style', self.style),
                ('Format', self.format),
                ('TileMatrixSet', self.tile_matrix_set),
                ('TileMatrix', self.tile_matrix(tilecoord.z)),
                ('TileRow', str(tilecoord.y)),
                ('TileCol', str(tilecoord.x)))
        return self.url + '?' + '&'.join('='.join(p) for p in query)


class WMTSTileStore(URLTileStore):

    def __init__(self, url=None, layer=None, style=None, format=None, tile_matrix_set=None, tile_matrix=None, **kwargs):
        layout = WMTSTileLayout(url, layer, style, format, tile_matrix_set, tile_matrix)
        URLTileStore.__init__(self, (layout,), **kwargs)
