from tilecloud import Tile


class EveryNth:
    """
    Create a filter that returns one out of every n tiles. This is done using consistent hashing.

    The following is used to determine if the tile should be returned::

        hash(tile.tilecoord) % n == i

        i:
        ``i`` in the above calculation.

        n:
        ``n`` in the above calculation.
    """

    def __init__(self, n: int, i: int) -> None:  # pylint: disable=invalid-name
        self.n = n  # pylint: disable=invalid-name
        self.i = i

    def __call__(self, tile: Tile) -> Tile | None:
        if hash(tile.tilecoord) % self.n == self.i:
            return tile
        return None
