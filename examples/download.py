#!/usr/bin/env python

import logging
import os.path
import sys

from tilecloud import BoundingPyramid, TileStore, consume
from tilecloud.filter.logger import Logger
from tilecloud.store.boundingpyramid import BoundingPyramidTileStore

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(os.path.basename(sys.argv[0]))


def main() -> None:
    # Create our input and output TileStores
    input_tilestore = TileStore.load("tiles.openstreetmap_org")
    output_tilestore = TileStore.load("local.mbtiles")
    # 1. Generate a list of tiles to download from a BoundingPyramid
    #    4/8/5 is the root tile, corresponding to Central Europe
    #    +3/+1/+1 specifies up to zoom level 4 + 3 = 7 and an extent of one tile in the X and Y directions
    bounding_pyramid = BoundingPyramid.from_string("4/8/5:+3/+1/+1")
    bounding_pyramid_tilestore = BoundingPyramidTileStore(bounding_pyramid)
    tilestream1 = bounding_pyramid_tilestore.list()
    # 2. Filter out tiles that already downloaded
    tilestream2 = (tile for tile in tilestream1 if tile not in output_tilestore)
    # 3. Get the tile from openstreetmap.org
    tilestream3 = input_tilestore.get(tilestream2)
    # 4. Save the tile to local.mbtiles
    tilestream4 = output_tilestore.put(filter(None, tilestream3))
    # 5. Log the fact that the tile was downloaded
    tilestream5 = map(Logger(logger, logging.INFO, "downloaded %(tilecoord)s"), tilestream4)
    # Go!
    consume(tilestream5, None)


if __name__ == "__main__":
    main()
