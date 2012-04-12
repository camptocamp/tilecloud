from collections import deque
import logging

from tilecloud import Tile, TileStore


class RenderingTheWorldTileStore(TileStore):
    """http://mapbox.com/blog/rendering-the-world/"""

    def __init__(self, subdivide, queue=None, seed=None):
        self.subdivide = subdivide
        self.queue = queue
        if self.queue is None:
            self.queue = deque()
        if seed is not None:
            self.queue.append(seed)

    def list(self):
        try:
            while True:
                yield self.queue.popleft()
        except IndexError:
            pass

    def put_one(self, tile):
        if self.subdivide(tile):
            for tilecoord in tile.tilecoord.subdivide():
                self.queue.append(Tile(tilecoord))
        return tile
