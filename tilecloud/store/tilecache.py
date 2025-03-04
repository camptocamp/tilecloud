from typing import Any

from tilecloud.layout.tilecache import TileCacheDiskLayout
from tilecloud.layout.wrapped import WrappedTileLayout
from tilecloud.store.filesystem import FilesystemTileStore


class TileCacheDiskTileStore(FilesystemTileStore):
    """A tile store that reads and writes tiles from a TileCache disk layout."""

    def __init__(self, prefix: str = "", suffix: str = "", **kwargs: Any) -> None:
        tilelayout = WrappedTileLayout(TileCacheDiskLayout(), prefix=prefix, suffix=suffix)
        FilesystemTileStore.__init__(self, tilelayout, **kwargs)
