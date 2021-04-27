import time
from typing import Optional

from tilecloud import Tile


class RateLimit:
    def __init__(self, rate: float):
        self.rate = rate
        self.count = 0
        self.start: Optional[float] = None

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
