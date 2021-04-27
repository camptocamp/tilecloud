import math
from typing import Callable, Dict, Optional

from c2cwsgiutils import stats

from tilecloud import Tile


class Statistics:
    def __init__(self, format: str = "%f"):
        self.format = format
        self.n = 0
        self.sum = 0.0
        self.sum_of_squares = 0.0
        self.minimum: Optional[float] = None
        self.maximum: Optional[float] = None

    def add(self, x: float) -> None:
        self.n += 1
        self.sum += x
        self.sum_of_squares += x * x
        self.minimum = x if self.minimum is None else min(self.minimum, x)
        self.maximum = x if self.maximum is None else max(self.maximum, x)

    def __str__(self) -> str:
        result = []
        if self.n:
            result.append("/".join(self.format % value for value in (self.minimum, self.mean, self.maximum)))
        result.append("(n={0:d})".format(self.n))
        return " ".join(result)

    @property
    def mean(self) -> Optional[float]:
        return self.sum / self.n if self.n else None

    @property
    def variance(self) -> float:
        return self.sum_of_squares / self.n - (self.sum / self.n) ** 2

    @property
    def standard_deviation(self) -> float:
        return math.sqrt(self.variance)


class Benchmark:
    def __init__(self, attr: str = "benchmark"):
        self.attr = attr
        self.statisticss: Dict[str, Statistics] = {}

    def sample(self, key: Optional[str] = None) -> Callable[[Tile], Tile]:
        if key:
            if key in self.statisticss:
                statistics: Optional[Statistics] = self.statisticss[key]
            else:
                statistics = Statistics("%.3fs")
                self.statisticss[key] = statistics
        else:
            statistics = None

        def callback(tile: Tile) -> Tile:
            if tile:
                if hasattr(tile, self.attr):
                    timer = getattr(tile, self.attr)
                    delta_t = timer.stop()
                    if statistics:
                        statistics.add(delta_t)
                else:
                    setattr(tile, self.attr, stats.timer([key]))
            return tile

        return callback


class StatsdCountTiles:
    def __call__(self, tile: Tile) -> Tile:
        if tile:
            stats.increment_counter(["tiles"])
        return tile


class StatsdCountErrors:
    def __call__(self, tile: Tile) -> Tile:
        if tile and tile.error:
            stats.increment_counter(["errors"])
        return tile
