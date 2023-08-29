from collections.abc import Iterator
from typing import Any, Optional

from tilecloud import NotSupportedOperation, Tile, TileStore


class FindFirstTileStore(TileStore):
    def __init__(self, tilestores: Iterator[TileStore], **kwargs: Any):
        TileStore.__init__(self, **kwargs)
        self.tilestores = tilestores

    def get_one(self, tile: Tile) -> Optional[Tile]:
        return next(filter(None, (store.get_one(tile) for store in self.tilestores)), None)

    def put_one(self, tile: Tile) -> Tile:
        raise NotSupportedOperation()

    def delete_one(self, tile: Tile) -> Tile:
        raise NotSupportedOperation()
