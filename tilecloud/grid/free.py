from math import floor
from six.moves import xrange
from six import integer_types

from tilecloud import TileCoord, TileGrid


class FreeTileGrid(TileGrid):

    def __init__(self, resolutions, max_extent=None, tile_size=None, scale=1, flip_y=False):
        TileGrid.__init__(self, max_extent=max_extent, tile_size=tile_size, flip_y=flip_y)
        assert list(resolutions) == sorted(resolutions, reverse=True)
        assert all(isinstance(r, integer_types) for r in resolutions)
        self.resolutions = resolutions
        self.scale = 1 if scale is 1 else float(scale)
        self.parent_zs = []
        self.child_zs = []
        for i, resolution in enumerate(self.resolutions):
            for parent in xrange(i - 1, -1, -1):
                if self.resolutions[parent] % resolution == 0:
                    self.parent_zs.append(parent)
                    self.child_zs[parent].append(i)
                    break
            else:
                self.parent_zs.append(None)
            self.child_zs.append([])

    def children(self, tilecoord):
        if tilecoord.z < len(self.resolutions):
            for child_z in self.child_zs[tilecoord.z]:
                factor = self.resolutions[tilecoord.z] / self.resolutions[child_z]
                for i in xrange(0, int(factor)):
                    x = factor * tilecoord.x + i
                    for j in xrange(0, int(factor)):
                        y = factor * tilecoord.y + j
                        yield TileCoord(child_z, x, y)

    def extent(self, tilecoord, border=0):
        y = tilecoord.y
        if not self.flip_y:
            n = self.scale * (self.max_extent[3] - self.max_extent[1]) / \
                float(self.tile_size * self.resolutions[tilecoord.z])
            y = n - y - tilecoord.n
        minx = self.max_extent[0] + (self.tile_size * tilecoord.x - border) * self.resolutions[tilecoord.z] / self.scale
        miny = self.max_extent[1] + (self.tile_size * y - border) * self.resolutions[tilecoord.z] / self.scale
        maxx = self.max_extent[0] + (self.tile_size * (tilecoord.x + tilecoord.n) + border) * self.resolutions[tilecoord.z] / self.scale
        maxy = self.max_extent[1] + (self.tile_size * (y + tilecoord.n) + border) * self.resolutions[tilecoord.z] / self.scale
        return (minx, miny, maxx, maxy)

    def parent(self, tilecoord):
        parent_z = self.parent_zs[tilecoord.z]
        if parent_z is None:
            return None
        else:
            factor = self.resolutions[parent_z] / self.resolutions[tilecoord.z]
            return TileCoord(parent_z, int(tilecoord.x // factor), int(tilecoord.y // factor))

    def roots(self):
        for z, parent_z in enumerate(self.parent_zs):
            if parent_z is None:
                x, s = 0, 0
                while s < self.resolutions[0]:
                    y, t = 0, 0
                    while t < self.resolutions[0]:
                        yield TileCoord(z, x, y)
                        y += 1
                        t += self.resolutions[z]
                    x += 1
                    s += self.resolutions[z]

    def tilecoord(self, z, x, y):
        tx = self.scale * (x - self.max_extent[0]) / (self.resolutions[z] * self.tile_size)
        ty = self.scale * (y - self.max_extent[1]) / float(self.resolutions[z] * self.tile_size)

        if not self.flip_y:
            n = self.scale * (self.max_extent[3] - self.max_extent[1]) / \
                float(self.tile_size * self.resolutions[z])
            ty = n - ty

        return TileCoord(z, int(floor(tx)), int(floor(ty)))

    def zs(self):
        return xrange(len(self.resolutions))
