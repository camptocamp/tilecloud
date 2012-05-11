from tilecloud import Tile, TileStore


class SearchUpTileStore(TileStore):

    def __init__(self, tilestore, tile_structure):
        self.tilestore = tilestore
        self.tile_structure = tile_structure

    def get_one(self, tile):
        if not tile:
            return None
        test_tile = Tile(tile.tilecoord)
        while test_tile.tilecoord:
            if test_tile in self.tilestore:
                tmp_tilecoord = tile.tilecoord
                tile.tilecoord = test_tile.tilecoord
                tile = self.tilestore.get_one(tile)
                if tile:
                    tile.tilecoord = tmp_tilecoord
                return tile
            else:
                test_tile.tilecoord = self.tile_structure.parent(test_tile.tilecoord)
        return None
