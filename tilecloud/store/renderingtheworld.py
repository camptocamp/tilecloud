from collections import deque
from collections.abc import Iterator
from typing import Callable, Deque, Optional

from tilecloud import NotSupportedOperation, Tile, TileGrid, TileStore
from tilecloud.grid.quad import QuadTileGrid


class RenderingTheWorldTileStore(TileStore):
    """
    http://mapbox.com/blog/rendering-the-world/
    """

    def __init__(
        self,
        subdivide: Callable[[Tile], bool],
        tilegrid: Optional[TileGrid] = None,
        queue: Optional[Deque[Tile]] = None,
        seeds: tuple[Tile, ...] = (),
    ):
        super().__init__()
        self.subdivide = subdivide
        self.tilegrid = tilegrid
        if self.tilegrid is None:
            self.tilegrid = QuadTileGrid()
        if queue is None:
            queue = deque()
        self.queue = queue
        for seed in seeds:
            self.queue.append(seed)

    def list(self) -> Iterator[Tile]:
        try:
            while True:
                yield self.queue.popleft()
        except IndexError:
            pass

    def put_one(self, tile: Tile) -> Tile:
        if self.subdivide(tile):
            for tilecoord in self.tilegrid.children(tile.tilecoord):  # type: ignore
                self.queue.append(Tile(tilecoord))
        return tile

    def get_one(self, tile: Tile) -> Optional[Tile]:
        raise NotSupportedOperation()

    def delete_one(self, tile: Tile) -> Tile:
        raise NotSupportedOperation()
