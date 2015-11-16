from six import iterkeys

from tilecloud import Tile, TileStore


class DictTileStore(TileStore):

    def __init__(self, tiles=None, **kwargs):
        self.tiles = tiles or {}
        TileStore.__init__(self, **kwargs)

    def __contains__(self, tile):
        return tile and tile.tilecoord in self.tiles

    def __len__(self):
        return len(self.tiles)

    def delete_one(self, tile):
        del self.tiles[tile.tilecoord]
        return tile

    def get_one(self, tile):
        if tile and tile.tilecoord in self.tiles:
            tile.__dict__.update(self.tiles[tile.tilecoord])
            return tile
        else:
            return None

    def list(self):
        for tilecoord in iterkeys(self.tiles):
            yield Tile(tilecoord)

    def put_one(self, tile):
        if tile:
            self.tiles[tile.tilecoord] = tile.__dict__
        return tile
