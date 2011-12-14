class ContentTypeAdder(object):
    """A class that adds a content type to a tile"""

    def __init__(self, content_type=None):
        self.content_type = content_type

    def __call__(self, tile):
        if self.content_type is None and tile.content_encoding is None:
            assert tile.data is not None
            data = str(tile.data)
            if data.startswith('\x89PNG\x0d\x0a\x1a\x0a'):
                tile.content_type = 'image/png'
            elif data.startswith('\xff\xd8'):
                tile.content_type = 'image/jpeg'
        else:
            tile.content_type = self.content_type
        return tile
