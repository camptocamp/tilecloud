from typing import Any, Iterator, Optional

from tilecloud import Tile, TileStore


class DictTileStore(TileStore):
    def __init__(self, tiles: Optional[Any] = None, **kwargs: Any) -> None:
        self.tiles = tiles or {}
        TileStore.__init__(self, **kwargs)

    def __contains__(self, tile: Tile) -> bool:
        return tile is not None and tile.tilecoord in self.tiles

    def __len__(self) -> int:
        return len(self.tiles)

    def delete_one(self, tile: Tile) -> Tile:
        del self.tiles[tile.tilecoord]
        return tile

    def get_one(self, tile: Tile) -> Optional[Tile]:
        if tile and tile.tilecoord in self.tiles:
            tile.__dict__.update(self.tiles[tile.tilecoord])
            return tile
        else:
            return None

    def list(self) -> Iterator[Tile]:
        for tilecoord in self.tiles.keys():
            yield Tile(tilecoord)

    def put_one(self, tile: Tile) -> Tile:
        if tile:
            self.tiles[tile.tilecoord] = tile.__dict__
        return tile
