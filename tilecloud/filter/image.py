"""
This module includes filters doing manipulations on the tile image. It
requires the PIL lib.
"""

import PIL.Image
from six.moves import cStringIO as StringIO

from tilecloud import Tile
from tilecloud.lib.PIL_ import FORMAT_BY_CONTENT_TYPE


class ImageFormatConverter(object):
    """
    Create a filter that converts a tile into the desired format.

    :param content_type:
        The content type representing the format to convert the tile image
        to.

    :param kwargs:
        Extra arguments passed to ``PIL`` when opening the tile image.
    """

    def __init__(self, content_type, **kwargs):
        self.content_type = content_type
        self.kwargs = kwargs
        self.format = FORMAT_BY_CONTENT_TYPE[content_type]

    def __call__(self, tile):
        if tile.content_type != self.content_type:
            assert tile.data is not None
            string_io = StringIO()
            PIL.Image.open(StringIO(tile.data)).save(string_io, self.format,
                                                     **self.kwargs)
            tile.content_type = self.content_type
            tile.data = string_io.getvalue()
        return tile


class MergeFilter(object):
    """
    Create a filter that merges the tile with tiles of the same
    coordinates.

    :param tilestores:
        A collection of :class:`TileStore` objects from which tiles to
        merge with the currently handled tile are read.

    :param content_type:
        The content type to set in the tile. If ``None`` the content
        type of the first tile found in the stream is used for every
        other tile. Default is ``None``.
    """

    def __init__(self, tilestores, content_type=None, **kwargs):
        self.tilestores = list(tilestores)
        self.content_type = content_type
        self.kwargs = kwargs

    def __call__(self, tile):
        image = PIL.Image.open(StringIO(tile.data))
        for tilestore in self.tilestores:
            t = tilestore.get_one(Tile(tile.tilecoord))
            if t is not None:
                image2 = PIL.Image.open(StringIO(t.data))
                image.paste(image2, None, image2)
        content_type = self.content_type
        if content_type is None:
            self.content_type = tile.content_type
        string_io = StringIO()
        image.save(string_io, FORMAT_BY_CONTENT_TYPE[content_type],
                   **self.kwargs)
        tile.content_type = content_type
        tile.data = string_io.getvalue()
        return tile


class PILImageFilter(object):
    """
    Create a filter to filter the tile image (with the PIL ``filter``
    function).

    :param filter:
        The filter to pass to the PIL ``filter`` function.

    :param kwargs:
        Extra params passed to the PIL ``save`` function.
    """

    def __init__(self, filter, **kwargs):
        self.filter = filter
        self.kwargs = kwargs

    def __call__(self, tile):
        assert tile.data is not None
        image = PIL.Image.open(StringIO(tile.data))
        image = image.filter(self.filter)
        string_io = StringIO()
        image.save(string_io,
                   FORMAT_BY_CONTENT_TYPE.get(tile.content_type, 'PNG'),
                   **self.kwargs)
        tile.data = string_io.getvalue()
        return tile
