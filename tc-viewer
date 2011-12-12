#!/usr/bin/env python

import bottle

from tilecloud import I3DTileLayout
from tilecloud import OSMTileLayout
from tilecloud import S3TileStore
from tilecloud import Tile
from tilecloud import TileCoord
from tilecloud import WrappedTileLayout


tile_stores = []


@bottle.route('/t/<index:int>/<z:int>/<x:int>/<y:int>')
def tile(index, z, x, y):
    if len(tile_stores) < index:
        bottle.abort(404)
    tile = tile_stores[index].get_one(Tile(TileCoord(z, x, y)))
    if tile is None:
        bottle.abort(404)
    if hasattr(tile, 'content_type'):
        bottle.response.set_header('Content-Type', tile.content_type)
    if hasattr(tile, 'content_encoding'):
        bottle.response.set_header('Content-Encoding', tile.content_encoding)
    return tile.data


@bottle.route('/openlayers/<filename:path>')
def openlayers(filename):
    return bottle.static_file(filename, root='./openlayers')


@bottle.route('/')
@bottle.view('index')
def index():
    layers = []
    for tile_store in tile_stores:
        layer = {'name': None}
        if hasattr(tile_store, 'name'):
            layer['name'] = tile_store.name
        elif hasattr(tile_store, 'metadata'):
            layer['name'] = tile_store.metadata.get('name', )
        layers.append(layer)
    return dict(layers=layers)


if __name__ == '__main__':
    bottle.DEBUG = True
    bottle.run(reloader=True)
