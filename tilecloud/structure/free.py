from tilecloud import TileCoord, TileStructure


class FreeTileStructure(TileStructure):

    def __init__(self, resolutions, max_extent=None, tile_size=None, scale=1):
        TileStructure.__init__(self, max_extent=max_extent, tile_size=tile_size)
        assert list(resolutions) == sorted(resolutions, reverse=True)
        assert all(isinstance(r, int) for r in resolutions)
        self.resolutions = resolutions
        self.scale = scale
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
                for i in xrange(0, factor):
                    x = factor * tilecoord.x + i
                    for j in xrange(0, factor):
                        y = factor * tilecoord.y + j
                        yield TileCoord(child_z, x, y)

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
