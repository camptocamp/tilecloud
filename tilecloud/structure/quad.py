from tilecloud import TileCoord, TileStructure


class QuadTileStructure(TileStructure):

    def __init__(self, max_extent=None, tile_size=None, max_zoom=None):
        TileStructure.__init__(self, max_extent=max_extent, tile_size=tile_size)
        self.max_zoom = max_zoom

    def children(self, tilecoord):
        if self.max_zoom is None or tilecoord.z < self.max_zoom:
            yield TileCoord(tilecoord.z + 1, 2 * tilecoord.x, 2 * tilecoord.y)
            yield TileCoord(tilecoord.z + 1, 2 * tilecoord.x + 1, 2 * tilecoord.y)
            yield TileCoord(tilecoord.z + 1, 2 * tilecoord.x, 2 * tilecoord.y + 1)
            yield TileCoord(tilecoord.z + 1, 2 * tilecoord.x + 1, 2 * tilecoord.y + 1)

    def parent(self, tilecoord):
        if tilecoord.z == 0:
            return None
        else:
            return TileCoord(tilecoord.z - 1, int(tilecoord.x // 2), int(tilecoord.y // 2))

    def roots(self):
        yield TileCoord(0, 0, 0)
