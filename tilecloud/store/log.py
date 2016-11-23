import re


from tilecloud import Tile, TileStore


class LogTileStore(TileStore):
    """Generates all tile coordinates matching the specified layout from file"""

    def __init__(self, tilelayout, file=None, **kwargs):
        TileStore.__init__(self, **kwargs)
        self.tilelayout = tilelayout
        self.file = file

    @staticmethod
    def get_one(tile):
        tile.data = None
        return tile

    def list(self):
        # FIXME warn that this consumes file
        filename_re = re.compile(self.tilelayout.pattern)
        for line in self.file:
            match = filename_re.search(line)
            if match:
                yield Tile(self.tilelayout.tilecoord(match.group()), line=line)

    def put_one(self, tile):
        self.file.write(self.tilelayout.filename(tile.tilecoord) + '\n')
        return tile
