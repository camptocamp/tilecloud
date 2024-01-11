#!/usr/bin/env python

import os.path
import re
import sys
from optparse import OptionParser

import bottle

from tilecloud import BoundingPyramid, Bounds, Tile, TileCoord, TileStore
from tilecloud.filter.contenttype import ContentTypeAdder

_root = None


@bottle.route("/tiles/<index:int>/tiles/<z:int>/<x:int>/<y:int><ext:re:.*>")
def tile(index, z, x, y, ext):
    # FIXME check ext
    if len(tilestores) < index:
        bottle.abort(404)
    tilecoord = TileCoord(z + _root.z, x + _root.x * (1 << z), y + _root.y * (1 << z))
    if cache is not None and (index, z, x, y) in cache:
        tile = cache[(index, z, x, y)]
    else:
        tile = Tile(tilecoord)
        tile = tilestores[index][1].get_one(tile)
        if cache is not None:
            cache[(index, z, x, y)] = tile
    if tile is None:
        bottle.abort(404)
    if tile.data is None:
        bottle.abort(204)
    tile = content_type_adder(tile)
    if tile.content_type is not None:
        bottle.response.content_type = tile.content_type
    if tile.content_encoding is not None:
        bottle.response.set_header("Content-Encoding", tile.content_encoding)
    bottle.response.set_header("Access-Control-Allow-Origin", "*")
    bottle.response.content_length = len(tile.data)
    return tile.data


@bottle.route("/tiles/<index:int>/layersettings.json")
def openwebglobe_layersettings(index):
    if len(tilestores) < index:
        bottle.abort(404)
    name, tilestore = tilestores[index]
    bounding_pyramid = tilestore.bounding_pyramid
    if bounding_pyramid is None:
        bounding_pyramid = tilestore.get_cheap_bounding_pyramid()
    if bounding_pyramid is None:
        bounding_pyramid = BoundingPyramid({20: (Bounds(0, 1 << 20), Bounds(0, 1 << 20))})
    maxlod = max(bounding_pyramid.zs())
    xbounds, ybounds = bounding_pyramid.zget(maxlod)
    extent = [xbounds.start, ybounds.start, xbounds.stop, ybounds.stop]
    content_type = getattr(tilestore, "content_type", "image/jpeg")
    if content_type == "application/json":
        return dict(extent=extent, maxlod=maxlod, name=name, type="elevation")
    elif content_type == "image/jpeg" or tilestore.content_type is None:
        return dict(extent=extent, format="jpg", maxlod=maxlod, name=name, type="image")
    elif content_type == "image/png":
        return dict(extent=extent, format="png", maxlod=maxlod, name=name, type="image")
    else:
        assert False


@bottle.route("/openlayers")
@bottle.view("openlayers")
def openlayers():
    return dict(max_extent=max_extent, resolutions=resolutions, tilestores=tilestores)


@bottle.route("/googlemaps")
@bottle.view("googlemaps")
def googlemaps():
    return dict(tilestores=tilestores)


@bottle.route("/jquerygeo")
@bottle.view("jquerygeo")
def jquerygeo():
    return dict(tilestores=tilestores)


@bottle.route("/leaflet")
@bottle.view("leaflet")
def leaflet():
    return dict(tilestores=tilestores)


@bottle.route("/modestmaps")
@bottle.view("modestmaps")
def modestmaps():
    return dict(tilestores=tilestores)


@bottle.route("/polymaps")
@bottle.view("polymaps")
def polymaps():
    return dict(tilestores=tilestores)


@bottle.route("/openwebglobe")
@bottle.view("openwebglobe")
def openwebglobe():
    if "q" in bottle.request.GET:
        quality = float(bottle.request.GET.get("q"))
    else:
        quality = None
    return dict(quality=quality, tilestores=tilestores)


@bottle.route("/favicon.ico")
def favicon():
    return bottle.static_file("favicon.ico", root="static")


@bottle.route("/static/<path:re:.*>")
def static(path):
    return bottle.static_file(path, root="static")


@bottle.route("/")
@bottle.view("index")
def index():
    return dict(debug=bottle.request.GET.get("debug"))


def main() -> None:
    global _root

    option_parser = OptionParser()
    option_parser.add_option("--cache", action="store_true")
    option_parser.add_option("--debug", action="store_true", default=False)
    option_parser.add_option("--root", metavar="Z/X/Y")
    option_parser.add_option("--host", default="127.0.0.1", metavar="HOST")
    option_parser.add_option("--port", default=8080, metavar="PORT", type=int)
    option_parser.add_option("--quiet", action="store_true", default=False)
    option_parser.add_option("--max-extent", metavar="MAX-EXTENT", type=str)
    option_parser.add_option("--resolutions", metavar="RESOLUTIONS", type=str)
    option_parser.add_option("--server", metavar="SERVER")
    options, args = option_parser.parse_args(sys.argv[1:])

    if options.debug:
        bottle.DEBUG = True
    if options.root:
        match = re.match(r"(\d+)/(\d+)/(\d+)\Z", options.root)
        _root = TileCoord(*map(int, match.groups()))
    else:
        _root = TileCoord(0, 0, 0)
    if options.server is None:
        try:
            import tornado.httpserver
            import tornado.ioloop
            import tornado.wsgi

            options.server = "tornado"
            id(tornado)  # Suppress pyflakes warning 'tornado' imported but unused
        except ImportError:
            options.server = "wsgiref"

    global cache, max_extent, resolutions, tilestores, content_type_adder
    cache = {} if options.cache else None
    max_extent = options.max_extent
    resolutions = options.resolutions
    tilestores = [(os.path.basename(arg), TileStore.load(arg)) for arg in args]
    content_type_adder = ContentTypeAdder()

    bottle.TEMPLATE_PATH.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), "views"))
    bottle.run(
        host=options.host,
        port=options.port,
        reloader=options.debug,
        quiet=options.quiet,
        server=options.server,
    )


if __name__ == "__main__":
    main()
