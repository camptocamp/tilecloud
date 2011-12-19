#!/usr/bin/python

from itertools import imap, islice
import logging
import multiprocessing
import os.path
import sqlite3
import sys

from tilecloud import BoundingPyramid, Tile, consume
from tilecloud.filter.image import ImageFormatConverter
from tilecloud.filter.logger import Logger
from tilecloud.store.boundingpyramid import BoundingPyramidTileStore
from tilecloud.store.mbtiles import MBTilesTileStore


if __name__ == '__main__':
    logger = logging.getLogger(os.path.basename(sys.argv[0]))
else:
    logger = logging.getLogger(__name__)


from tiles.map3d.png_s3 import tile_store as input_tile_store
from tiles.map3d.jpg_s3 import tile_store as output_tile_store
done_tile_store = MBTilesTileStore(sqlite3.connect('map3d.done.mbtiles'))


convert_to_jpeg_quality85 = ImageFormatConverter('image/jpeg', quality=85)
convert_to_jpeg_quality100 = ImageFormatConverter('image/jpeg', quality=100)


def convert_to_jpeg_and_put_if_not_transparent(tile):
    tilecoord = tile.tilecoord
    tile = input_tile_store.get_one(tile)
    if tile is None:
        logger.warn('missing %s' % (tilecoord,))
    elif tile.s3key.headers['ETag'] == '"f90b26e2519742ebd9630a35aa01156e"':
        logger.warn('transparent %s' % (tilecoord,))
    else:
        if tile.tilecoord.z <= 17:
            tile = convert_to_jpeg_quality85(tile)
        else:
            tile = convert_to_jpeg_quality100(tile)
        tile = output_tile_store.put_one(tile)
    return Tile(tilecoord)


def main(argv):
    logging.basicConfig(format='%(asctime)s:%(levelname)s:%(module)s:%(message)s', level=logging.INFO)
    bounding_pyramid = BoundingPyramid.from_string('17/67407/45436:69714/46944')
    bounding_pyramid_tile_store = BoundingPyramidTileStore(bounding_pyramid)
    tilestream = bounding_pyramid_tile_store.list()
    done_tilecoordtuples = set(tile.tilecoord.tuple() for tile in done_tile_store.list())
    tilestream = (tile for tile in tilestream if tile.tilecoord.tuple() not in done_tilecoordtuples)
    tilestream = multiprocessing.Pool(8).imap_unordered(convert_to_jpeg_and_put_if_not_transparent, tilestream)
    tilestream = imap(Logger(logger, logging.INFO, 'wrote %(tilecoord)s'), tilestream)
    tilestream = done_tile_store.put(tilestream)
    consume(tilestream, None)


if __name__ == '__main__':
    sys.exit(main(sys.argv))
