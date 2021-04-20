from typing import Any

from tilecloud.layout.tilecache import TileCacheDiskLayout
from tilecloud.layout.wrapped import WrappedTileLayout
from tilecloud.store.filesystem import FilesystemTileStore


class TileCacheDiskTileStore(FilesystemTileStore):
    def __init__(self, prefix: str = "", suffix: str = "", **kwargs: Any):
        tilelayout = WrappedTileLayout(TileCacheDiskLayout(), prefix=prefix, suffix=suffix)
        FilesystemTileStore.__init__(self, tilelayout, **kwargs)
