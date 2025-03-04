import re
from re import Match

from tilecloud import TileCoord
from tilecloud.layout.re_ import RETileLayout


class I3DTileLayout(RETileLayout):
    """I3D (FHNW/OpenWebGlobe) tile layout."""

    PATTERN = r"(?:[0-3]{2}/)*[0-3]{1,2}"
    RE = re.compile(PATTERN + r"\Z")

    def __init__(self) -> None:
        RETileLayout.__init__(self, self.PATTERN, self.RE)

    def filename(self, tilecoord: TileCoord, metadata: dict[str, str] | None = None) -> str:
        return "/".join(re.findall(r"[0-3]{1,2}", I3DTileLayout.quadcode_from_tilecoord(tilecoord)))

    @staticmethod
    def _tilecoord(match: Match[str]) -> TileCoord:
        return I3DTileLayout.tilecoord_from_quadcode(re.sub(r"/", "", match.group()))

    @staticmethod
    def quadcode_from_tilecoord(tilecoord: TileCoord) -> str:
        x, y = int(tilecoord.x), int(tilecoord.y)  # pylint: disable=invalid-name
        result = ""
        for _ in range(tilecoord.z):
            result += "0123"[(x & 1) + ((y & 1) << 1)]
            x >>= 1  # pylint: disable=invalid-name
            y >>= 1  # pylint: disable=invalid-name
        return result[::-1]

    @staticmethod
    def tilecoord_from_quadcode(quadcode: str) -> TileCoord:
        z, x, y = len(quadcode), 0, 0  # pylint: disable=invalid-name
        for i, code in enumerate(quadcode):
            mask = 1 << (z - i - 1)
            if code in ["1", "3"]:
                x |= mask  # pylint: disable=invalid-name
            if code in ["2", "3"]:
                y |= mask  # pylint: disable=invalid-name
        return TileCoord(z, x, y)
