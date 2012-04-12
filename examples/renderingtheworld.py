#!/usr/bin/env python

from itertools import imap
import logging
import os.path
import sys

from tilecloud import Tile, TileCoord, TileStore, consume
from tilecloud.filter.error import DropErrors
from tilecloud.filter.logger import Logger
from tilecloud.store.renderingtheworld import RenderingTheWorldTileStore


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(os.path.basename(sys.argv[0]))


def subdivide(tile):
    return tile.error is None and tile.tilecoord.z < 15


def main(argv):
    input_tile_store = TileStore.load('tiles.medford_buildings')
    output_tile_store = TileStore.load('medford_buildings.mbtiles')
    rendering_the_world_tile_store = RenderingTheWorldTileStore(subdivide, seed=Tile(TileCoord(0, 0, 0)))
    tilestream = rendering_the_world_tile_store.list()
    tilestream = imap(Logger(logger, logging.INFO, 'get %(tilecoord)s'), tilestream)
    tilestream = input_tile_store.get(tilestream)
    tilestream = imap(Logger(logger, logging.INFO, 'got %(tilecoord)s, error=%(error)s'), tilestream)
    tilestream = rendering_the_world_tile_store.put(tilestream)
    tilestream = imap(DropErrors(), tilestream)
    tilestream = output_tile_store.put(tilestream)
    tilestream = imap(Logger(logger, logging.INFO, 'saved %(tilecoord)s'), tilestream)
    consume(tilestream, None)


if __name__ == '__main__':
    sys.exit(main(sys.argv))
