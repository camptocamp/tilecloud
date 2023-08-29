from functools import reduce
from typing import Any, Callable, Optional

from tilecloud import NotSupportedOperation, Tile, TileStore


class FilteredTileStore(TileStore):
    def __init__(self, tilestore: TileStore, filters: list[Callable[[Optional[Tile]], Tile]], **kwargs: Any):
        TileStore.__init__(self, **kwargs)
        self.tilestore = tilestore
        self.filters = filters

    def get_one(self, tile: Tile) -> Optional[Tile]:
        def reduce_function(
            tile: Optional[Tile], filter_pattern: Callable[[Optional[Tile]], Tile]
        ) -> Optional[Tile]:
            return filter_pattern(tile)

        return reduce(reduce_function, self.filters, self.tilestore.get_one(tile))

    def put_one(self, tile: Tile) -> Tile:
        raise NotSupportedOperation()

    def delete_one(self, tile: Tile) -> Tile:
        raise NotSupportedOperation()
