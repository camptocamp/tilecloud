import logging
from typing import Any

from tilecloud import Tile


class Logger:
    def __init__(self, logger: logging.Logger, level: int, msgformat: str, *args: Any, **kwargs: Any):
        self.logger = logger
        self.level = level
        self.msgformat = msgformat
        self.args = args
        self.kwargs = kwargs

    def __call__(self, tile: Tile) -> Tile:
        if tile is not None:
            variables = dict()
            variables.update(tile.__dict2__)
            variables.update(tile.tilecoord.__dict__)
            self.logger.log(self.level, self.msgformat, variables, *self.args, **self.kwargs)
        return tile
