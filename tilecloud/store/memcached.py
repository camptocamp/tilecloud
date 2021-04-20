from typing import Any, Optional

from tilecloud import Tile, TileLayout, TileStore
import tilecloud.lib.memcached


class MemcachedTileStore(TileStore):
    def __init__(
        self,
        client: tilecloud.lib.memcached.MemcachedClient,
        tilelayout: TileLayout,
        flags: int = 0,
        exptime: int = 0,
        **kwargs: Any,
    ):
        TileStore.__init__(self, **kwargs)
        self.client = client
        self.tilelayout = tilelayout
        self.flags = flags
        self.exptime = exptime

    def __contains__(self, tile: Tile) -> bool:
        flags, _, _ = self.client.get(self.tilelayout.filename(tile.tilecoord, tile.metadata))
        return flags is not None

    def get_one(self, tile: Tile) -> Optional[Tile]:
        flags, value, cas = self.client.get(self.tilelayout.filename(tile.tilecoord, tile.metadata))
        tile.memcached_flags = flags  # type: ignore
        tile.data = value
        tile.memcached_cas = cas  # type: ignore
        return tile

    def put_one(self, tile: Tile) -> Tile:
        flags = getattr(tile, "memcached_flags", self.flags)
        exptime = getattr(tile, "memached_exptime", self.exptime)
        assert tile.data is not None
        self.client.set(self.tilelayout.filename(tile.tilecoord, tile.metadata), flags, exptime, tile.data)
        return tile

    def delete_one(self, tile: Tile) -> Tile:
        self.client.delete(self.tilelayout.filename(tile.tilecoord, tile.metadata))
        return tile
