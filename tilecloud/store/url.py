import logging
from collections.abc import Iterable
from typing import Any

import requests

from tilecloud import NotSupportedOperation, Tile, TileLayout, TileStore

_LOGGER = logging.getLogger(__name__)


class URLTileStore(TileStore):
    """A tile store that reads and writes tiles from a formatted URL."""

    def __init__(
        self,
        tilelayouts: Iterable[TileLayout],
        headers: Any | None = None,
        allows_no_contenttype: bool = False,
        **kwargs: Any,
    ) -> None:
        TileStore.__init__(self, **kwargs)
        self.allows_no_contenttype = allows_no_contenttype
        self.tilelayouts = tuple(tilelayouts)
        self.session = requests.session()
        if headers is not None:
            self.session.headers.update(headers)

    def get_one(self, tile: Tile) -> Tile | None:
        if tile is None:
            return None
        if self.bounding_pyramid is not None and tile.tilecoord not in self.bounding_pyramid:
            return None
        tilelayout = self.tilelayouts[hash(tile.tilecoord) % len(self.tilelayouts)]
        try:
            url = tilelayout.filename(tile.tilecoord, tile.metadata)
        except Exception as exception:  # pylint: disable=broad-except
            _LOGGER.warning("Error while getting tile %s", tile, exc_info=True)
            tile.error = exception
            return tile

        _LOGGER.info("GET %s", url)
        try:
            response = self.session.get(url)
            if response.status_code in (404, 204):
                _LOGGER.debug("Got empty tile from %s: %s", url, response.status_code)
                return None
            tile.content_encoding = response.headers.get("Content-Encoding")
            tile.content_type = response.headers.get("Content-Type")
            if response.status_code < 300:
                if response.status_code != 200:
                    tile.error = (
                        f"URL: {url}\nUnsupported status code {response.status_code}: {response.reason}"
                    )
                if tile.content_type:
                    if tile.content_type.startswith("image/"):
                        tile.data = response.content
                    else:
                        tile.error = f"URL: {url}\n{response.text}"
                elif self.allows_no_contenttype:
                    tile.data = response.content
                else:
                    tile.error = f"URL: {url}\nThe Content-Type header is missing"

            else:
                tile.error = f"URL: {url}\n{response.status_code}: {response.reason}\n{response.text}"
        except requests.exceptions.RequestException as exception:
            _LOGGER.warning("Error while getting tile %s", tile, exc_info=True)
            tile.error = exception
        return tile

    def put_one(self, tile: Tile) -> Tile:
        raise NotSupportedOperation

    def delete_one(self, tile: Tile) -> Tile:
        raise NotSupportedOperation
