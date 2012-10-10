from tilecloud.layout.tilecache import TileCacheDiskLayout
from tilecloud.layout.wrapped import WrappedTileLayout
from tilecloud.store.filesystem import FilesystemTileStore


class TileCacheDiskTileStore(FilesystemTileStore):

    def __init__(self, prefix='', suffix='', **kwargs):
        tilelayout = WrappedTileLayout(TileCacheDiskLayout(), prefix=prefix, suffix=suffix)
        FilesystemTileStore.__init__(self, tilelayout, **kwargs)
