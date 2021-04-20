from typing import Iterable

from tilecloud import Tile, TileStore


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
    def list() -> Iterable[Tile]:
        return ()

    @staticmethod
    def put_one(tile: Tile) -> Tile:
        return tile
