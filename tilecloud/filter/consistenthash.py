class EveryNth(object):

    def __init__(self, n, i):
        self.n = n
        self.i = i

    def __call__(self, tile):
        if hash(tile.tilecoord) % self.n == self.i:
            return tile
        else:
            return None
