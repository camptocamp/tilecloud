from cStringIO import StringIO

import cairo

from tilecloud import TileStore


class DebugTileStore(TileStore):

    def __init__(self, color=(0, 0, 0), transparent=True, **kwargs):
        TileStore.__init__(self, content_type='image/png', **kwargs)
        self.color = color
        self.inverse_color = tuple(1.0 - x for x in color)
        self.transparent = transparent

    def get_one(self, tile):
        format = cairo.FORMAT_ARGB32 if self.transparent else cairo.FORMAT_RGB24
        image_surface = cairo.ImageSurface(format, 256, 256)
        context = cairo.Context(image_surface)
        if not self.transparent:
            context.set_source_rgba(1, 1, 1, 1)
            context.paint()
        context.rectangle(0.5, 0.5, 256, 256)
        if self.transparent:
            context.set_source_rgb(*self.inverse_color)
            context.set_line_width(2)
            context.stroke_preserve()
        context.set_source_rgb(*self.color)
        context.set_line_width(1)
        context.stroke()
        text = str(tile.tilecoord)
        extents = context.text_extents(text)
        context.move_to(128.0 - extents[2] / 2.0, 128 - extents[3] / 2.0)
        context.text_path(text)
        if self.transparent:
            context.set_source_rgb(*self.inverse_color)
            context.set_line_width(2)
            context.stroke_preserve()
        context.set_source_rgb(*self.color)
        context.fill()
        string_io = StringIO()
        image_surface.write_to_png(string_io)
        tile.content_type = 'image/png'
        tile.data = string_io.getvalue()
        return tile
