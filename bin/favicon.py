import math

import cairo
from shapely.geometry import LineString, Point, Polygon
from shapely.ops import cascaded_union

def box(minx, miny, maxx, maxy):
    return Polygon(((minx, miny), (maxx, miny), (maxx, maxy), (minx, maxy)))

GOLDEN_RATIO = (1 + math.sqrt(5)) / 2

Y0 = int(3 - (2 + GOLDEN_RATIO) / 2) - 0.5
rectangle = box(1, Y0, 5, 2 + Y0)
circle1 = Point(1, 1 + Y0).buffer(1)
circle2 = Point(1 + 1 / GOLDEN_RATIO, 2 + Y0).buffer(1 / GOLDEN_RATIO)
circle3 = Point(5 - GOLDEN_RATIO, 2 + Y0).buffer(GOLDEN_RATIO)
circle4 = Point(5, 1 + Y0).buffer(1)
cloud = cascaded_union((rectangle, circle1, circle2, circle3, circle4))

SIZE = 16
TRANSLATE = 1
LINE_WIDTH = 1
SCALE = (SIZE - 2 * TRANSLATE) / 6.0
image_surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, SIZE, SIZE)
context = cairo.Context(image_surface)
context.scale(1, -1)
context.translate(0, -SIZE)
for i, coord in enumerate(cloud.exterior.coords):
    if i == 0:
        context.move_to(SCALE * coord[0] + TRANSLATE, SCALE * coord[1] + 2 * TRANSLATE)
    else:
        context.line_to(SCALE * coord[0] + TRANSLATE, SCALE * coord[1] + 2 * TRANSLATE)
context.close_path()
context.set_source_rgb(1, 1, 1)
context.fill_preserve()
context.set_source_rgb(0, 0, 0)
context.set_line_width(LINE_WIDTH)
context.stroke()
image_surface.write_to_png('favicon.png')
