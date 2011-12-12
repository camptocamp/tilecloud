#!/usr/bin/env python

import fileinput
from optparse import OptionParser
import sqlite3
import sys

from mbtiles import MBTilesTileStore
from tilecloud import BoundingPyramid
from tilecloud import BoundingPyramidTileStore
from tilecloud import FilesystemTileStore
from tilecloud import I3DTileLayout
from tilecloud import LinesTileStore
from tilecloud import OSMTileLayout
from tilecloud import S3TileStore
from tilecloud import WrappedTileLayout
from tilecloud import consume


def main(argv):
    tile_layouts = {'i3d': I3DTileLayout, 'osm': OSMTileLayout}
    tile_stores = 'fs lines s3'.split()
    option_parser = OptionParser()
    option_parser.add_option('--bounds', metavar='Z1/X1/Y1:(Z2/)?X2/Y2')
    option_parser.add_option('--bucket', dest='bucket_name', metavar='BUCKET')
    option_parser.add_option('--layout', choices=tile_layouts.keys(), dest='tile_layout')
    option_parser.add_option('--limit', metavar='LIMIT', type=int)
    option_parser.add_option('--output', default=':memory:', metavar='TILESET')
    option_parser.add_option('--prefix', default='', metavar='STRING')
    option_parser.add_option('--store', choices=tile_stores)
    option_parser.add_option('--suffix', default='', metavar='STRING')
    option_parser.add_option('--name', metavar='NAME')
    option_parser.add_option('--type', default='baselayer', choices=('baselayer', 'overlay'))
    option_parser.add_option('--version', metavar='VERSION')
    option_parser.add_option('--description', metavar='DESCRIPTION')
    option_parser.add_option('--format', metavar='FORMAT')
    options, args = option_parser.parse_args(argv[1:])
    assert options.store
    tile_layout = tile_layouts[options.tile_layout]()
    if options.prefix or options.suffix:
        tile_layout = WrappedTileLayout(tile_layout, options.prefix, options.suffix)
    if options.store == 'fs':
        store = FilesystemTileStore(tile_layout)
    elif options.store == 'lines':
        store = LinesTileStore(tile_layout, fileinput.input(args))
    elif options.store == 's3':
        store = S3TileStore(options.bucket_name, tile_layout)
    else:
        assert False
    if options.bounds:
        bounds = BoundingPyramid.from_string(options.bounds)
        tilestream = BoundingPyramidTileStore(bounds).list()
    else:
        tilestream = store.list()
    connection = sqlite3.connect(options.output)
    kwargs = {}
    mbtiles_tile_store = MBTilesTileStore(connection, commit=False)
    for key in 'name type version description format'.split():
        value = getattr(options, key)
        if value is not None:
            mbtiles_tile_store.metadata[key] = getattr(options, key)
    tilestream = store.get(tilestream)
    tilestream = mbtiles_tile_store.put(tilestream)
    consume(tilestream, options.limit)
    connection.commit()


if __name__ == '__main__':
    sys.exit(main(sys.argv))
