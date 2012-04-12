from memcache import Client

from tilecloud import TileStore


class MemcachedTileStore(TileStore):

    def __init__(self, servers, tilelayout, **kwargs):
        TileStore.__init__(self, **kwargs)
        self.mc = Client(servers)
        self.tilelayout = tilelayout

    def __contains__(self, tile):
        return self.mc.get(self.tilelayout.filename(tile.tilecoord)) is not None

    def list(self):
        # possible with memcached ?
        raise NotImplementedError

    def get_one(self, tile):
        tile.data = self.mc.get(self.tilelayout.filename(tile.tilecoord))
        return tile

    def put_one(self, tile):
        # FIXME: expire in seconds or unix timestamp
        self.mc.set(self.tilelayout.filename(tile.tilecoord), tile.data)
        return tile

    def delete_one(self, tile):
        self.mc.delete(self.tilelayout.filename(tile.tilecoord))
        return tile
