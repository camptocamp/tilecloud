from typing import Any
from urllib.parse import urlencode

from tilecloud import NotSupportedOperation, TileCoord, TileGrid, TileLayout


class WMSTileLayout(TileLayout):
    """WMS tile layout."""

    def __init__(
        self,
        url: str,
        layers: str,
        srs: str,
        format_pattern: str,
        tilegrid: TileGrid,
        border: int = 0,
        params: dict[str, str] | None = None,
    ) -> None:
        if params is None:
            params = {}
        self.tilegrid = tilegrid
        self.url = url
        self.border = border
        self.params = {
            "LAYERS": layers,
            "FORMAT": format_pattern,
            "TRANSPARENT": "TRUE" if format_pattern in ("image/png", "image/webp") else "FALSE",
            "SERVICE": "WMS",
            "VERSION": "1.1.1",
            "REQUEST": "GetMap",
            "STYLES": "",
            "SRS": srs,
        }
        self.params.update(params)
        if params.get("FILTER") is not None:
            self.params["FILTER"] = params["FILTER"].format(**params)

    def filename(self, tilecoord: TileCoord, metadata: Any | None = None) -> str:
        metadata = {} if metadata is None else metadata
        bbox = self.tilegrid.extent(tilecoord, self.border)
        size = tilecoord.n * self.tilegrid.tile_size + 2 * self.border
        params = self.params.copy()
        for k, value in metadata.items():
            if k.startswith("dimension_"):
                params[k[len("dimension_") :]] = value
        params["BBOX"] = f"{bbox[0]:f},{bbox[1]:f},{bbox[2]:f},{bbox[3]:f}"
        params["WIDTH"] = str(size)
        params["HEIGHT"] = str(size)
        return self.url + "?" + urlencode(params)

    def tilecoord(self, filename: str) -> TileCoord:
        raise NotSupportedOperation
