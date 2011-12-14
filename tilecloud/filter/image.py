from cStringIO import StringIO

import PIL.Image



class ImageFormatConverter(object):
    """A class that converts a tile into the desired format"""

    def __init__(self, content_type, **kwargs):
        self.content_type = content_type
        self.kwargs = kwargs
        if self.content_type == 'image/jpeg':
            self.format = 'JPEG'
        elif content_type == 'image/png':
            self.format = 'PNG'
        else:
            assert False

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
            im = PIL.Image.open(StringIO(tile.data))
            im = im.filter(self.filter)
            if tile.content_type == 'image/png':
                format = 'PNG'
            elif tile.content_type == 'image/jpeg':
                format = 'JPEG'
            else:
                assert False
            output = StringIO()
            im.save(output, format)
            tile.data = output.getvalue()
            output.close()
            return tile
        else:
            return tile
