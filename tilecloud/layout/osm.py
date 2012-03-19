import re

from tilecloud import TileCoord
from tilecloud.layout.re_ import RETileLayout


class OSMTileLayout(RETileLayout):
    """OpenStreetMap tile layout"""

    PATTERN = r'[0-9]+/[0-9]+/[0-9]+'
    RE = re.compile(r'([0-9]+)/([0-9]+)/([0-9]+)\Z')

    def __init__(self):
        RETileLayout.__init__(self, self.PATTERN, self.RE)

    def filename(self, tilecoord):
        return '%d/%d/%d' % (tilecoord.z, tilecoord.x, tilecoord.y)

    def _tilecoord(self, match):
        return TileCoord(*map(int, match.groups()))
