from tilecloud import TileStore


class SearchUpTileStore(TileStore):

    def __init__(self, tile_store):
        self.tile_store = tile_store

    def get_one(self, tile):
        while tile:
            if tile in self.tile_store:
                return tile
            tile = tile.parent()
        return None
