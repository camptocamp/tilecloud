#!/usr/bin/env python

import fileinput
import sqlite3
from optparse import OptionParser

from tilecloud import BoundingPyramid, consume
from tilecloud.layout.i3d import I3DTileLayout
from tilecloud.layout.osm import OSMTileLayout
from tilecloud.layout.wrapped import WrappedTileLayout
from tilecloud.store.boundingpyramid import BoundingPyramidTileStore
from tilecloud.store.filesystem import FilesystemTileStore
from tilecloud.store.log import LogTileStore
from tilecloud.store.mbtiles import MBTilesTileStore
from tilecloud.store.s3 import S3TileStore


def main() -> None:
    tilelayouts = {"i3d": I3DTileLayout, "osm": OSMTileLayout}
    tilestores = "filesystem log s3".split()
    option_parser = OptionParser()
    option_parser.add_option("--bounds", metavar="Z1/X1/Y1:(Z2/)?X2/Y2")
    option_parser.add_option("--bucket", dest="bucket_name", metavar="BUCKET")
    option_parser.add_option("--layout", choices=tilelayouts.keys(), dest="tilelayout")
    option_parser.add_option("--limit", metavar="LIMIT", type=int)
    option_parser.add_option("--output", default=":memory:", metavar="TILESET")
    option_parser.add_option("--prefix", default="", metavar="STRING")
    option_parser.add_option("--store", choices=tilestores)
    option_parser.add_option("--suffix", default="", metavar="STRING")
    option_parser.add_option("--name", metavar="NAME")
    option_parser.add_option("--type", default="baselayer", choices=("baselayer", "overlay"))
    option_parser.add_option("--version", metavar="VERSION")
    option_parser.add_option("--description", metavar="DESCRIPTION")
    option_parser.add_option("--format", metavar="FORMAT")
    options, args = option_parser.parse_args()
    assert options.store
    tilelayout = tilelayouts[options.tilelayout]()
    if options.prefix or options.suffix:
        tilelayout = WrappedTileLayout(tilelayout, options.prefix, options.suffix)
    if options.store == "filesystem":
        store = FilesystemTileStore(tilelayout)
    elif options.store == "log":
        store = LogTileStore(tilelayout, fileinput.input(args))
    elif options.store == "s3":
        store = S3TileStore(options.bucket_name, tilelayout)
    else:
        raise AssertionError
    if options.bounds:
        bounds = BoundingPyramid.from_string(options.bounds)
        tilestream = BoundingPyramidTileStore(bounds).list()
        tilestream = store.get(tilestream)
    else:
        tilestream = store.get_all()
    connection = sqlite3.connect(options.output)
    mbtiles_tilestore = MBTilesTileStore(connection, commit=False)
    for key in "name type version description format".split():
        value = getattr(options, key)
        if value is not None:
            mbtiles_tilestore.metadata[key] = getattr(options, key)
    tilestream = mbtiles_tilestore.put(tilestream)
    consume(tilestream, options.limit)
    connection.commit()


if __name__ == "__main__":
    main()
