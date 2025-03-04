#!/usr/bin/env python

import sys
from collections import defaultdict
from operator import attrgetter
from optparse import OptionParser

from tilecloud import BoundingPyramid, TileStore


def main() -> None:
    option_parser = OptionParser()
    option_parser.add_option("-b", "--bounding-pyramid", metavar="BOUNDING-PYRAMID")
    option_parser.add_option("-r", "--relative", action="store_true")
    option_parser.add_option(
        "-t",
        "--tiles",
        choices=("bounding-pyramid", "completion", "count", "estimate-completion", "list"),
    )
    options, args = option_parser.parse_args()
    for arg in args:
        tilestore = TileStore.load(arg)
        if options.tiles == "bounding-pyramid":
            bounding_pyramid = tilestore.bounding_pyramid
            if bounding_pyramid is None:
                bounding_pyramid = tilestore.get_cheap_bounding_pyramid()
            if bounding_pyramid is None:
                bounding_pyramid = tilestore.get_bounding_pyramid()
            for z in sorted(bounding_pyramid.zs()):
                xbounds, ybounds = bounding_pyramid.zget(z)
                if options.relative:
                    print(
                        "%d/%d/%d:%+d/%+d"
                        % (
                            z,
                            xbounds.start,
                            ybounds.start,
                            xbounds.stop - xbounds.start,
                            ybounds.stop - ybounds.start,
                        ),
                    )
                else:
                    print("%d/%d/%d:%d/%d" % (z, xbounds.start, ybounds.start, xbounds.stop, ybounds.stop))
        elif options.tiles == "completion":
            bounding_pyramid = BoundingPyramid.from_string(options.bounding_pyramid)
            completed = defaultdict(set)
            for tilecoord in map(attrgetter("tilecoord"), tilestore.list()):
                completed[tilecoord.z].add((tilecoord.x, tilecoord.y))
            for z in bounding_pyramid.zs():
                numerator = len(completed[z])
                dxbounds, dybounds = bounding_pyramid.zget(z)
                denominator = len(dxbounds) * len(dybounds)
                print("%d %d/%d (%d%%)" % (z, numerator, denominator, 100 * numerator / denominator))
        elif options.tiles == "count":
            print(len(tilestore))
        elif options.tiles == "estimate-completion":
            bounding_pyramid = BoundingPyramid.from_string(options.bounding_pyramid)
            tilestore_bounding_pyramid = tilestore.get_cheap_bounding_pyramid()
            for z in bounding_pyramid.zs():
                try:
                    nxbounds, nybounds = tilestore_bounding_pyramid.zget(z)
                    numerator = len(nxbounds) * len(nybounds)
                except IndexError:
                    numerator = 0
                dxbounds, dybounds = bounding_pyramid.zget(z)
                denominator = len(dxbounds) * len(dybounds)
                print("%d %d/%d (%d%%)" % (z, numerator, denominator, 100 * numerator / denominator))
        elif options.tiles == "list":
            for tile in tilestore.list():
                print(tile.tilecoord)


if __name__ == "__main__":
    sys.exit(main())
