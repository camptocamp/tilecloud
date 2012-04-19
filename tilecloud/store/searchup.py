from tilecloud import Tile, TileStore


class SearchUpTileStore(TileStore):

    def __init__(self, tile_store):
        self.tile_store = tile_store

    def get_one(self, tile):
        if not tile:
            return None
        test_tile = Tile(tile.tilecoord)
        while test_tile.tilecoord:
            if test_tile in self.tile_store:
                tmp_tilecoord = tile.tilecoord
                tile.tilecoord = test_tile.tilecoord
                tile = self.tile_store.get_one(tile)
                if tile:
                    tile.tilecoord = tmp_tilecoord
                return tile
            else:
                test_tile.tilecoord = test_tile.tilecoord.parent()
        return None
