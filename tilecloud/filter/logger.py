import logging
from typing import Any, Optional

from tilecloud import Tile


class Logger:
    def __init__(self, logger: logging.Logger, level: int, msgformat: str, *args: Any, **kwargs: Any):
        self.logger = logger
        self.level = level
        self.msgformat = msgformat
        self.args = args
        self.kwargs = kwargs

    def __call__(self, tile: Optional[Tile]) -> Optional[Tile]:
        if tile is not None:
            variables = {}
            variables.update(tile.__dict2__)
            variables.update(tile.tilecoord.__dict__)
            self.logger.log(self.level, self.msgformat, variables, *self.args, **self.kwargs)
        return tile

    def __str__(self) -> str:
        return f"{self.logger.name}({self.level},  {self.msgformat})"

    def __repr__(self) -> str:
        return self.__str__()
