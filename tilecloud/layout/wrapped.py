import re

from tilecloud import TileLayout


class WrappedTileLayout(TileLayout):
    """A tile layout with an option prefix and/or suffix"""

    def __init__(self, tilelayout, prefix='', suffix=''):
        self.tilelayout = tilelayout
        self.prefix = prefix
        self.suffix = suffix
        prefix_re = re.escape(self.prefix)
        suffix_re = re.escape(self.suffix)
        self.pattern = ''.join((prefix_re, tilelayout.pattern, suffix_re))
        filename_pattern = ''.join((prefix_re,
                                    r'(', self.tilelayout.pattern, r')',
                                    suffix_re, r'\Z'))
        self.filename_re = re.compile(filename_pattern)

    def filename(self, tilecoord):
        return ''.join((self.prefix,
                        self.tilelayout.filename(tilecoord),
                        self.suffix))

    def tilecoord(self, filename):
        match = self.filename_re.match(filename)
        if not match:
            raise ValueError('invalid literal for {0!s}.tilecoord(): {1!r}'.format(self.__class__.__name__, filename))
        return self.tilelayout.tilecoord(match.group(1))
