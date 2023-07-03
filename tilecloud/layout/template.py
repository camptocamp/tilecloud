import re
from re import Match
from typing import Any, Optional

from tilecloud import TileCoord
from tilecloud.layout.re_ import RETileLayout


class TemplateTileLayout(RETileLayout):
    def __init__(self, template: str) -> None:
        self.template = template
        self.prefix = None
        index, patterns, filename_patterns = 0, [], []
        for match in re.finditer(r"%\(([xyz])\)d", self.template):
            prematch_pattern = re.escape(self.template[index : match.start()])
            if self.prefix is None:
                self.prefix = self.template[index : match.start()]
            patterns.append(prematch_pattern)
            patterns.append(r"\d+")
            filename_patterns.append(prematch_pattern)
            filename_patterns.append(rf"(?P<{match.group(1)!s}>\d+)")
            index = match.end()
        postmatch_pattern = re.escape(self.template[index:])
        patterns.append(postmatch_pattern)
        filename_patterns.append(postmatch_pattern)
        pattern = "".join(patterns)
        filename_re = re.compile("".join(filename_patterns))
        RETileLayout.__init__(self, pattern, filename_re)

    def filename(self, tilecoord: TileCoord, metadata: Optional[Any] = None) -> str:
        return self.template % {"z": tilecoord.z, "x": tilecoord.x, "y": tilecoord.y}

    @staticmethod
    def _tilecoord(match: Match[str]) -> TileCoord:
        return TileCoord(*(int(match.group(s)) for s in "zxy"))
