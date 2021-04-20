from gzip import GzipFile
from io import BytesIO

from tilecloud import Tile


class GzipCompressor:
    """
    Create a filter that compresses a tile with gzip.

    :param compresslevel:
        The compression level. Default is 9.

    """

    def __init__(self, compresslevel: int = 9):
        self.compresslevel = compresslevel

    def __call__(self, tile: Tile) -> Tile:
        assert tile.data is not None
        assert tile.content_encoding is None
        bytes_io = BytesIO()
        gzip_file = GzipFile(compresslevel=self.compresslevel, fileobj=bytes_io, mode="w")
        gzip_file.write(tile.data)
        gzip_file.close()
        tile.content_encoding = "gzip"
        tile.data = bytes_io.getvalue()
        return tile


class GzipDecompressor:
    """
    Create a filter that decompresses a tile with gzip.
    """

    def __call__(self, tile: Tile) -> Tile:
        assert tile.data is not None
        if tile.content_encoding == "gzip":
            tile.content_encoding = None
            tile.data = GzipFile(fileobj=BytesIO(tile.data)).read()
        return tile
