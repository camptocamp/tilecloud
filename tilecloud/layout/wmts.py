from collections.abc import Iterable
from typing import Callable, Optional

from tilecloud import NotSupportedOperation, TileCoord, TileLayout


class WMTSTileLayout(TileLayout):
    """WMTS tile layout."""

    def __init__(
        self,
        url: str = "",
        layer: Optional[str] = None,
        style: Optional[str] = None,
        format_pattern: Optional[str] = None,
        tile_matrix_set: Optional[str] = None,
        tile_matrix: Callable[[int], str] = str,
        dimensions_name: Iterable[str] = (),
        request_encoding: str = "KVP",
    ) -> None:
        self.url = url
        assert layer is not None
        self.layer = layer
        assert style is not None
        self.style = style
        assert format_pattern is not None
        self.format = format_pattern
        assert tile_matrix_set is not None
        self.tile_matrix_set = tile_matrix_set
        self.tile_matrix = tile_matrix
        self.dimensions_name = dimensions_name
        self.request_encoding = request_encoding

        if self.request_encoding == "KVP":
            if not self.url or self.url[-1] != "?":
                self.url += "?"
        elif self.url and self.url[-1] != "/":
            self.url += "/"

    def filename(self, tilecoord: TileCoord, metadata: Optional[dict[str, str]] = None) -> str:
        metadata = {} if metadata is None else metadata
        # Careful the order is important for the REST request encoding
        query: list[tuple[str, str]] = []
        if self.request_encoding == "KVP":
            query.extend([("Service", "WMTS"), ("Request", "GetTile"), ("Format", self.format)])

        query.extend([("Version", "1.0.0"), ("Layer", self.layer), ("Style", self.style)])

        for name in self.dimensions_name:
            query.append((name, metadata["dimension_" + name]))

        query.extend(
            [
                ("TileMatrixSet", self.tile_matrix_set),
                ("TileMatrix", str(self.tile_matrix(tilecoord.z))),
                ("TileRow", str(tilecoord.y)),
                ("TileCol", str(tilecoord.x)),
            ]
        )
        if self.request_encoding == "KVP":
            return self.url + "&".join("=".join(p) for p in query)
        return self.url + "/".join(p[1] for p in query) + self.format

    def tilecoord(self, filename: str) -> TileCoord:
        raise NotSupportedOperation()
