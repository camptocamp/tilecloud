from tilecloud import TileStore



class FilteredTileStore(TileStore):

    def __init__(self, tile_store, filters, **kwargs):
        TileStore.__init__(self, **kwargs)
        self.tile_store = tile_store
        self.filters = filters

    def get_one(self, tile):
        return reduce(lambda tile, filter: filter(tile), self.filters, self.tile_store.get_one(tile))
