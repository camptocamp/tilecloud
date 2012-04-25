from itertools import imap

from tilecloud import Tile, TileCoord, TileStore


class BSDDBTileStore(TileStore):

    def __init__(self, db, **kwargs):
        self.db = db
        TileStore.__init__(self, **kwargs)

    def __contains__(self, tile):
        return tile and str(tile.tilecoord) in self.db

    def __len__(self):
        return len(self.db)

    def delete_one(self, tile):
        del self.db[str(tile.tilecoord)]
        return tile

    def get_all(self):
        for key, data in self.db.items():
            tile = Tile(TileCoord.from_string(key), content_type=self.content_type, data=data)
            yield tile

    def get_one(self, tile):
        try:
            tile.content_type = self.content_type
            tile.data = self.db[str(tile.tilecoord)]
            return tile
        except KeyError:
            return None

    def list(self):
        return imap(lambda s: Tile(TileCoord.from_string(s)), self.db.iterkeys())

    def put_one(self, tile):
        self.db[str(tile.tilecoord)] = getattr(tile, 'data', '')
        return tile
