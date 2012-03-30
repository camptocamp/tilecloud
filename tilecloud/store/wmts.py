from tilecloud.store.url import URLTileStore
from tilecloud.layout.wmts import WMTSTileLayout


class WMTSTileStore(URLTileStore):

    def __init__(self, url=None, layer=None, style=None, format=None, tile_matrix_set=None, tile_matrix=None, **kwargs):
        layout = WMTSTileLayout(url, layer, style, format, tile_matrix_set, tile_matrix)
        URLTileStore.__init__(self, (layout,), **kwargs)
