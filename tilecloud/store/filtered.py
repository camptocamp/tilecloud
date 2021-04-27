from functools import reduce
from typing import Any, Callable, List, Optional

from tilecloud import Tile, TileStore


class FilteredTileStore(TileStore):
    def __init__(self, tilestore: TileStore, filters: List[Callable[[Optional[Tile]], Tile]], **kwargs: Any):
        TileStore.__init__(self, **kwargs)
        self.tilestore = tilestore
        self.filters = filters

    def get_one(self, tile: Tile) -> Optional[Tile]:
        def reduce_function(tile: Optional[Tile], filter: Callable[[Optional[Tile]], Tile]) -> Optional[Tile]:
            return filter(tile)

        return reduce(reduce_function, self.filters, self.tilestore.get_one(tile))
