# http://mbtiles.org/

from itertools import imap
import mimetypes
import sqlite3
import UserDict

from tilecloud import Tile, TileCoord, TileStore



def query(connection, *args):
    cursor = connection.cursor()
    cursor.execute(*args)
    return cursor



class SQLiteDict(UserDict.DictMixin):
    """A dict facade for an SQLite table"""

    def __init__(self, connection, commit=True, **kwargs):
        self.connection = connection
        self.commit = commit
        query(self.connection, self.CREATE_TABLE_SQL)
        if self.commit:
            self.connection.commit()
        self.update(kwargs)

    def __contains__(self, key):
        return query(self.connection, self.CONTAINS_SQL, self._packkey(key)).fetchone()[0]

    def __delitem__(self, key):
        query(self.connection, self.DELITEM_SQL, self._packkey(key))
        if self.commit:
            self.connection.commit()

    def __getitem__(self, key):
        row = query(self.connection, self.GETITEM_SQL, self._packkey(key)).fetchone()
        if row is None:
            raise KeyError, key
        return self._unpackvalue(row)

    def __iter__(self):
        return imap(self._unpackkey, query(self.connection, self.ITER_SQL))

    def __len__(self):
        return query(self.connection, self.LEN_SQL).fetchone()[0]

    def __setitem__(self, key, value):
        query(self.connection, self.SETITEM_SQL, self._packitem(key, value))
        if self.commit:
            self.connection.commit()

    def iteritems(self):
        return imap(self._unpackitem, query(self.connection, self.ITERITEMS_SQL))

    def itervalues(self):
        return imap(self._unpackvalue, query(self.connection, self.ITERVALUES_SQL))

    def keys(self):
        return list(iter(self))

    def _packitem(self, key, value):
        return (key, value)

    def _packkey(self, key):
        return (key,)

    def _packvalue(self, value):
        return (value,)

    def _unpackitem(self, row):
        return row

    def _unpackkey(self, row):
        return row[0]

    def _unpackvalue(self, row):
        return row[0]



class Metadata(SQLiteDict):
    """A dict facade for the metadata table"""

    CREATE_TABLE_SQL = 'CREATE TABLE IF NOT EXISTS metadata (name text, value text, PRIMARY KEY (name))'
    CONTAINS_SQL = 'SELECT COUNT(*) FROM metadata WHERE name = ?'
    DELITEM_SQL = 'DELETE FROM metadata WHERE name = ?'
    GETITEM_SQL = 'SELECT value FROM metadata WHERE name = ?'
    ITER_SQL = 'SELECT name FROM metadata'
    ITERITEMS_SQL = 'SELECT name, value FROM metadata'
    ITERVALUES_SQL = 'SELECT value FROM metadata'
    LEN_SQL = 'SELECT COUNT(*) FROM metadata'
    SETITEM_SQL = 'INSERT OR REPLACE INTO metadata (name, value) VALUES (?, ?)'



class Tiles(SQLiteDict):
    """A dict facade for the tiles table"""

    CREATE_TABLE_SQL = 'CREATE TABLE IF NOT EXISTS tiles (zoom_level integer, tile_column integer, tile_row integer, tile_data blob, PRIMARY KEY (zoom_level, tile_column, tile_row))'
    CONTAINS_SQL = 'SELECT COUNT(*) FROM tiles WHERE zoom_level = ? AND tile_column = ? AND tile_row = ?'
    DELITEM_SQL = 'DELETE FROM tiles WHERE zoom_level = ? AND tile_column = ? AND tile_row = ?'
    GETITEM_SQL = 'SELECT tile_data FROM tiles WHERE zoom_level = ? AND tile_column = ? AND tile_row = ?'
    ITER_SQL = 'SELECT zoom_level, tile_column, tile_row FROM tiles'
    ITERITEMS_SQL = 'SELECT zoom_level, tile_column, tile_row, tile_data FROM tiles'
    ITERVALUES_SQL = 'SELECT tile_data FROM tiles'
    LEN_SQL = 'SELECT COUNT(*) FROM tiles'
    SETITEM_SQL = 'INSERT OR REPLACE INTO tiles (zoom_level, tile_column, tile_row, tile_data) VALUES (?, ?, ?, ?)'

    def _packitem(self, key, value):
        return (key.z, key.x, (1 << key.z) - key.y - 1, sqlite3.Binary(value) if value is not None else None)

    def _packkey(self, key):
        return (key.z, key.x, (1 << key.z) - key.y - 1)

    def _unpackitem(self, row):
        z, x, y, data = row
        return (TileCoord(z, x, (1 << z) - y - 1), data)
    
    def _unpackkey(self, row):
        z, x, y = row
        return TileCoord(z, x, (1 << z) - y - 1)



class MBTilesTileStore(TileStore):
    """A MBTiles tile store"""

    def __init__(self, connection, commit=True, **kwargs):
        self.connection = connection
        self.metadata = Metadata(self.connection, commit, **kwargs)
        if 'format' in self.metadata:
            self.content_type = mimetypes.types_map.get('.' + self.metadata['format'], None)
        else:
            self.content_type = None
        self.tiles = Tiles(self.connection, commit)

    def delete_one(self, tile):
        del self.tiles[tile.tilecoord]
        return tile

    def get_all(self):
        for tilecoord, data in self.tiles.iteritems():
            tile = Tile(tilecoord, data=data)
            if self.content_type is not None:
                tile.content_type = self.content_type
            yield tile

    def get_one(self, tile):
        try:
            tile = Tile(tile.tilecoord, data=self.tiles[tile.tilecoord])
        except KeyError:
            return None
        if self.content_type is not None:
            tile.content_type = self.content_type
        return tile

    def list(self):
        return (Tile(tilecoord) for tilecoord in self.tiles)

    def put_one(self, tile):
        self.tiles[tile.tilecoord] = getattr(tile, 'data', None)
        return tile
