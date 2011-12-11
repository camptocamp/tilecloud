#!/usr/bin/env python

from itertools import chain
from optparse import OptionParser
import sqlite3
import sys

from mbtiles import MBTilesTileStore
from tilecloud import MaskTileStore
from tilecloud import BoundingBoxTileStore
from tilecloud import consume


def main(argv):
    option_parser = OptionParser()
    option_parser.add_option('--limit', metavar='LIMIT', type=int)
    option_parser.add_option('--output', metavar='FILENAME')
    option_parser.add_option('-z', metavar='Z', type=int)
    options, args = option_parser.parse_args(argv[1:])
    assert options.output
    assert options.z
    mbtiles_tile_stores = [MBTilesTileStore(sqlite3.connect(arg)) for arg in args]
    bounding_box = BoundingBoxTileStore()
    tilestream = chain(*(mbtiles_tile_store.list() for mbtiles_tile_store in mbtiles_tile_stores))
    tilestream = bounding_box.put(tilestream)
    consume(tilestream, options.limit)
    mask_tile_store = MaskTileStore(options.z, bounding_box.bounds[options.z])
    tilestream = chain(*(mbtiles_tile_store.list() for mbtiles_tile_store in mbtiles_tile_stores))
    tilestream = mask_tile_store.put(tilestream)
    consume(tilestream, options.limit)
    mask_tile_store.save(options.output, 'PNG')


if __name__ == '__main__':
    sys.exit(main(sys.argv))
