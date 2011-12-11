#!/usr/bin/env python

import fileinput
from optparse import OptionParser
import sqlite3
import sys

from mbtiles import MBTilesTileStore
from tilecloud import consume
from tilecloud import I3DTileLayout
from tilecloud import LinesTileStore
from tilecloud import OSMTileLayout
from tilecloud import WrappedTileLayout


def main(argv):
    tile_layouts = {'i3d': I3DTileLayout(), 'osm': OSMTileLayout()}
    option_parser = OptionParser()
    option_parser.add_option('--layout', choices=tile_layouts.keys(), dest='tile_layout')
    option_parser.add_option('--limit', metavar='LIMIT', type=int)
    option_parser.add_option('--output', default=':memory:', metavar='TILESET')
    option_parser.add_option('--prefix', default='', metavar='STRING')
    option_parser.add_option('--suffix', default='', metavar='STRING')
    options, args = option_parser.parse_args(argv[1:])
    tile_layout = tile_layouts[options.tile_layout]
    if options.prefix or options.suffix:
        tile_layout = WrappedTileLayout(tile_layout, options.prefix, options.suffix)
    connection = sqlite3.connect(options.output)
    mbtiles_tile_store = MBTilesTileStore(connection, commit=False)
    tilestream = LinesTileStore(tile_layout, fileinput.input(args)).list()
    tilestream = mbtiles_tile_store.put(tilestream)
    consume(tilestream, options.limit)
    connection.commit()


if __name__ == '__main__':
    sys.exit(main(sys.argv))
