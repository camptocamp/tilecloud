from collections.abc import Iterator
from typing import Any

from tilecloud import Tile, TileStore


class DictTileStore(TileStore):
    """Tiles stored in a dictionary."""

    def __init__(self, tiles: Any | None = None, **kwargs: Any) -> None:
        self.tiles = tiles or {}
        TileStore.__init__(self, **kwargs)

    def __contains__(self, tile: Tile) -> bool:
        return tile is not None and tile.tilecoord in self.tiles

    def __len__(self) -> int:
        return len(self.tiles)

    def delete_one(self, tile: Tile) -> Tile:
        del self.tiles[tile.tilecoord]
        return tile

    def get_one(self, tile: Tile) -> Tile | None:
        if tile and tile.tilecoord in self.tiles:
            tile.__dict__.update(self.tiles[tile.tilecoord])
            return tile
        return None

    def list(self) -> Iterator[Tile]:
        for tilecoord in self.tiles:
            yield Tile(tilecoord)

    def put_one(self, tile: Tile) -> Tile:
        if tile:
            self.tiles[tile.tilecoord] = tile.__dict__
        return tile
