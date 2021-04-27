import errno
import os
import os.path
from typing import Any, Iterator, Optional

from tilecloud import Tile, TileLayout, TileStore


class FilesystemTileStore(TileStore):
    """Tiles stored in a filesystem"""

    def __init__(self, tilelayout: TileLayout, **kwargs: Any):
        TileStore.__init__(self, **kwargs)
        assert tilelayout is not None
        self.tilelayout = tilelayout

    def delete_one(self, tile: Tile) -> Tile:
        try:
            filename = self.tilelayout.filename(tile.tilecoord, tile.metadata)
        except Exception as e:
            tile.error = e
            return tile
        if os.path.exists(filename):
            os.remove(filename)
        return tile

    def get_all(self) -> Iterator[Tile]:
        for tile in self.list():
            with open(tile.path, "rb") as file:  # type: ignore
                tile.data = file.read()
            yield tile

    def get_one(self, tile: Tile) -> Optional[Tile]:
        try:
            filename = self.tilelayout.filename(tile.tilecoord, tile.metadata)
        except Exception as e:
            tile.error = e
            return tile
        try:
            with open(filename, "rb") as file:
                tile.data = file.read()
            if self.content_type is not None:
                tile.content_type = self.content_type
            return tile
        except IOError as e:
            if e.errno == errno.ENOENT:
                return None
            else:
                raise

    def list(self) -> Iterator[Tile]:
        top = getattr(self.tilelayout, "prefix", ".")
        for dirpath, _, filenames in os.walk(top):
            for filename in filenames:
                path = os.path.join(dirpath, filename)
                tilecoord = self.tilelayout.tilecoord(path)
                if tilecoord:
                    yield Tile(tilecoord, path=path)

    def put_one(self, tile: Tile) -> Tile:
        assert isinstance(tile.data, bytes)
        try:
            filename = self.tilelayout.filename(tile.tilecoord, tile.metadata)
        except Exception as e:
            tile.error = e
            return tile
        dirname = os.path.dirname(filename)
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        with open(filename, "wb") as file:
            file.write(tile.data)
        return tile
