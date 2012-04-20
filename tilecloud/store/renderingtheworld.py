from collections import deque

from tilecloud import Tile, TileStore


class RenderingTheWorldTileStore(TileStore):
    """http://mapbox.com/blog/rendering-the-world/"""

    def __init__(self, subdivide, queue=None, seeds=()):
        self.subdivide = subdivide
        self.queue = queue
        if self.queue is None:
            self.queue = deque()
        for seed in seeds:
            self.queue.append(seed)

    def list(self):
        try:
            while True:
                yield self.queue.popleft()
        except IndexError:
            pass

    def put_one(self, tile):
        if self.subdivide(tile):
            for tilecoord in tile.tilecoord.children():
                self.queue.append(Tile(tilecoord))
        return tile
