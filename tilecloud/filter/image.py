from cStringIO import StringIO

import PIL.Image


def content_type_to_pil_format(content_type):
    if content_type == 'image/jpeg':
        return 'JPEG'
    elif content_type == 'image/png':
        return 'PNG'
    else:
        assert False


class ImageFormatConverter(object):
    """A class that converts a tile into the desired format"""

    def __init__(self, content_type, **kwargs):
        self.content_type = content_type
        self.kwargs = kwargs
        self.format = content_type_to_pil_format(self.content_type)

    def __call__(self, tile):
        if not hasattr(tile, 'content_type') or tile.content_type != self.content_type:
            assert hasattr(tile, 'data')
            string_io = StringIO()
            PIL.Image.open(StringIO(tile.data)).save(string_io, self.format, **self.kwargs)
            tile.content_type = self.content_type
            tile.data = string_io.getvalue()
        return tile


class PILImageFilters(object):
    def __init__(self, filter):
        self.filter = filter

    def __call__(self, tile):
        if hasattr(tile, 'data'):
            im = PIL.Image.open(StringIO(tile.data)).filter(self.filter)
            output = StringIO()
            im.save(output, content_type_to_pil_format(tile.content_type))
            tile.data = output.getvalue()
            output.close()
            return tile
        else:
            return tile
