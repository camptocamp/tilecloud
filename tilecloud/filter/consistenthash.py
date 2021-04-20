from typing import Optional

from tilecloud import Tile


class EveryNth:
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

    def __init__(self, n: int, i: int) -> None:
        self.n = n
        self.i = i

    def __call__(self, tile: Tile) -> Optional[Tile]:
        if hash(tile.tilecoord) % self.n == self.i:
            return tile
        else:
            return None
