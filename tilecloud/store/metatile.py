from sys import version_info

from tilecloud import Tile, TileStore
from tilecloud.lib.PIL_ import FORMAT_BY_CONTENT_TYPE

if version_info[0] == 2:
    from cStringIO import StringIO
else:
    from io import BytesIO as StringIO

try:
    from PIL import Image
    Image  # suppress pyflakes warning
except:
    import Image


class MetaTileSplitterTileStore(TileStore):

    def __init__(self, format, tile_size=256, border=0, **kwargs):
        self.format = format
        self.tile_size = tile_size
        self.border = border
        TileStore.__init__(self, **kwargs)

    def get(self, tiles):
        for metatile in tiles:
            metaimage = Image.open(StringIO(metatile.data))
            for tilecoord in metatile.tilecoord:
                x = self.border + (tilecoord.x - metatile.tilecoord.x) * self.tile_size
                y = self.border + (tilecoord.y - metatile.tilecoord.y) * self.tile_size
                image = metaimage.crop((x, y, x + self.tile_size, y + self.tile_size))
                string_io = StringIO()
                image.save(string_io, FORMAT_BY_CONTENT_TYPE[self.format])
                yield Tile(tilecoord, data=string_io.getvalue(), content_type=self.format)
