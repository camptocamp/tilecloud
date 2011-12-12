from cStringIO import StringIO
from gzip import GzipFile



class GzipCompressor(object):
    """A class that compresses a tile with gzip"""

    def __init__(self, compresslevel=9):
        self.compresslevel = compresslevel

    def __call__(self, tile):
        assert hasattr(tile, 'data')
        string_io = StringIO()
        gzip_file = GzipFile(compresslevel=self.compresslevel, fileobj=string_io, mode='w')
        gzip_file.write(tile.data)
        gzip_file.close()
        tile.content_encoding = 'gzip'
        tile.data = string_io.getvalue()
        return tile



