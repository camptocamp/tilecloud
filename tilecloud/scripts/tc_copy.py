#!/usr/bin/env python

import logging
import os.path
import random
import sys
from optparse import OptionParser

from tilecloud import BoundingPyramid, TileStore, consume
from tilecloud.filter.benchmark import Benchmark, StatsCountErrors, StatsCountTiles
from tilecloud.filter.consistenthash import EveryNth
from tilecloud.filter.contenttype import ContentTypeAdder
from tilecloud.filter.error import (
    DropErrors,
    LogErrors,
    MaximumConsecutiveErrors,
    MaximumErrorRate,
    MaximumErrors,
)
from tilecloud.filter.logger import Logger
from tilecloud.filter.rate import RateLimit
from tilecloud.store.boundingpyramid import BoundingPyramidTileStore


def main() -> None:
    logger = logging.getLogger(os.path.basename(sys.argv[0]))
    option_parser = OptionParser()
    option_parser.add_option("--benchmark", action="store_true")
    option_parser.add_option("-b", "--bounding-pyramid", metavar="BOUNDING-PYRAMID")
    option_parser.add_option("--add-content-type", action="store_true")
    option_parser.add_option("-i", metavar="I", type=int)
    option_parser.add_option("-g", "--generate", metavar="TILE-STORE", action="append")
    option_parser.add_option("--limit", metavar="N", type=int)
    option_parser.add_option("-m", "--move", action="store_true")
    option_parser.add_option("--maximum-consecutive-errors", metavar="N", type=int)
    option_parser.add_option("--maximum-errors", metavar="N", type=int)
    option_parser.add_option("--maximum-error-rate", metavar="FLOAT", type=float)
    option_parser.add_option("-n", metavar="N", type=int)
    option_parser.add_option("-o", "--overwrite", action="store_true")
    option_parser.add_option("-r", "--rate-limit", metavar="HZ", type=float)
    option_parser.add_option("--randomize", action="store_true")
    option_parser.add_option("--stats", action="store_true")
    option_parser.add_option("-v", "--verbose", action="store_true")
    options, args = option_parser.parse_args()
    if options.verbose:
        logging.basicConfig(level=logging.INFO)
    else:
        logging.basicConfig(level=logging.WARNING)
    assert len(args) >= 2
    if options.bounding_pyramid:
        bounding_pyramid = BoundingPyramid.from_string(options.bounding_pyramid)
    else:
        bounding_pyramid = None

    benchmark = Benchmark() if options.benchmark else None
    if options.generate:
        generate = map(TileStore.load, options.generate)
    else:
        generate = ()
    try:
        output_tilestore = TileStore.load(args[-1])
        for arg in args[:-1]:
            input_tilestore = TileStore.load(arg, allows_no_contenttype=options.add_content_type)
            if bounding_pyramid:
                tilestream = BoundingPyramidTileStore(bounding_pyramid).list()
            else:
                tilestream = input_tilestore.list()
            if options.i is not None and options.n is not None:
                tilestream = map(EveryNth(options.n, options.i), tilestream)
            if options.randomize:
                tilestream = list(tilestream)
                random.shuffle(tilestream)
            if not options.overwrite:
                tilestream = (tile for tile in tilestream if tile not in output_tilestore)
            if options.rate_limit:
                tilestream = map(RateLimit(options.rate_limit), tilestream)
            if benchmark:
                tilestream = map(benchmark.sample(), tilestream)
            tilestream = input_tilestore.get(tilestream)
            if benchmark:
                tilestream = map(benchmark.sample("get"), tilestream)
            for i, g in enumerate(generate):
                tilestream = g.get(tilestream)
                if options.benchmark:
                    tilestream = map(benchmark.sample("generate-%d" % (i,)), tilestream)
            tilestream = map(LogErrors(logger, logging.ERROR, "%(tilecoord)s: %(error)s"), tilestream)
            if options.stats:
                tilestream = map(StatsCountErrors(), tilestream)
            if options.maximum_consecutive_errors:
                tilestream = map(MaximumConsecutiveErrors(options.maximum_consecutive_errors), tilestream)
            if options.maximum_error_rate:
                tilestream = map(MaximumErrorRate(options.maximum_error_rate), tilestream)
            if options.maximum_errors:
                tilestream = map(MaximumErrors(options.maximum_errors), tilestream)
            tilestream = map(DropErrors(), tilestream)
            if options.add_content_type:
                tilestream = map(ContentTypeAdder(), tilestream)
            tilestream = output_tilestore.put(tilestream)
            if benchmark:
                tilestream = map(benchmark.sample("put"), tilestream)
            if options.move:
                tilestream = input_tilestore.delete(tilestream)
                if benchmark:
                    tilestream = map(benchmark.sample("delete"), tilestream)
            if options.verbose:
                tilestream = map(Logger(logger, logging.INFO, "%(tilecoord)s"), tilestream)
            if options.stats:
                tilestream = map(StatsCountTiles(), tilestream)
            consume(tilestream, options.limit)
    finally:
        logging.basicConfig(level=logging.INFO)
        if benchmark:
            keys = ["get"]
            keys.extend("generate-%i" % (i,) for i in range(0, len(generate)))
            keys.extend(["put", "delete"])
            for key in keys:
                if key in benchmark.statisticss:
                    statistics = benchmark.statisticss[key]
                    logger.info(
                        "%s: %s%s"
                        % (
                            key,
                            statistics,
                            f" ({1.0 / statistics.mean:.1f} tiles/s)" if statistics.n else "",
                        )
                    )


if __name__ == "__main__":
    sys.exit(main())
