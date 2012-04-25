from tilecloud import TileCoord, TileStructure


class QuadTileStructure(TileStructure):

    def __init__(self, max_extent=None, tile_size=None, max_zoom=None, flip_y=False):
        TileStructure.__init__(self, max_extent=max_extent, tile_size=tile_size, flip_y=flip_y)
        self.max_zoom = max_zoom

    def children(self, tilecoord):
        if self.max_zoom is None or tilecoord.z < self.max_zoom:
            yield TileCoord(tilecoord.z + 1, 2 * tilecoord.x, 2 * tilecoord.y)
            yield TileCoord(tilecoord.z + 1, 2 * tilecoord.x + 1, 2 * tilecoord.y)
            yield TileCoord(tilecoord.z + 1, 2 * tilecoord.x, 2 * tilecoord.y + 1)
            yield TileCoord(tilecoord.z + 1, 2 * tilecoord.x + 1, 2 * tilecoord.y + 1)

    def extent(self, tilecoord, border=0):
        if self.flip_y:
            y = (1 << tilecoord.z) - tilecoord.y - tilecoord.n
        else:
            y = tilecoord.y
        delta = float(border) / self.tile_size if border else 0
        minx = self.max_extent[0] + (self.max_extent[2] - self.max_extent[0]) * (tilecoord.x - delta) / (1 << tilecoord.z)
        miny = self.max_extent[1] + (self.max_extent[3] - self.max_extent[1]) * (y - delta) / (1 << tilecoord.z)
        maxx = self.max_extent[0] + (self.max_extent[2] - self.max_extent[0]) * (tilecoord.x + tilecoord.n + delta) / (1 << tilecoord.z)
        maxy = self.max_extent[1] + (self.max_extent[3] - self.max_extent[1]) * (y + tilecoord.n + delta) / (1 << tilecoord.z)
        return (minx, miny, maxx, maxy)

    def parent(self, tilecoord):
        if tilecoord.z == 0:
            return None
        else:
            return TileCoord(tilecoord.z - 1, int(tilecoord.x // 2), int(tilecoord.y // 2))

    def roots(self):
        yield TileCoord(0, 0, 0)

    def tilecoord(self, z, x, y):
        return TileCoord(z,
                         int((x - self.max_extent[0]) * (1 << z) / (self.max_extent[2] - self.max_extent[0])),
                         int((y - self.max_extent[1]) * (1 << z) / (self.max_extent[3] - self.max_extent[1])))
