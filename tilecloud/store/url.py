import logging
from typing import Any, Iterable, Optional

import requests

from tilecloud import Tile, TileLayout, TileStore

logger = logging.getLogger(__name__)


class URLTileStore(TileStore):
    def __init__(
        self,
        tilelayouts: Iterable[TileLayout],
        headers: Optional[Any] = None,
        allows_no_contenttype: bool = False,
        **kwargs: Any,
    ) -> None:
        TileStore.__init__(self, **kwargs)
        self.allows_no_contenttype = allows_no_contenttype
        self.tilelayouts = tuple(tilelayouts)
        self.session = requests.session()
        if headers is not None:
            self.session.headers.update(headers)

    def get_one(self, tile: Tile) -> Optional[Tile]:
        if tile is None:
            return None
        if self.bounding_pyramid is not None:
            if tile.tilecoord not in self.bounding_pyramid:
                return None
        tilelayout = self.tilelayouts[hash(tile.tilecoord) % len(self.tilelayouts)]
        try:
            url = tilelayout.filename(tile.tilecoord, tile.metadata)
        except Exception as e:
            tile.error = e
            return tile

        logger.info("GET %s", url)
        try:
            response = self.session.get(url)
            if response.status_code == 404 or response.status_code == 204:
                return None
            tile.content_encoding = response.headers.get("Content-Encoding")
            tile.content_type = response.headers.get("Content-Type")
            if response.status_code < 300:
                if response.status_code != 200:
                    tile.error = "Unsupportetd status code {}: {}".format(
                        response.status_code, response.reason
                    )
                if tile.content_type:
                    if tile.content_type.startswith("image/"):
                        tile.data = response.content
                    else:
                        tile.error = response.text
                else:
                    if self.allows_no_contenttype:
                        tile.data = response.content
                    else:
                        tile.error = "The Content-Type header is missing"

            else:
                tile.error = response.reason
        except requests.exceptions.RequestException as e:
            tile.error = e
        return tile
