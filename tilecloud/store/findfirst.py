from collections.abc import Iterator
from typing import Any

from tilecloud import NotSupportedOperation, Tile, TileStore


class FindFirstTileStore(TileStore):
    """A tile store used to get the first tile."""

    def __init__(self, tilestores: Iterator[TileStore], **kwargs: Any) -> None:
        TileStore.__init__(self, **kwargs)
        self.tilestores = tilestores

    def get_one(self, tile: Tile) -> Tile | None:
        return next(filter(None, (store.get_one(tile) for store in self.tilestores)), None)

    def put_one(self, tile: Tile) -> Tile:
        raise NotSupportedOperation

    def delete_one(self, tile: Tile) -> Tile:
        raise NotSupportedOperation
