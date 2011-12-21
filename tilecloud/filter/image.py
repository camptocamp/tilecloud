from cStringIO import StringIO

import PIL.Image

from tilecloud import Tile



FORMAT_BY_CONTENT_TYPE = {
        'image/jpeg': 'JPEG',
        'image/png': 'PNG'}



class ImageFormatConverter(object):
    """A class that converts a tile into the desired format"""

    def __init__(self, content_type, **kwargs):
        self.content_type = content_type
        self.kwargs = kwargs
        self.format = FORMAT_BY_CONTENT_TYPE[content_type]

    def __call__(self, tile):
        if tile.content_type != self.content_type:
            assert tile.data is not None
            string_io = StringIO()
            PIL.Image.open(StringIO(tile.data)).save(string_io, self.format, **self.kwargs)
            tile.content_type = self.content_type
            tile.data = string_io.getvalue()
        return tile



class MergeFilter(object):

    def __init__(self, tile_stores, content_type=None, **kwargs):
        self.tile_stores = list(tile_stores)
        self.content_type = content_type
        self.kwargs = kwargs

    def __call__(self, tile):
        image = PIL.Image.open(StringIO(tile.data))
        for tile_store in self.tile_stores:
            t = tile_store.get_one(Tile(tile.tilecoord))
            if t is not None:
                image2 = PIL.Image.open(StringIO(t.data))
                image.paste(image2, None, image2)
        content_type = self.content_type
        if content_type is None:
            self.content_type = tile.content_type
        string_io = StringIO()
        image.save(string_io, FORMAT_BY_CONTENT_TYPE[content_type], **self.kwargs)
        tile.content_type = content_type
        tile.data = string_io.getvalue()
        return tile



class PILImageFilter(object):

    def __init__(self, filter, **kwargs):
        self.filter = filter
        self.kwargs = kwargs

    def __call__(self, tile):
        assert tile.data is not None
        image = PIL.Image.open(StringIO(tile.data))
        image = image.filter(self.filter)
        string_io = StringIO()
        image.save(string_io, FORMAT_BY_CONTENT_TYPE.get(tile.content_type, 'PNG'), **self.kwargs)
        tile.data = string_io.getvalue()
        return tile
