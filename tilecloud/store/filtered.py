from six.moves import reduce

from tilecloud import TileStore


class FilteredTileStore(TileStore):

    def __init__(self, tilestore, filters, **kwargs):
        TileStore.__init__(self, **kwargs)
        self.tilestore = tilestore
        self.filters = filters

    def get_one(self, tile):
        return reduce(lambda tile, filter: filter(tile),
                      self.filters,
                      self.tilestore.get_one(tile))
