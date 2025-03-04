import time

from tilecloud import Tile


class RateLimit:
    """Rate limit the number of tiles per second."""

    def __init__(self, rate: float) -> None:
        self.rate = rate
        self.count = 0
        self.start: float | None = None

    def __call__(self, tile: Tile) -> Tile:
        if tile:
            if self.start is None:
                self.start = time.time()
            else:
                self.count += 1
                seconds = self.start + self.count / self.rate - time.time()
                if seconds > 0:
                    time.sleep(seconds)
        return tile
