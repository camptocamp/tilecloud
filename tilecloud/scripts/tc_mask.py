#!/usr/bin/env python

import sys
from itertools import chain
from optparse import OptionParser

from tilecloud import BoundingPyramid, TileStore, consume
from tilecloud.store.boundingpyramid import BoundingPyramidTileStore
from tilecloud.store.mask import MaskTileStore


def main() -> None:
    option_parser = OptionParser()
    option_parser.add_option("--bounds", metavar="BOUNDS")
    option_parser.add_option("--limit", metavar="LIMIT", type=int)
    option_parser.add_option("--output", metavar="FILENAME")
    option_parser.add_option("-z", metavar="Z", type=int)
    options, args = option_parser.parse_args()
    assert options.output
    assert options.z
    tilestores = map(TileStore.load, args)
    if options.bounds:
        bounding_pyramid = BoundingPyramid.from_string(options.bounds)
    else:
        bounding_pyramid_tilestore = BoundingPyramidTileStore()
        tilestream = chain.from_iterable(ts.list() for ts in tilestores)
        tilestream = bounding_pyramid_tilestore.put(tilestream)
        consume(tilestream, options.limit)
        bounding_pyramid = bounding_pyramid_tilestore.get_bounding_pyramid()
    mask_tilestore = MaskTileStore(options.z, bounding_pyramid.zget(options.z))
    tilestream = chain.from_iterable(ts.list() for ts in tilestores)
    tilestream = mask_tilestore.put(tilestream)
    consume(tilestream, options.limit)
    mask_tilestore.save(options.output, "PNG")


if __name__ == "__main__":
    sys.exit(main())
