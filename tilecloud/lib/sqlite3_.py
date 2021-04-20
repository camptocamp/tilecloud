from collections import MutableMapping
from sqlite3 import Connection, Cursor
from typing import TYPE_CHECKING, AbstractSet, Any, Iterator, Optional, Tuple, Union

from tilecloud import TileCoord


def query(connection: Connection, *args: Any) -> Cursor:
    cursor = connection.cursor()
    cursor.execute(*args)
    return cursor


if TYPE_CHECKING:
    Base = MutableMapping[Union[str, TileCoord], bytes]
else:
    Base = MutableMapping


class SQLiteDict(Base):
    """A dict facade for an SQLite table"""

    def __init__(
        self,
        connection: Connection,
        commit: bool = True,
        **kwargs: bytes,
    ) -> None:
        self.connection = connection
        self.commit = commit
        query(self.connection, self.CREATE_TABLE_SQL)  # type: ignore
        if self.commit:
            self.connection.commit()
        # Convert a Dict to a Mapping
        self.update({k: v for k, v in kwargs.items()})  # pylint: disable=unnecessary-comprehension

    def __contains__(self, key: Union[str, TileCoord]) -> bool:  # type: ignore
        return query(self.connection, self.CONTAINS_SQL, self._packkey(key)).fetchone()[0]  # type: ignore

    def __delitem__(self, key: Union[str, TileCoord]) -> None:
        query(self.connection, self.DELITEM_SQL, self._packkey(key))  # type: ignore
        if self.commit:
            self.connection.commit()

    def __getitem__(self, key: Union[str, TileCoord]) -> bytes:
        row = query(self.connection, self.GETITEM_SQL, self._packkey(key)).fetchone()  # type: ignore
        if row is None:
            raise KeyError(key)
        return self._unpackvalue(row)

    def __iter__(self) -> Iterator[str]:
        return map(self._unpackkey, query(self.connection, self.ITER_SQL))  # type: ignore

    def __len__(self) -> int:
        return query(self.connection, self.LEN_SQL).fetchone()[0]  # type: ignore

    def __setitem__(self, key: Union[str, TileCoord], value: Any) -> None:
        query(self.connection, self.SETITEM_SQL, self._packitem(key, value))  # type: ignore
        if self.commit:
            self.connection.commit()

    def iteritems(self) -> Iterator[Cursor]:
        return map(self._unpackitem, query(self.connection, self.ITERITEMS_SQL))  # type: ignore

    def itervalues(self) -> Iterator[Tuple[bytes]]:
        return map(self._unpackvalue, query(self.connection, self.ITERVALUES_SQL))  # type: ignore

    def keys(self) -> AbstractSet[str]:
        return set(iter(self))  # type: ignore

    def _packitem(  # pylint: disable=no-self-use
        self, key: TileCoord, value: Optional[bytes]
    ) -> Tuple[int, int, int, Optional[memoryview]]:
        return (key, value)  # type: ignore

    def _packkey(self, key: TileCoord) -> Tuple[int, int, int]:  # pylint: disable=no-self-use
        return (key,)  # type: ignore

    @staticmethod
    def _packvalue(value: Any) -> Tuple[Any]:  # pragma: no cover
        return (value,)

    def _unpackitem(  # pylint: disable=no-self-use
        self, row: Tuple[int, int, int, bytes]
    ) -> Tuple[TileCoord, bytes]:  # pragma: no cover
        return row  # type: ignore

    def _unpackkey(self, row: Tuple[int, int, int]) -> TileCoord:  # pylint: disable=no-self-use
        return row[0]  # type: ignore

    @staticmethod
    def _unpackvalue(row: Tuple[bytes]) -> bytes:
        return row[0]
