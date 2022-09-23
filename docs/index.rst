.. TileCloud documentation master file, created by
   sphinx-quickstart on Thu Apr 12 22:29:48 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to TileCloud's documentation!
=====================================

TileCloud is a powerful utility for generating, managing, transforming,
visualizing and map tiles in multiple formats.  It can create, read update,
delete tiles in multiple back ends, called *TileStores*. Existing TileStores
include:

* HTTP/REST in any layout
* WMTS
* Amazon `S3 <http://aws.amazon.com/s3/>`_ and `SQS
  <http://aws.amazon.com/sqs/>`_
* `MBTiles <https://github.com/mapbox/mbtiles-spec>`_
* `TileJSON <https://github.com/mapbox/TileJSON>`_
* Local file system
* Log files in any format

TileCloud is not limited to image tiles, it can also handle other tile data
such as `UTFGrid <https://github.com/mapbox/utfgrid-spec>`_, or elevation data in
JSON format.

TileCloud uses Python's generators and iterators to efficiently stream tens of
millions of tiles, and can handle multiple tiles in parallel using Python's
`multiprocessing <http://docs.python.org/library/multiprocessing.html>`_ library.

TileCloud includes command lines, and Python APIs for use in specific commands
or libraries.

Contents:

.. toctree::
   :maxdepth: 1

   command
   api


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
