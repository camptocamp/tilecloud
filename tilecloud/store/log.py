import re


from tilecloud import Tile, TileStore


class LogTileStore(TileStore):
    """Generates all tile coordinates matching the specified layout from lines"""

    def __init__(self, tile_layout, lines=None):
        self.tile_layout = tile_layout
        self.lines = lines

    def get_one(self, tile):
        tile.data = None
        return tile

    def list(self):
        # FIXME warn that this consumes lines
        filename_re = re.compile(self.tile_layout.pattern)
        for line in self.lines:
            match = filename_re.search(line)
            if match:
                yield Tile(self.tile_layout.tilecoord(match.group()), line=line)
