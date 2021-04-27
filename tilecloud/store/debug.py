from io import BytesIO
from typing import Any, Optional, Tuple

import PIL.Image
import PIL.ImageDraw
import PIL.ImageFont

from tilecloud import Tile, TileStore
from tilecloud.lib.PIL_ import FORMAT_BY_CONTENT_TYPE


class DebugTileStore(TileStore):
    def __init__(self, color: Tuple[int, int, int] = (0, 0, 0), **kwargs: Any):
        TileStore.__init__(self, content_type="image/png", **kwargs)
        self.color = color

    def get_one(self, tile: Tile) -> Optional[Tile]:
        image = PIL.Image.new("RGBA", (256, 256), (0, 0, 0, 0))
        draw = PIL.ImageDraw.Draw(image)
        draw.line([(0, 255), (0, 0), (255, 0)], fill=self.color)
        text = str(tile.tilecoord)
        font = PIL.ImageFont.load_default()
        width, height = font.getsize(text)
        draw.text((127 - width / 2, 127 - height / 2), text, fill=self.color, font=font)
        bytes_io = BytesIO()
        assert self.content_type is not None
        image.save(bytes_io, FORMAT_BY_CONTENT_TYPE[self.content_type])
        tile.data = bytes_io.getvalue()
        return tile
