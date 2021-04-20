from collections import deque
from typing import Callable, Deque, Iterable, Iterator, Optional, Tuple

from tilecloud import Tile, TileGrid, TileStore
from tilecloud.grid.quad import QuadTileGrid


class RenderingTheWorldTileStore(TileStore):
    """http://mapbox.com/blog/rendering-the-world/"""

    def __init__(
        self,
        subdivide: Callable[[Tile], Iterable[Tile]],
        tilegrid: Optional[TileGrid] = None,
        queue: Optional[Deque[Tile]] = None,
        seeds: Tuple[Tile, ...] = (),
    ):
        super(RenderingTheWorldTileStore, self).__init__()
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
