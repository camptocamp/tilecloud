class HashDropper(object):
    """
    Create a filter to remove the tiles data where they have
    the specified size and hash.

    Used to drop the empty tiles.

    The ``store`` is used to delete the empty tiles.
    """

    def __init__(self, size, hashcode, store=None):
        self.size = size
        self.hashcode = hashcode
        self.store = store

    def __call__(self, tile):
        if len(tile.data) != self.size or \
                hash(tile.data) != self.hashcode:
            return tile
        else:
            if self.store:
                self.store.delete_one(tile)
            return None

class HashLogger(object):  # pragma: no cover
    """
    Log the tile size and hash.
    """

    def __init__(self, logger):
        self.logger = logger

    def __call__(self, tile):
        self.logger.info("size: %i, hash: %i" % (len(tile.data), hash(tile.data)))
        return tile
