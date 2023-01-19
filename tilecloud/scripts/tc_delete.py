#!/usr/bin/env python

import logging
import os.path
import sys
from optparse import OptionParser

from tilecloud import BoundingPyramid, TileStore, consume
from tilecloud.filter.logger import Logger
from tilecloud.store.boundingpyramid import BoundingPyramidTileStore


def main() -> None:
    logger = logging.getLogger(os.path.basename(sys.argv[0]))
    option_parser = OptionParser()
    option_parser.add_option("-b", "--bounding-pyramid", metavar="BOUNDING-PYRAMID")
    option_parser.add_option("-v", "--verbose", action="store_true")
    options, args = option_parser.parse_args()
    if options.verbose:
        logging.basicConfig(level=logging.INFO)
    if options.bounding_pyramid:
        bounding_pyramid = BoundingPyramid.from_string(options.bounding_pyramid)
    else:
        bounding_pyramid = None
    for arg in args:
        tilestore = TileStore.load(arg)
        if bounding_pyramid:
            tilestream = BoundingPyramidTileStore(bounding_pyramid).list()
        else:
            tilestream = tilestore.list()
        tilestream = tilestore.delete(tilestream)
        if options.verbose:
            tilestream = map(Logger(logger, logging.INFO, "%(tilecoord)s"), tilestream)
        consume(tilestream, None)


if __name__ == "__main__":
    sys.exit(main())
