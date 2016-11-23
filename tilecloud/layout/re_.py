from tilecloud import TileLayout


class RETileLayout(TileLayout):

    def __init__(self, pattern, filename_re):
        self.pattern = pattern
        self.filename_re = filename_re

    def tilecoord(self, filename):
        match = self.filename_re.match(filename)
        if not match:
            raise ValueError('invalid literal for {0!s}.tilecoord(): {1!r}'.format(self.__class__.__name__, filename))
        return self._tilecoord(match)

    @staticmethod
    def _tilecoord(match):  # pragma: no cover
        raise NotImplementedError
