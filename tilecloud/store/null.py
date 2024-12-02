from collections.abc import Iterable

from tilecloud import Tile, TileStore


class NullTileStore(TileStore):
    """A TileStore that does nothing."""

    def __contains__(self, tile: Tile) -> bool:
        return False

    def delete_one(self, tile: Tile) -> Tile:
        return tile

    def get_one(self, tile: Tile) -> Tile:
        return tile

    def list(self) -> Iterable[Tile]:
        return ()

    def put_one(self, tile: Tile) -> Tile:
        return tile
