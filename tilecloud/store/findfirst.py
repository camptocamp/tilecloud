from typing import Any, Iterator, Optional

from tilecloud import Tile, TileStore


class FindFirstTileStore(TileStore):
    def __init__(self, tilestores: Iterator[TileStore], **kwargs: Any):
        TileStore.__init__(self, **kwargs)
        self.tilestores = tilestores

    def get_one(self, tile: Tile) -> Optional[Tile]:
        return next(filter(None, (store.get_one(tile) for store in self.tilestores)), None)
