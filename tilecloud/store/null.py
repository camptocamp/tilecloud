from tilecloud import TileStore


class NullTileStore(TileStore):
    """A TileStore that does nothing"""

    def __contains__(self, tile):
        return False

    @staticmethod
    def delete_one(tile):
        return tile

    @staticmethod
    def get_one(tile):
        return tile

    @staticmethod
    def list():
        return ()

    @staticmethod
    def put_one(tile):
        return tile
