from gzip import GzipFile
from six.moves import cStringIO as StringIO


class GzipCompressor(object):
    """
    Create a filter that compresses a tile with gzip.

    :param compresslevel:
        The compression level. Default is 9.

    """

    def __init__(self, compresslevel=9):
        self.compresslevel = compresslevel

    def __call__(self, tile):
        assert tile.data is not None
        assert tile.content_encoding is None
        string_io = StringIO()
        gzip_file = GzipFile(compresslevel=self.compresslevel,
                             fileobj=string_io,
                             mode='w')
        gzip_file.write(tile.data)
        gzip_file.close()
        tile.content_encoding = 'gzip'
        tile.data = string_io.getvalue()
        return tile


class GzipDecompressor(object):
    """
    Create a filter that decompresses a tile with gzip.
    """

    def __call__(self, tile):
        assert tile.data is not None
        if tile.content_encoding == 'gzip':
            tile.content_encoding = None
            tile.data = GzipFile(fileobj=StringIO(tile.data)).read()
        return tile
