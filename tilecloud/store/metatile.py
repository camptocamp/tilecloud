from cStringIO import StringIO

from PIL import Image

from tilecloud import Tile, TileStore


class MetaTileToTileStore(TileStore):

    def __init__(self, tile_size, buffer, image_format, **kwargs):
        self.tile_size = tile_size
        self.buffer = buffer
        self.image_format = image_format
        TileStore.__init__(self, **kwargs)

    def get(self, tiles):
        for metatile in tiles:
            metaimage = Image.open(StringIO(metatile.data))
            for tilecoord in metatile.tilecoord:
                x = tilecoord.x - metatile.tilecoord.x
                y = tilecoord.y - metatile.tilecoord.y
                px_x = self.buffer + x * self.tile_size
                px_y = self.buffer + y * self.tile_size
                image = metaimage.crop((px_x, px_y, px_x + self.tile_size, px_y + self.tile_size))
                string_io = StringIO()
                image.save(string_io, self.image_format)
                yield Tile(tilecoord, data=string_io.getvalue())
