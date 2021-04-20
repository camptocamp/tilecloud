import re
from typing import Any, Optional

from _sre import SRE_Match

from tilecloud import TileCoord
from tilecloud.layout.re_ import RETileLayout


class OSMTileLayout(RETileLayout):
    """OpenStreetMap tile layout"""

    PATTERN = r"[0-9]+/[0-9]+/[0-9]+"
    RE = re.compile(r"([0-9]+)/([0-9]+)/([0-9]+)\Z")

    def __init__(self) -> None:
        RETileLayout.__init__(self, self.PATTERN, self.RE)

    @staticmethod
    def filename(tilecoord: TileCoord, metadata: Optional[Any] = None) -> str:
        return "{0:d}/{1:d}/{2:d}".format(tilecoord.z, tilecoord.x, tilecoord.y)

    @staticmethod
    def _tilecoord(match: SRE_Match) -> TileCoord:
        return TileCoord(*map(int, match.groups()))
