# FIXME port to requests  # pylint: disable=fixme
# FIXME rename url1 and url2 to url when pyflakes grows a second brain cell  # pylint: disable=fixme
# https://github.com/mapbox/TileJSON

import json
import mimetypes
import os.path
import re
from typing import Any, ClassVar
from urllib.parse import urlparse

from urllib2 import urlopen  # pylint: disable=import-error

from tilecloud import BoundingPyramid, NotSupportedOperation, Tile
from tilecloud.layout.template import TemplateTileLayout
from tilecloud.store.url import URLTileStore


class TileJSONTileStore(URLTileStore):
    """A tile store for tiles in JSON data."""

    KEYS: ClassVar[list[str]] = [
        "name",
        "description",
        "version",
        "attribution",
        "template",
        "legend",
        "center",
    ]

    def __init__(self, tile_json: str, urls_key: str = "tiles", **kwargs: Any) -> None:
        # FIXME schema  # pylint: disable=fixme
        # FIXME version 1.0.0 support  # pylint: disable=fixme
        tile = json.loads(tile_json)
        assert "tiles" in tile
        assert isinstance(tile["tiles"], list)
        assert len(tile["tiles"]) > 0
        for key in self.KEYS:
            kwargs.setdefault(key, tile.get(key))
        if "bounding_pyramid" not in kwargs:
            zmin, zmax = tile.get("minzoom", 0), tile.get("maxzoom", 22)
            if "bounds" in tile:
                lonmin, latmin, lonmax, latmax = tile["bounds"]
                bounding_pyramid = BoundingPyramid.from_wgs84(  # type: ignore[attr-defined] # pylint: disable=no-member
                    zmin,
                    zmax,
                    lonmin,
                    lonmax,
                    latmin,
                    latmax,
                )
            else:
                bounding_pyramid = BoundingPyramid.full(zmin, zmax)
            kwargs["bounding_pyramid"] = bounding_pyramid
        urls = tile[urls_key]
        if "content_type" not in kwargs:
            exts = {os.path.splitext(urlparse(url1).path)[1] for url1 in urls}
            content_types = {mimetypes.types_map.get(ext) for ext in exts}
            assert len(content_types) == 1
            kwargs["content_type"] = content_types.pop()
        templates = [re.sub(r"\{([xyz])\}", lambda m: f"%({m.group(1)!s})d", url2) for url2 in urls]
        tilelayouts = map(TemplateTileLayout, templates)
        URLTileStore.__init__(self, tilelayouts, **kwargs)

    @classmethod
    def from_url(cls, url: str) -> Any:
        return cls(urlopen(url).read())  # nosec

    def delete_one(self, tile: Tile) -> Tile:
        raise NotSupportedOperation
