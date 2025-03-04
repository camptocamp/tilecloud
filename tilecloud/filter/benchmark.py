import math
import time
from collections.abc import Callable

from prometheus_client import Counter

from tilecloud import Tile

_TILES_COUNTER = Counter("tilecloud_tiles", "Number of tiles")
_TILES_ERROR_COUINTER = Counter("tilecloud_tiles_errors", "Number of tiles in error")


class Statistics:
    """Compute statistics on a sequence of numbers."""

    def __init__(self, format_pattern: str = "%f") -> None:
        self.format = format_pattern
        self.n = 0  # pylint: disable=invalid-name
        self.sum = 0.0
        self.sum_of_squares = 0.0
        self.minimum: float | None = None
        self.maximum: float | None = None

    def add(self, x: float) -> None:  # pylint: disable=invalid-name
        self.n += 1
        self.sum += x
        self.sum_of_squares += x * x
        self.minimum = x if self.minimum is None else min(self.minimum, x)
        self.maximum = x if self.maximum is None else max(self.maximum, x)

    def __str__(self) -> str:
        result = []
        if self.n:
            result.append("/".join(self.format % value for value in (self.minimum, self.mean, self.maximum)))
        result.append(f"(n={self.n:d})")
        return " ".join(result)

    @property
    def mean(self) -> float | None:
        return self.sum / self.n if self.n else None

    @property
    def variance(self) -> float:
        return self.sum_of_squares / self.n - (self.sum / self.n) ** 2

    @property
    def standard_deviation(self) -> float:
        return math.sqrt(self.variance)


class Benchmark:
    """Create a filter for benchmarking tiles."""

    def __init__(self, attr: str = "benchmark") -> None:
        self.attr = attr
        self.statisticss: dict[str, Statistics] = {}

    def sample(self, key: str | None = None) -> Callable[[Tile], Tile]:
        if key:
            if key in self.statisticss:
                statistics: Statistics | None = self.statisticss[key]
            else:
                statistics = Statistics("%.3fs")
                self.statisticss[key] = statistics
        else:
            statistics = None

        def callback(tile: Tile) -> Tile:
            if tile:
                if hasattr(tile, self.attr):
                    start = getattr(tile, self.attr)
                    delta_t = time.perf_counter() - start
                    if statistics:
                        statistics.add(delta_t)
                else:
                    setattr(tile, self.attr, time.perf_counter())
            return tile

        return callback


class StatsCountTiles:
    """Create a filter for counting all tiles."""

    def __call__(self, tile: Tile) -> Tile:
        if tile:
            _TILES_COUNTER.inc()
        return tile


class StatsCountErrors:
    """Create a filter for counting all tiles with errors."""

    def __call__(self, tile: Tile) -> Tile:
        if tile and tile.error:
            _TILES_ERROR_COUINTER.inc()
        return tile
