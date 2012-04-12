import logging
from urllib2 import HTTPError, Request, urlopen

from tilecloud import TileStore


logger = logging.getLogger(__name__)


class URLTileStore(TileStore):

    def __init__(self, tile_layouts, headers=None, **kwargs):
        TileStore.__init__(self, **kwargs)
        self.tile_layouts = tuple(tile_layouts)
        self.headers = headers or {}

    def get_one(self, tile):
        if self.bounding_pyramid is not None:
            if tile.tilecoord not in self.bounding_pyramid:
                return None
        tile_layout = self.tile_layouts[hash(tile.tilecoord) %
                                        len(self.tile_layouts)]
        url = tile_layout.filename(tile.tilecoord)
        request = Request(url, headers=self.headers)
        try:
            logger.debug('GET %s' % (url,))
            response = urlopen(request)
            info = response.info()
            if 'Content-Encoding' in info:
                tile.content_encoding = info['Content-Encoding']
            if 'Content-Type' in info:
                tile.content_type = info['Content-Type']
            tile.data = response.read()
        except HTTPError as exc:
            tile.error = exc
        return tile
