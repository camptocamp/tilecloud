from cStringIO import StringIO

import PIL.Image



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
        if not hasattr(tile, 'content_type') or tile.content_type != self.content_type:
            assert hasattr(tile, 'data')
            string_io = StringIO()
            PIL.Image.open(StringIO(tile.data)).save(string_io, self.format, **self.kwargs)
            tile.content_type = self.content_type
            tile.data = string_io.getvalue()
        return tile
