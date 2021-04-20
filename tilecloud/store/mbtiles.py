# http://mbtiles.org/

import mimetypes
import sqlite3
from sqlite3 import Connection
from typing import Any, Iterator, Optional, Tuple

from tilecloud import BoundingPyramid, Bounds, Tile, TileCoord, TileStore
from tilecloud.lib.sqlite3_ import SQLiteDict, query


class Metadata(SQLiteDict):
    """A dict facade for the metadata table"""

    CREATE_TABLE_SQL = "CREATE TABLE IF NOT EXISTS metadata (name text, value text, PRIMARY KEY (name))"
    CONTAINS_SQL = "SELECT COUNT(*) FROM metadata WHERE name = ?"
    DELITEM_SQL = "DELETE FROM metadata WHERE name = ?"
    GETITEM_SQL = "SELECT value FROM metadata WHERE name = ?"
    ITER_SQL = "SELECT name FROM metadata"
    ITERITEMS_SQL = "SELECT name, value FROM metadata"
    ITERVALUES_SQL = "SELECT value FROM metadata"
    LEN_SQL = "SELECT COUNT(*) FROM metadata"
    SETITEM_SQL = "INSERT OR REPLACE INTO metadata (name, value) VALUES (?, ?)"


class Tiles(SQLiteDict):
    """A dict facade for the tiles table"""

    CREATE_TABLE_SQL = (
        "CREATE TABLE IF NOT EXISTS tiles (zoom_level integer, tile_column integer, "
        "tile_row integer, tile_data blob, PRIMARY KEY (zoom_level, tile_column, tile_row))"
    )
    CONTAINS_SQL = "SELECT COUNT(*) FROM tiles WHERE zoom_level = ? AND tile_column = ? AND tile_row = ?"
    DELITEM_SQL = "DELETE FROM tiles WHERE zoom_level = ? AND tile_column = ? AND tile_row = ?"
    GETITEM_SQL = "SELECT tile_data FROM tiles WHERE zoom_level = ? AND tile_column = ? AND tile_row = ?"
    ITER_SQL = "SELECT zoom_level, tile_column, tile_row FROM tiles"
    ITERITEMS_SQL = "SELECT zoom_level, tile_column, tile_row, tile_data FROM tiles"
    ITERVALUES_SQL = "SELECT tile_data FROM tiles"
    LEN_SQL = "SELECT COUNT(*) FROM tiles"
    SETITEM_SQL = (
        "INSERT OR REPLACE INTO tiles (zoom_level, tile_column, tile_row, tile_data) VALUES (?, ?, ?, ?)"
    )

    def __init__(self, tilecoord_in_topleft: bool, *args: Any, **kwargs: Any) -> None:
        self.tilecoord_in_topleft = tilecoord_in_topleft
        SQLiteDict.__init__(self, *args, **kwargs)

    def _packitem(self, key: TileCoord, value: Optional[bytes]) -> Tuple[int, int, int, Optional[memoryview]]:
        y = key.y if self.tilecoord_in_topleft else (1 << key.z) - key.y - 1
        return (key.z, key.x, y, sqlite3.Binary(value) if value is not None else None)

    def _packkey(self, key: TileCoord) -> Tuple[int, int, int]:
        y = key.y if self.tilecoord_in_topleft else (1 << key.z) - key.y - 1
        return (key.z, key.x, y)

    def _unpackitem(self, row: Tuple[int, int, int, bytes]) -> Tuple[TileCoord, bytes]:
        z, x, y, data = row
        y = y if self.tilecoord_in_topleft else (1 << z) - y - 1
        return (TileCoord(z, x, y), data)

    def _unpackkey(self, row: Tuple[int, int, int]) -> TileCoord:
        z, x, y = row
        y = y if self.tilecoord_in_topleft else (1 << z) - y - 1
        return TileCoord(z, x, y)


class MBTilesTileStore(TileStore):
    """A MBTiles tile store"""

    BOUNDING_PYRAMID_SQL = (
        "SELECT zoom_level, MIN(tile_column), MAX(tile_column) + 1, "
        "MIN((1 << zoom_level) - tile_row - 1), MAX((1 << zoom_level) - tile_row - 1) + 1 "
        "FROM tiles GROUP BY zoom_level ORDER BY zoom_level"
    )
    SET_METADATA_ZOOMS_SQL = "SELECT MIN(zoom_level), MAX(zoom_level) FROM tiles"

    def __init__(
        self, connection: Connection, commit: bool = True, tilecoord_in_topleft: bool = False, **kwargs: Any
    ) -> None:
        self.connection = connection
        self.metadata = Metadata(self.connection, commit)
        self.tiles = Tiles(tilecoord_in_topleft, self.connection, commit)
        if "content_type" not in kwargs and "format" in self.metadata:
            kwargs["content_type"] = mimetypes.types_map.get("." + self.metadata["format"])  # type: ignore
        TileStore.__init__(self, **kwargs)

    def __contains__(self, tile: Tile) -> bool:
        return tile and tile.tilecoord in self.tiles  # type: ignore

    def __len__(self) -> int:
        return len(self.tiles)

    def delete_one(self, tile: Tile) -> Tile:
        del self.tiles[tile.tilecoord]
        return tile

    def get_all(self) -> Iterator[Tile]:
        for tilecoord, data in self.tiles.iteritems():
            tile = Tile(tilecoord, data=data)
            if self.content_type is not None:
                tile.content_type = self.content_type
            yield tile

    def get_cheap_bounding_pyramid(self) -> BoundingPyramid:
        bounds = {}
        for z, xstart, xstop, ystart, ystop in query(self.connection, self.BOUNDING_PYRAMID_SQL):
            bounds[z] = (Bounds(xstart, xstop), Bounds(ystart, ystop))
        return BoundingPyramid(bounds)

    def get_one(self, tile: Tile) -> Optional[Tile]:
        try:
            tile.data = self.tiles[tile.tilecoord]
        except KeyError:
            return None
        if self.content_type is not None:
            tile.content_type = self.content_type
        return tile

    def list(self) -> Iterator[Tile]:
        return (Tile(tilecoord) for tilecoord in self.tiles)  # type: ignore

    def put_one(self, tile: Tile) -> Tile:
        self.tiles[tile.tilecoord] = getattr(tile, "data", None)
        return tile

    def set_metadata_zooms(self) -> None:
        for minzoom, maxzoom in query(self.connection, self.SET_METADATA_ZOOMS_SQL):
            self.metadata["minzoom"] = minzoom
            self.metadata["maxzoom"] = maxzoom
