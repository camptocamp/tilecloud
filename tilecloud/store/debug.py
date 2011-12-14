from cStringIO import StringIO

import cairo

from tilecloud import TileStore



class DebugTileStore(TileStore):

    def __init__(self, inset=4):
        self.inset = 4

    def get_one(self, tile):
        image_surface = cairo.ImageSurface(cairo.FORMAT_RGB24, 256, 256)
        context = cairo.Context(image_surface)
        context.set_source_rgb(1, 1, 1)
        context.paint()
        context.rectangle(0.5 + self.inset, 0.5 + self.inset, 256 - 2 * self.inset, 256 - 2 * self.inset)
        context.set_source_rgb(0, 0, 0)
        context.set_line_width(1)
        context.stroke()
        text = str(tile.tilecoord)
        extents = context.text_extents(text)
        context.move_to(128.0 - extents[2] / 2.0, 128 - extents[3] / 2.0)
        context.show_text(text)
        context.fill()
        string_io = StringIO()
        image_surface.write_to_png(string_io)
        tile.content_type = 'image/png'
        tile.data = string_io.getvalue()
        return tile
