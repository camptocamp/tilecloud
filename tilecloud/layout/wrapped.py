import re
from typing import Any

from tilecloud import TileCoord, TileLayout
from tilecloud.layout.re_ import RETileLayout


class WrappedTileLayout(TileLayout):
    """A tile layout with an option prefix and/or suffix."""

    def __init__(self, tilelayout: RETileLayout, prefix: str = "", suffix: str = "") -> None:
        self.tilelayout = tilelayout
        self.prefix = prefix
        self.suffix = suffix
        prefix_re = re.escape(self.prefix)
        suffix_re = re.escape(self.suffix)
        self.pattern = f"{prefix_re}{tilelayout.pattern}{suffix_re}"
        filename_pattern = f"{prefix_re}({self.tilelayout.pattern}){suffix_re}\\Z"
        self.filename_re = re.compile(filename_pattern)

    def filename(self, tilecoord: TileCoord, metadata: Any | None = None) -> str:
        return "".join((self.prefix, self.tilelayout.filename(tilecoord, metadata), self.suffix))

    def tilecoord(self, filename: str) -> TileCoord:
        match = self.filename_re.match(filename)
        if not match:
            raise ValueError(f"invalid literal for {self.__class__.__name__!s}.tilecoord(): {filename!r}")
        return self.tilelayout.tilecoord(match.group(1))
