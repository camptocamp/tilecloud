from itertools import ifilter

from tilecloud import TileStore


class FindFirstTileStore(TileStore):

    def __init__(self, tile_stores, **kwargs):
        TileStore.__init__(self, **kwargs)
        self.tile_stores = tile_stores

    def get_one(self, tile):
        return next(ifilter(None,
                            (store.get_one(tile)
                                for store in self.tile_stores)),
                    None)
