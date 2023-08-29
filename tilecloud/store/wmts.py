from typing import Any, Callable, Optional

from tilecloud import NotSupportedOperation, Tile
from tilecloud.layout.wmts import WMTSTileLayout
from tilecloud.store.url import URLTileStore


class WMTSTileStore(URLTileStore):
    def __init__(
        self,
        url: str = "",
        layer: Optional[str] = None,
        style: Optional[str] = None,
        format_pattern: Optional[str] = None,
        tile_matrix_set: Optional[str] = None,
        tile_matrix: Callable[[int], str] = str,
        **kwargs: Any,
    ):
        layout = WMTSTileLayout(url, layer, style, format_pattern, tile_matrix_set, tile_matrix)
        URLTileStore.__init__(self, (layout,), **kwargs)

    def delete_one(self, tile: Tile) -> Tile:
        raise NotSupportedOperation()
