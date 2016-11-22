import re

from tilecloud import TileCoord
from tilecloud.layout.re_ import RETileLayout


class TemplateTileLayout(RETileLayout):

    def __init__(self, template):
        self.template = template
        self.prefix = None
        index, patterns, filename_patterns = 0, [], []
        for match in re.finditer(r'%\(([xyz])\)d', self.template):
            prematch_pattern = re.escape(self.template[index:match.start()])
            if self.prefix is None:
                self.prefix = self.template[index:match.start()]
            patterns.append(prematch_pattern)
            patterns.append(r'\d+')
            filename_patterns.append(prematch_pattern)
            filename_patterns.append(r'(?P<{0!s}>\d+)'.format(match.group(1)))
            index = match.end()
        postmatch_pattern = re.escape(self.template[index:])
        patterns.append(postmatch_pattern)
        filename_patterns.append(postmatch_pattern)
        pattern = ''.join(patterns)
        filename_re = re.compile(''.join(filename_patterns))
        RETileLayout.__init__(self, pattern, filename_re)

    def filename(self, tilecoord):
        return self.template % \
            dict(z=tilecoord.z, x=tilecoord.x, y=tilecoord.y)

    def _tilecoord(self, match):
        return TileCoord(*(int(match.group(s)) for s in 'zxy'))
