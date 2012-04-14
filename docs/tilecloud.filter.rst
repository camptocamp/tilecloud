Filters
=======

Filters are callables. They receive a tile (:class:`tilecloud.Tile` object) as
their first argument and return a tile. They can act on the tile they receive.
They may return ``None`` to drop the tile.

To filter a time stream use the ``itertools.imap`` function. For example::

    from itertools import imap
    from tilecloud.filter.error import DropErrors

    tilestream = imap(DropErrors(), tilestream)

TileCloud provides a number of filters (filter factories really). See below.

Reference
---------

Error filters
~~~~~~~~~~~~~

.. automodule:: tilecloud.filter.error
   :members:

Image filters
~~~~~~~~~~~~~

.. automodule:: tilecloud.filter.image
  :members:

GZIP filters
~~~~~~~~~~~~

.. automodule:: tilecloud.filter.gzip_
   :members:

Other filters
~~~~~~~~~~~~~

.. automodule:: tilecloud.filter.contenttype
   :members:

.. automodule:: tilecloud.filter.consistenthash
   :members:

.. automodule:: tilecloud.filter.inboundingpyramid
   :members:
