from collections.abc import Callable
from typing import Any

from tilecloud import NotSupportedOperation, Tile
from tilecloud.layout.wmts import WMTSTileLayout
from tilecloud.store.url import URLTileStore


class WMTSTileStore(URLTileStore):
    """A tile store that reads and writes tiles in WMTS format."""

    def __init__(
        self,
        url: str = "",
        layer: str | None = None,
        style: str | None = None,
        format_pattern: str | None = None,
        tile_matrix_set: str | None = None,
        tile_matrix: Callable[[int], str] = str,
        **kwargs: Any,
    ) -> None:
        layout = WMTSTileLayout(url, layer, style, format_pattern, tile_matrix_set, tile_matrix)
        URLTileStore.__init__(self, (layout,), **kwargs)

    def delete_one(self, tile: Tile) -> Tile:
        raise NotSupportedOperation
