class ContentTypeAdder(object):
    """A class that adds a content type to a tile"""

    def __init__(self, content_type):
        self.content_type = content_type

    def __call__(self, tile):
        tile.content_type = self.content_type
        return tile
