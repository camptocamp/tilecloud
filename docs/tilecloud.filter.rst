Filters
=======

Filters are callables. They receive a tile as their first argument and return
a tile. They can act on the tile they receive. They may return ``None`` to drop
the tile.

Filter Reference API
--------------------

.. automodule:: tilecloud.filter.error
   :members:

GZIP filters
~~~~~~~~~~~~

.. automodule:: tilecloud.filter.gzip_
   :members:
.. automodule:: tilecloud.filter.contenttype
   :members:

.. automodule:: tilecloud.filter.consistenthash
   :members:

