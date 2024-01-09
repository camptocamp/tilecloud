#!/usr/bin/env python

import logging
import os.path
import sqlite3
import sys

from tilecloud import Tile, TileCoord, consume
from tilecloud.filter.error import DropErrors
from tilecloud.filter.logger import Logger
from tilecloud.store.mbtiles import MBTilesTileStore
from tilecloud.store.renderingtheworld import RenderingTheWorldTileStore
from tilecloud.store.wmts import WMTSTileStore

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(os.path.basename(sys.argv[0]))


def subdivide(tile: Tile) -> bool:
    # Return true if tile should be subdivided.
    # In our case, the WMTS server returns a 400 Bad Request error if there is no data in this tile.
    # We also don't want to go any further than zoom level 15.
    return tile.error is None and tile.tilecoord.z < 15


def main() -> None:
    # Create our RenderingTheWorld tile store that will manage the queue and subdivision.
    # We pass it the function that decides whether a tile should be subdivided, and an initial tile.
    rendering_the_world_tilestore = RenderingTheWorldTileStore(subdivide, seeds=(Tile(TileCoord(0, 0, 0)),))
    # Start the tilestream by getting a list of all tiles to be generated.
    tilestream1 = rendering_the_world_tilestore.list()
    tilestream2 = map(Logger(logger, logging.INFO, "get %(tilecoord)s"), tilestream1)
    # Create the tile store that will generate our tiles, in this case it's a demo WMTS server at OpenGeo.
    # Getting tiles from this store will either return the tile as a PNG file, or set an error on the tile
    # if there are no features in this tile.
    generate_tilestore = WMTSTileStore(
        url="http://v2.suite.opengeo.org/geoserver/gwc/service/wmts/",
        layer="medford:buildings",
        style="_null",
        format_pattern="image/png",
        tile_matrix_set="EPSG:900913",
        tile_matrix=lambda z: f"EPSG:900913:{z:d}",
    )
    tilestream3 = generate_tilestore.get(tilestream2)
    tilestream4 = map(Logger(logger, logging.INFO, "got %(tilecoord)s, error=%(error)s"), tilestream3)
    # Put the tile back into the RenderingTheWorld tile store.  This check whether the tile should be
    # subdivided, and, if so, adds the tile's children to the list of tiles to be generated.
    tilestream5 = rendering_the_world_tilestore.put(filter(None, tilestream4))
    # Get rid of tiles that returned an error (i.e. where there was no data).
    tilestream6 = map(DropErrors(), tilestream5)
    # Store the generated tiles in the output tile store, in our case a local MBTiles file.
    output_tilestore = MBTilesTileStore(sqlite3.connect("medford_buildings.mbtiles"))
    tilestream7 = output_tilestore.put(filter(None, tilestream6))
    tilestream8 = map(Logger(logger, logging.INFO, "saved %(tilecoord)s"), tilestream7)
    # Go!
    consume(tilestream8, None)


if __name__ == "__main__":
    main()
