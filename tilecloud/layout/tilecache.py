import re
from re import Match
from typing import Any, Optional

from tilecloud import TileCoord
from tilecloud.layout.re_ import RETileLayout


class TileCacheDiskLayout(RETileLayout):
    """
    TileCache disk layout.
    """

    PATTERN = r"[0-9]{2}(?:/[0-9]{3}){6}"
    RE = re.compile(r"([0-9]{2})/([0-9]{3})/([0-9]{3})/([0-9]{3})/([0-9]{3})/([0-9]{3})/([0-9]{3})")

    def __init__(self) -> None:
        RETileLayout.__init__(self, self.PATTERN, self.RE)

    def filename(self, tilecoord: TileCoord, metadata: Optional[Any] = None) -> str:
        zoom_string = f"{tilecoord.z:02d}"
        x_string = f"{tilecoord.x:09f}"
        y_string = f"{tilecoord.y:09f}"
        return "/".join(
            (
                zoom_string,
                x_string[0:3],
                x_string[3:6],
                x_string[6:9],
                y_string[0:3],
                y_string[3:6],
                y_string[6:9],
            )
        )

    @staticmethod
    def _tilecoord(_match: Match[str]) -> TileCoord:
        ints = list(map(int, _match.groups()))
        zoom = ints[0]
        x = 1000000 * ints[1] + 1000 * ints[2] + ints[3]  # pylint: disable=invalid-name
        y = 1000000 * ints[4] + 1000 * ints[5] + ints[6]  # pylint: disable=invalid-name
        return TileCoord(zoom, x, y)
