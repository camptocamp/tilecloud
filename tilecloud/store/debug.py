
import PIL.Image
import PIL.ImageDraw
import PIL.ImageFont
from six.moves import cStringIO as StringIO

from tilecloud import TileStore
from tilecloud.lib.PIL_ import FORMAT_BY_CONTENT_TYPE


class DebugTileStore(TileStore):

    def __init__(self, color=(0, 0, 0), **kwargs):
        TileStore.__init__(self, content_type='image/png', **kwargs)
        self.color = color

    def get_one(self, tile):
        image = PIL.Image.new('RGBA', (256, 256), (0, 0, 0, 0))
        draw = PIL.ImageDraw.Draw(image)
        draw.line([(0, 255), (0, 0), (255, 0)], fill=self.color)
        text = str(tile.tilecoord)
        font = PIL.ImageFont.load_default()
        width, height = font.getsize(text)
        draw.text((127 - width / 2, 127 - height / 2), text, fill=self.color, font=font)
        string_io = StringIO()
        image.save(string_io, FORMAT_BY_CONTENT_TYPE[self.content_type])
        tile.data = string_io.getvalue()
        return tile
