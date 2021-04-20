from typing import Tuple

from tilecloud import TileStore


class NullTileStore(TileStore):
    """A TileStore that does nothing"""

    def __contains__(self, tile: Tile) -> bool:
        return False

    @staticmethod
    def delete_one(tile: Tile) -> Tile:
        return tile

    @staticmethod
    def get_one(tile: Tile) -> Tile:
        return tile

    @staticmethod
    def list() -> Tuple[()]:
        return ()

    @staticmethod
    def put_one(tile: Tile) -> Tile:
        return tile
