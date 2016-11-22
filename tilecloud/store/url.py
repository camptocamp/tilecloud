import logging
import requests
from tilecloud import TileStore


logger = logging.getLogger(__name__)


class URLTileStore(TileStore):

    def __init__(self, tilelayouts, headers=None, **kwargs):
        TileStore.__init__(self, **kwargs)
        self.tilelayouts = tuple(tilelayouts)
        self.session = requests.session()
        if headers is not None:
            self.session.headers.update(headers)

    def get_one(self, tile):
        if self.bounding_pyramid is not None:
            if tile.tilecoord not in self.bounding_pyramid:
                return None
        tilelayout = self.tilelayouts[hash(tile.tilecoord) %
                                      len(self.tilelayouts)]
        url = tilelayout.filename(tile.tilecoord)

        logger.info('GET {0!s}'.format(url))
        try:
            response = self.session.get(url)
            if response.status_code == 404:
                return None
            tile.content_encoding = response.headers.get('Content-Encoding')
            tile.content_type = response.headers.get('Content-Type')
            tile.data = response.content
        except requests.exceptions.RequestException as e:
            tile.error = e
        return tile
