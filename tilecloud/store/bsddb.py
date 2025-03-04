from collections.abc import Iterator
from typing import Any

import bsddb3 as bsddb  # pylint: disable=import-error

from tilecloud import Tile, TileCoord, TileStore


class BSDDBTileStore(TileStore):
    """Tiles stored in a BSDDB database."""

    def __init__(self, db: bsddb.DB, **kwargs: Any) -> None:
        self.db = db  # pylint: disable=invalid-name
        TileStore.__init__(self, **kwargs)

    def __contains__(self, tile: Tile) -> bool:
        return tile is not None and str(tile.tilecoord) in self.db

    def __len__(self) -> int:
        return len(self.db)

    def delete_one(self, tile: Tile) -> Tile:
        key = str(tile.tilecoord).encode("utf-8")
        if key in self.db:
            del self.db[key]
        return tile

    def get_all(self) -> Iterator[Tile]:
        for key, data in self.db.items():
            tile = Tile(TileCoord.from_string(key), content_type=self.content_type, data=data)
            yield tile

    def get_one(self, tile: Tile) -> Tile | None:
        try:
            tile.content_type = self.content_type
            tile.data = self.db[str(tile.tilecoord).encode("utf-8")]
            return tile
        except KeyError:
            return None

    def list(self) -> Iterator[Tile]:
        return (Tile(TileCoord.from_string(s)) for s in self.db)

    def put_one(self, tile: Tile) -> Tile:
        self.db[str(tile.tilecoord).encode("utf-8")] = getattr(tile, "data", "")
        return tile
