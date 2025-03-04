#!/usr/bin/env python

import sys
from optparse import OptionParser

from tilecloud import BoundingPyramid, Tile, TileCoord, TileStore


def detect_edge(tilestore, z, first, last, other, horizontal, up):
    while first < last:
        middle = (first + last) // 2
        if horizontal:
            tile = Tile(TileCoord(z, middle, other))
        else:
            tile = Tile(TileCoord(z, other, middle))
        tile_exists = tile in tilestore
        if up:
            if tile_exists:
                last = middle
            else:
                first = middle + 1
        elif tile_exists:
            first = middle + 1
        else:
            last = middle
    return last


def main() -> None:
    option_parser = OptionParser()
    option_parser.add_option("-b", "--bounds", metavar="BOUNDING-PYRAMID")
    option_parser.add_option("-r", "--relative", action="store_true")
    option_parser.add_option("-s", "--seed", metavar="SEED")
    option_parser.add_option("-z", "--zoom", metavar="ZOOM", type=int)
    options, args = option_parser.parse_args()
    bounding_pyramid = BoundingPyramid.from_string(options.bounds)
    z = options.zoom
    if options.seed is None:
        xbounds, ybounds = bounding_pyramid.zget(z)
        seed = TileCoord(z, (xbounds.start + xbounds.stop) // 2, (ybounds.start + ybounds.stop) // 2)
    else:
        seed = TileCoord.from_string(options.seed)
    for arg in args:
        tilestore = TileStore.load(arg)
        xbounds, ybounds = bounding_pyramid.zget(z)
        assert Tile(seed) in tilestore
        xstart = detect_edge(tilestore, z, xbounds.start, seed.x, seed.y, True, True)
        xstop = detect_edge(tilestore, z, seed.x, xbounds.stop, seed.y, True, False)
        ystart = detect_edge(tilestore, z, ybounds.start, seed.y, seed.x, False, True)
        ystop = detect_edge(tilestore, z, seed.y, ybounds.stop, seed.x, False, False)
        if options.relative:
            print("%d/%d/%d:+%d/+%d" % (z, xstart, ystart, xstop - xstart, ystop - ystart))
        else:
            print("%d/%d/%d:%d/%d" % (z, xstart, ystart, xstop, ystop))


if __name__ == "__main__":
    sys.exit(main())
