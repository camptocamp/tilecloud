from tilecloud import TileStore


class MemcachedTileStore(TileStore):

    def __init__(self, client, tilelayout, flags=0, exptime=0, **kwargs):
        TileStore.__init__(self, **kwargs)
        self.client = client
        self.tilelayout = tilelayout
        self.flags = flags
        self.exptime = exptime

    def __contains__(self, tile):
        flags, value, cas = self.client.get(self.tilelayout.filename(tile.tilecoord))
        return flags is not None

    def get_one(self, tile):
        flags, value, cas = self.client.get(self.tilelayout.filename(tile.tilecoord))
        tile.memcached_flags = flags
        tile.data = value
        tile.memcached_cas = cas
        return tile

    def put_one(self, tile):
        flags = getattr(tile, 'memcached_flags', self.flags)
        exptime = getattr(tile, 'memached_exptime', self.exptime)
        self.client.set(self.tilelayout.filename(tile.tilecoord), flags, exptime, tile.data)
        return tile

    def delete_one(self, tile):
        self.client.delete(self.tilelayout.filename(tile.tilecoord))
        return tile
