class EveryNth(object):
    """
    Create a filter that returns one out of every n tiles. This is done
    using consistent hashing.

    The following is used to determine if the tile should be returned::

        hash(tile.tilecoord) % n == i

    :param i:
        ``i`` in the above calculation.

    :param n:
        ``n`` in the above calculation.


    """

    def __init__(self, n, i):
        self.n = n
        self.i = i

    def __call__(self, tile):
        if hash(tile.tilecoord) % self.n == self.i:
            return tile
        else:
            return None
