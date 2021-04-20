from collections import MutableMapping as DictMixin
from sqlite3 import Connection, Cursor
from typing import Any, List, Tuple, Union


def query(connection: Connection, *args: Any) -> Cursor:
    cursor = connection.cursor()
    cursor.execute(*args)
    return cursor


class SQLiteDict(DictMixin):
    """A dict facade for an SQLite table"""

    def __init__(self, connection: Connection, commit: bool = True, **kwargs: Any) -> None:
        self.connection = connection
        self.commit = commit
        query(self.connection, self.CREATE_TABLE_SQL)
        if self.commit:
            self.connection.commit()
        self.update(kwargs)

    def __contains__(self, key: Union[str, TileCoord]) -> int:
        return query(self.connection, self.CONTAINS_SQL, self._packkey(key)).fetchone()[0]

    def __delitem__(self, key: TileCoord) -> None:
        query(self.connection, self.DELITEM_SQL, self._packkey(key))
        if self.commit:
            self.connection.commit()

    def __getitem__(self, key: Union[str, TileCoord]) -> Union[None, bytes, str]:
        row = query(self.connection, self.GETITEM_SQL, self._packkey(key)).fetchone()
        if row is None:
            raise KeyError(key)
        return self._unpackvalue(row)

    def __iter__(self) -> map:
        return map(self._unpackkey, query(self.connection, self.ITER_SQL))

    def __len__(self) -> int:
        return query(self.connection, self.LEN_SQL).fetchone()[0]

    def __setitem__(self, key: Union[str, TileCoord], value: Any) -> None:
        query(self.connection, self.SETITEM_SQL, self._packitem(key, value))
        if self.commit:
            self.connection.commit()

    def iteritems(self) -> map:
        return map(self._unpackitem, query(self.connection, self.ITERITEMS_SQL))

    def itervalues(self) -> map:
        return map(self._unpackvalue, query(self.connection, self.ITERVALUES_SQL))

    def keys(self) -> List[str]:
        return list(iter(self))

    @staticmethod
    def _packitem(key: str, value: Union[int, str]) -> Tuple[str, Union[int, str]]:
        return (key, value)

    @staticmethod
    def _packkey(key: str) -> Tuple[str]:
        return (key,)

    @staticmethod
    def _packvalue(value):  # pragma: no cover
        return (value,)

    @staticmethod
    def _unpackitem(row):  # pragma: no cover
        return row

    @staticmethod
    def _unpackkey(row: Tuple[str]) -> str:
        return row[0]

    @staticmethod
    def _unpackvalue(row: Tuple[Union[None, bytes, str]]) -> Union[None, bytes, str]:
        return row[0]
