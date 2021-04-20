from typing import Optional

from tilecloud import Tile, TileGrid, TileStore


class SearchUpTileStore(TileStore):
    def __init__(self, tilestore: TileStore, tilegrid: TileGrid):
        super(SearchUpTileStore, self).__init__()
        self.tilestore = tilestore
        self.tilegrid = tilegrid

    def get_one(self, tile: Tile) -> Optional[Tile]:
        if not tile:
            return None
        test_tile = Tile(tile.tilecoord)
        while test_tile.tilecoord:
            if test_tile in self.tilestore:
                tmp_tilecoord = tile.tilecoord
                tile.tilecoord = test_tile.tilecoord
                new_tile = self.tilestore.get_one(tile)
                if new_tile is not None:
                    new_tile.tilecoord = tmp_tilecoord
                return new_tile
            else:
                tilecoord = self.tilegrid.parent(test_tile.tilecoord)
                assert tilecoord is not None
                test_tile.tilecoord = tilecoord
        return None
