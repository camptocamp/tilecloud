from typing import Any, Optional

from tilecloud.layout.wmts import WMTSTileLayout
from tilecloud.store.url import URLTileStore


class WMTSTileStore(URLTileStore):
    def __init__(
        self,
        url: str = "",
        layer: Optional[str] = None,
        style: Optional[str] = None,
        format: Optional[str] = None,
        tile_matrix_set: Optional[str] = None,
        tile_matrix: type = str,
        **kwargs: Any,
    ):
        layout = WMTSTileLayout(url, layer, style, format, tile_matrix_set, tile_matrix)
        URLTileStore.__init__(self, (layout,), **kwargs)
