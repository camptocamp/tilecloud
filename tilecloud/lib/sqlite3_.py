from six.moves import map as imap
from sys import version_info
if version_info[0] == 2:
    from UserDict import DictMixin
else:
    from collections import MutableMapping as DictMixin


def query(connection, *args):
    cursor = connection.cursor()
    cursor.execute(*args)
    return cursor


class SQLiteDict(DictMixin):
    """A dict facade for an SQLite table"""

    def __init__(self, connection, commit=True, **kwargs):
        self.connection = connection
        self.commit = commit
        query(self.connection, self.CREATE_TABLE_SQL)
        if self.commit:
            self.connection.commit()
        self.update(kwargs)

    def __contains__(self, key):
        return query(self.connection,
                     self.CONTAINS_SQL,
                     self._packkey(key)).fetchone()[0]

    def __delitem__(self, key):
        query(self.connection, self.DELITEM_SQL, self._packkey(key))
        if self.commit:
            self.connection.commit()

    def __getitem__(self, key):
        row = query(self.connection,
                    self.GETITEM_SQL,
                    self._packkey(key)).fetchone()
        if row is None:
            raise KeyError(key)
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
        return imap(self._unpackitem,
                    query(self.connection,
                          self.ITERITEMS_SQL))

    def itervalues(self):
        return imap(self._unpackvalue,
                    query(self.connection,
                          self.ITERVALUES_SQL))

    def keys(self):
        return list(iter(self))

    @staticmethod
    def _packitem(key, value):
        return (key, value)

    @staticmethod
    def _packkey(key):
        return (key,)

    @staticmethod
    def _packvalue(value):  # pragma: no cover
        return (value,)

    @staticmethod
    def _unpackitem(row):  # pragma: no cover
        return row

    @staticmethod
    def _unpackkey(row):
        return row[0]

    @staticmethod
    def _unpackvalue(row):
        return row[0]
