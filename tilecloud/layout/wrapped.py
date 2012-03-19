import re

from tilecloud import TileLayout


class WrappedTileLayout(TileLayout):
    """A tile layout with an option prefix and/or suffix"""

    def __init__(self, tile_layout, prefix='', suffix=''):
        self.tile_layout = tile_layout
        self.prefix = prefix
        self.suffix = suffix
        prefix_re = re.escape(self.prefix)
        suffix_re = re.escape(self.suffix)
        self.pattern = ''.join((prefix_re, tile_layout.pattern, suffix_re))
        filename_pattern = ''.join((prefix_re,
                                    r'(', self.tile_layout.pattern, r')',
                                    suffix_re, r'\Z'))
        self.filename_re = re.compile(filename_pattern)

    def filename(self, tilecoord):
        return ''.join((self.prefix,
                        self.tile_layout.filename(tilecoord),
                        self.suffix))

    def tilecoord(self, filename):
        match = self.filename_re.match(filename)
        if not match:
            raise RuntimeError # FIXME
        return self.tile_layout.tilecoord(match.group(1))
