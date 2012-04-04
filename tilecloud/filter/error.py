from tilecloud.filter.logger import Logger


class TooManyErrors(RuntimeError):
    pass


class CollectErrors(object):
    """Save tiles with errors in an attribute called errors"""

    def __init__(self):
        self.errors = []

    def __call__(self, tile):
        if tile and tile.error:
            self.errors.append(tile)
        return tile


class DropErrors(object):
    """Drop all tiles with errors"""

    def __call__(self, tile):
        if not tile or tile.error:
            return None
        else:
            return tile


class LogErrors(Logger):
    """Log all tiles with errors"""

    def __call__(self, tile):
        if tile and tile.error:
            Logger.__call__(self, tile)
        return tile


class MaximumConsecutiveErrors(object):
    """Raise a TooManyErrors exception when there are max_consecutive_errors consecutive errors"""

    def __init__(self, max_consecutive_errors):
        self.max_consecutive_errors = max_consecutive_errors
        self.consecutive_errors = 0

    def __call__(self, tile):
        if tile.error:
            self.consecutive_errors += 1
            if self.consecutive_errors > self.max_consecutive_errors:
                raise TooManyErrors
        else:
            self.consecutive_errors = 0
        return tile


class MaximumErrorRate(object):
    """Raise a TooManyErrors exception when the total error rate exceeds max_error_rate"""

    def __init__(self, max_error_rate, min_tiles=8):
        self.max_error_rate = max_error_rate
        self.min_tiles = min_tiles
        self.tile_count = 0
        self.error_count = 0

    def __call__(self, tile):
        self.tile_count += 1
        if tile and tile.error:
            self.error_count += 1
            if self.tile_count >= self.min_tiles and self.error_count >= self.max_error_rate * self.count:
                raise TooManyErrors
        return tile


class MaximumErrors(object):
    """Raise a TooManyErrors exception when a number of errors is reached"""

    def __init__(self, max_errors):
        self.max_errors = max_errors
        self.error_count = 0

    def __call__(self, tile):
        if tile and tile.error:
            self.error_count += 1
            if self.error_count >= self.max_errors:
                raise TooManyErrors
        return tile
