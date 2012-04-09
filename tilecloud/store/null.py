from tilecloud import TileStore


class NullTileStore(TileStore):
    """A TileStore that does nothing"""

    def __contains__(self, tile):
        return False

    def delete_one(self, tile):
        return tile

    def get_one(self, tile):
        return tile

    def list(self):
        return ()

    def put_one(self, tile):
        return tile
