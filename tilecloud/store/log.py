import re
from collections.abc import Iterator
from typing import IO, Any

from tilecloud import NotSupportedOperation, Tile, TileStore
from tilecloud.layout.re_ import RETileLayout


class LogTileStore(TileStore):
    """Generates all tile coordinates matching the specified layout from file."""

    def __init__(self, tilelayout: RETileLayout, file: IO[str], **kwargs: Any) -> None:
        TileStore.__init__(self, **kwargs)
        self.tilelayout = tilelayout
        self.file = file

    def get_one(self, tile: Tile) -> Tile:
        tile.data = None
        return tile

    def list(self) -> Iterator[Tile]:
        # FIXME warn that this consumes file  # pylint: disable=fixme
        filename_re = re.compile(self.tilelayout.pattern)
        for line in self.file:
            match = filename_re.search(line)
            if match:
                yield Tile(self.tilelayout.tilecoord(match.group()), line=line)

    def put_one(self, tile: Tile) -> Tile:
        self.file.write(self.tilelayout.filename(tile.tilecoord, tile.metadata) + "\n")
        return tile

    def delete_one(self, tile: Tile) -> Tile:
        raise NotSupportedOperation
