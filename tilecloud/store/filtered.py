from collections.abc import Callable
from functools import reduce
from typing import Any

from tilecloud import NotSupportedOperation, Tile, TileStore


class FilteredTileStore(TileStore):
    """A tile store that filter the tiles."""

    def __init__(
        self,
        tilestore: TileStore,
        filters: list[Callable[[Tile | None], Tile]],
        **kwargs: Any,
    ) -> None:
        TileStore.__init__(self, **kwargs)
        self.tilestore = tilestore
        self.filters = filters

    def get_one(self, tile: Tile) -> Tile | None:
        def reduce_function(tile: Tile | None, filter_pattern: Callable[[Tile | None], Tile]) -> Tile | None:
            return filter_pattern(tile)

        return reduce(reduce_function, self.filters, self.tilestore.get_one(tile))

    def put_one(self, tile: Tile) -> Tile:
        raise NotSupportedOperation

    def delete_one(self, tile: Tile) -> Tile:
        raise NotSupportedOperation
