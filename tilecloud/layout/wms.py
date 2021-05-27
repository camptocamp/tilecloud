from typing import Any, Dict, Optional
from urllib.parse import urlencode

from tilecloud import TileCoord, TileGrid, TileLayout


class WMSTileLayout(TileLayout):
    def __init__(
        self,
        url: str,
        layers: str,
        srs: str,
        format: str,
        tilegrid: TileGrid,
        border: int = 0,
        params: Optional[Dict[str, str]] = None,
    ) -> None:
        if params is None:
            params = {}
        self.tilegrid = tilegrid
        self.url = url
        self.border = border
        self.params = {
            "LAYERS": layers,
            "FORMAT": format,
            "TRANSPARENT": "TRUE" if format == "image/png" else "FALSE",
            "SERVICE": "WMS",
            "VERSION": "1.1.1",
            "REQUEST": "GetMap",
            "STYLES": "",
            "SRS": srs,
        }
        self.params.update(params)
        if params.get("FILTER", None) is not None:
            self.params["FILTER"] = params["FILTER"].format(**params)

    def filename(self, tilecoord: TileCoord, metadata: Optional[Any] = None) -> str:
        metadata = {} if metadata is None else metadata
        bbox = self.tilegrid.extent(tilecoord, self.border)
        size = tilecoord.n * self.tilegrid.tile_size + 2 * self.border
        params = self.params.copy()
        for k, v in metadata.items():
            if k.startswith("dimension_"):
                params[k[len("dimension_") :]] = v
        params["BBOX"] = "{0:f},{1:f},{2:f},{3:f}".format(*bbox)
        params["WIDTH"] = str(size)
        params["HEIGHT"] = str(size)
        return self.url + "?" + urlencode(params)
