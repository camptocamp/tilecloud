from typing import Optional

from tilecloud import Tile


class ContentTypeAdder:
    """
    Create a filter that adds a content type to the tile.

        content_type:
        Force this content type for the tile. Default is ``None``, meaning
        that the content type will be determined based on the tile data.
    """

    def __init__(self, content_type: Optional[str] = None) -> None:
        self.content_type = content_type

    def __call__(self, tile: Tile) -> Tile:
        if self.content_type is None and tile.content_encoding is None and tile.data is not None:
            data = str(tile.data)
            if data.startswith("{"):
                tile.content_type = "application/json"
            elif data.startswith("\x89PNG\x0d\x0a\x1a\x0a"):
                tile.content_type = "image/png"
            elif data.startswith("\xff\xd8"):
                tile.content_type = "image/jpeg"
        else:
            tile.content_type = self.content_type
        return tile
