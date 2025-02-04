from collections.abc import Iterator, KeysView, MutableMapping
from sqlite3 import Connection, Cursor
from typing import TYPE_CHECKING, Any, Optional, Union

from tilecloud import TileCoord

# For me this class can't works!
# flake8: noqa


def _query(connection: Connection, *args: Any) -> Cursor:
    cursor = connection.cursor()
    cursor.execute(*args)
    return cursor


if TYPE_CHECKING:
    Base = MutableMapping[Union[str, TileCoord], Optional[bytes]]
else:
    Base = MutableMapping


class SQLiteDict(Base):
    """A dict facade for an SQLite table."""

    def __init__(
        self,
        connection: Connection,
        commit: bool = True,
        **kwargs: bytes,
    ) -> None:
        self.connection = connection
        self.commit = commit
        _query(self.connection, self.CREATE_TABLE_SQL)  # pylint: disable=no-member # type: ignore[attr-defined]
        if self.commit:
            self.connection.commit()
        # Convert a Dict to a Mapping
        self.update({k: v for k, v in kwargs.items()})  # pylint: disable=unnecessary-comprehension

    def __contains__(self, key: Union[str, TileCoord]) -> bool:
        return _query(self.connection, self.CONTAINS_SQL, self._packkey(key)).fetchone()[0]  # pylint: disable=no-member   # type: ignore[attr-defined]

    def __delitem__(self, key: Union[str, TileCoord]) -> None:
        _query(self.connection, self.DELITEM_SQL, self._packkey(key))  # pylint: disable=no-member   # type: ignore[attr-defined]
        if self.commit:
            self.connection.commit()

    def __getitem__(self, key: Union[str, TileCoord]) -> Optional[bytes]:
        row = _query(self.connection, self.GETITEM_SQL, self._packkey(key)).fetchone()  # pylint: disable=no-member   # type: ignore[attr-defined]
        if row is None:
            return None
        return self._unpackvalue(row)

    def __iter__(self) -> Iterator[str]:
        return map(self._unpackkey, _query(self.connection, self.ITER_SQL))  # pylint: disable=no-member   # type: ignore[attr-defined]

    def __len__(self) -> int:
        return _query(self.connection, self.LEN_SQL).fetchone()[0]  # pylint: disable=no-member   # type: ignore[attr-defined]

    def __setitem__(self, key: Union[str, TileCoord], value: Any) -> None:
        _query(self.connection, self.SETITEM_SQL, self._packitem(key, value))  # pylint: disable=no-member   # type: ignore[attr-defined]
        if self.commit:
            self.connection.commit()

    def iteritems(self) -> Iterator[Cursor]:
        return map(self._unpackitem, _query(self.connection, self.ITERITEMS_SQL))  # pylint: disable=no-member   # type: ignore[attr-defined]

    def itervalues(self) -> Iterator[tuple[bytes]]:
        return map(self._unpackvalue, _query(self.connection, self.ITERVALUES_SQL))  # pylint: disable=no-member   # type: ignore[attr-defined]

    def keys(self) -> KeysView[str]:
        return set(iter(self))

    def _packitem(self, key: TileCoord, value: Optional[bytes]) -> tuple[int, int, int, Optional[memoryview]]:
        return (key, value)

    def _packkey(self, key: TileCoord) -> tuple[int, int, int]:
        return (key,)

    @staticmethod
    def _packvalue(value: Any) -> tuple[Any]:  # pragma: no cover
        return (value,)

    def _unpackitem(self, row: tuple[int, int, int, bytes]) -> tuple[TileCoord, bytes]:  # pragma: no cover
        return row  # type: ignore

    def _unpackkey(self, row: tuple[int, int, int]) -> TileCoord:
        return row[0]  # type: ignore

    @staticmethod
    def _unpackvalue(row: tuple[bytes]) -> bytes:
        return row[0]
