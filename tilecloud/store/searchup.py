from tilecloud import NotSupportedOperation, Tile, TileGrid, TileStore


class SearchUpTileStore(TileStore):
    """A tile store that searches up the tile grid for a tile."""

    def __init__(self, tilestore: TileStore, tilegrid: TileGrid) -> None:
        super().__init__()
        self.tilestore = tilestore
        self.tilegrid = tilegrid

    def get_one(self, tile: Tile) -> Tile | None:
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
            tilecoord = self.tilegrid.parent(test_tile.tilecoord)
            assert tilecoord is not None
            test_tile.tilecoord = tilecoord
        return None

    def put_one(self, tile: Tile) -> Tile:
        raise NotSupportedOperation

    def delete_one(self, tile: Tile) -> Tile:
        raise NotSupportedOperation
