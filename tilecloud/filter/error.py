"""
This module includes filters for dealing with errors in tiles.
"""
from tilecloud.filter.logger import Logger


class CollectErrors(object):
    """
    Create a filter for collecting tiles with errors in an attribute
    called ``errors``.
    """

    def __init__(self):
        self.errors = []

    def __call__(self, tile):
        if tile and tile.error:
            self.errors.append(tile)
        return tile


class DropErrors(object):
    """
    Create a filter for dropping all tiles with errors.
    """

    def __call__(self, tile):
        if not tile or tile.error:
            return None
        else:
            return tile


class LogErrors(Logger):
    """
    Create a filter for logging all tiles with errors.
    """

    def __call__(self, tile):
        if tile and tile.error:
            Logger.__call__(self, tile)
        return tile


class MaximumConsecutiveErrors(object):
    """
    Create a filter that raises a :class:`TooManyErrors` exception
    when there are ``max_consecutive_errors`` consecutive errors.

    :param max_consecutive_errors:
        The max number of permitted consecutive errors. Once
        exceeded a :class:`TooManyErrors` exception is raised.
    """

    def __init__(self, max_consecutive_errors):
        self.max_consecutive_errors = max_consecutive_errors
        self.consecutive_errors = 0

    def __call__(self, tile):
        if tile and tile.error:
            self.consecutive_errors += 1
            if self.consecutive_errors > self.max_consecutive_errors:
                raise TooManyErrors
        else:
            self.consecutive_errors = 0
        return tile


class MaximumErrorRate(object):
    """
    Create a filter that raises a :class:`TooManyErrors` exception
    when the total error rate exceeds ``max_error_rate``.

    :param max_error_rate:
       The maximum error rate. Once exceeded a :class:`TooManyErrors`
       exception is raised.
    :param min_tiles:
       The minimum number of received tiles before a :class:`TooManyErrors`
       exception can be raised. Defaults to 8.
    """

    def __init__(self, max_error_rate, min_tiles=8):
        self.max_error_rate = max_error_rate
        self.min_tiles = min_tiles
        self.tile_count = 0
        self.error_count = 0

    def __call__(self, tile):
        self.tile_count += 1
        if tile and tile.error:
            self.error_count += 1
            if self.tile_count >= self.min_tiles and \
               self.error_count >= self.max_error_rate * self.tile_count:
                raise TooManyErrors
        return tile


class MaximumErrors(object):
    """
    Create a filter that raises a :class:`TooManyErrors` exception when
    a number of errors is reached.

    :param max_errors:
        The maximum number of errors. Once exceeded a :class:`TooManyErrors`
        exception is raised.
    """

    def __init__(self, max_errors):
        self.max_errors = max_errors
        self.error_count = 0

    def __call__(self, tile):
        if tile and tile.error:
            self.error_count += 1
            if self.error_count >= self.max_errors:
                raise TooManyErrors
        return tile


class TooManyErrors(RuntimeError):
    """TooManyErrors exception class."""
    pass
