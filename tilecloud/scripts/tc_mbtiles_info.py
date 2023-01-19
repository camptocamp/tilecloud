#!/usr/bin/env python

import os.path
import sqlite3
import sys
import textwrap
from optparse import OptionParser

from tilecloud.store.mbtiles import Metadata, Tiles

BOUNDING_PYRAMID_SQL = textwrap.dedent(
    """\
    SELECT
        zoom_level,
        MIN(tile_column),
        MIN(tile_row),
        MAX(tile_column),
        MAX(tile_row),
        COUNT(zoom_level),
        (MAX(tile_column) - MIN(tile_column) + 1) *
         (MAX(tile_row) - MIN(tile_row) + 1)
    FROM
        tiles
    GROUP BY
        zoom_level
    ORDER BY
        zoom_level
    """
)


def main() -> None:
    option_parser = OptionParser()
    option_parser.add_option("-m", "--metadata", action="store_true")
    option_parser.add_option("-t", "--tiles", choices=("bounding-pyramid", "count", "list"))
    options, args = option_parser.parse_args()
    for arg in args:
        assert os.path.exists(arg)
        connection = sqlite3.connect(arg)
        if options.metadata:
            metadata = Metadata(connection)
            for key, value in metadata.iteritems():
                print(f"{key}: {value}")
        if options.tiles:
            if options.tiles == "count":
                print(len(Tiles(connection)))
            elif options.tiles == "bounding-pyramid":
                cursor = connection.cursor()
                cursor.execute(BOUNDING_PYRAMID_SQL)
                for row in cursor:
                    if row[5] == row[6]:
                        extra = ""
                    else:
                        extra = " # %+d" % (row[5] - row[6])
                    print("%d/%d/%d:%d/%d%s" % (row[0], row[1], row[2], row[3], row[4], extra))
            elif options.tiles == "list":
                for key in Tiles(connection):
                    print("%d/%d/%d" % (key.z, key.x, key.y))


if __name__ == "__main__":
    sys.exit(main())
