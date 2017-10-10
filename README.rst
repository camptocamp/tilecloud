TileCloud
=========

A powerful utility for generating, managing, transforming, and
visualizing map tiles in multiple formats.

.. image:: https://api.travis-ci.org/camptocamp/tilecloud.png?branch=master
   :alt: Travis CI Status
   :target: http://travis-ci.org/#!/camptocamp/tilecloud

Introduction
============

TileCloud is a powerful utility for generating, managing,
transforming, visualising and map tiles in multiple formats. It can
create, read update, delete tiles in multiple back ends, called
TileStores. Existing TileStores include:


-  HTTP/REST in any layout

-  WMTS

-  Amazon `S3 <http://aws.amazon.com/s3/>`_ and
   `SQS <http://aws.amazon.com/sqs/>`_

-  `MBTiles <https://github.com/mapbox/mbtiles-spec>`_

-  `TileJSON <https://github.com/mapbox/TileJSON>`_

-  `Mapnik <http://mapnik.org/>`_ (via
   `mapnik2 <http://pypi.python.org/pypi/mapnik2>`_)

-  `Memcached <http://memcached.org/>`_

-  Local file system

-  Log files in any format


TileCloud is not limited to image tiles, it can also handle other
tile data such as
`UTFGrid <https://github.com/mapbox/utfgrid-spec>`_, or elevation
data in JSON format.

TileCloud uses Python's generators and iterators to efficiently
stream tens of millions of tiles, and can handle multiple tiles in
parallel using Python's
`multiprocessing <http://docs.python.org/library/multiprocessing.html>`_
library.

Example tasks that TileCloud makes easy include:


-  Visualize tiles stored in any TileStore with
   `OpenLayers <http://www.openlayers.org/>`_,
   `Google Maps <http://maps.google.com/>`_,
   `jQuery Geo <http://www.jquerygeo.com/>`_,
   `Leaflet <http://leaflet.cloudmade.com/>`_,
   `Polymaps <http://polymaps.org/>`_,
   `Modest Maps <http://www.modestmaps.com/>`_, and
   `OpenWebGlobe <http://www.openwebglobe.org/>`_.

-  Convert sixty million PNG tiles stored in S3 to JPEG format with
   different quality settings at different zoom levels.

-  Transform image formats and perform arbitrary image
   transformations on the fly, including PNG optimization.

-  Generate semi-transparent tiles with embedded tile coordinates
   for debugging.

-  Pack multiple tile layers into a single tile on the server.

-  Efficiently calculate bounding boxes and detect missing tiles in
   existing tile datasets.

-  Simulate fast and slow tile servers.

-  Efficiently delete millions of tiles in S3.

-  Read JSON tiles from a tarball, compress them, and upload
   them.


Getting started
===============

TileCloud depends on some Python modules. It's easiest to install them with
``pip`` in a ``virtualenv``:

::

    $ virtualenv .
    $ . bin/activate
    $ pip install -r requirements.txt

For a quick demo, run

::

    $ ./tc-viewer --root=3/4/2 'http://gsp2.apple.com/tile?api=1&style=slideshow&layers=default&lang=en_GB&z=%(z)d&x=%(x)d&y=%(y)d&v=9'

and point your browser at http://localhost:8080/. Type ``Ctrl-C``
to terminate ``tc-viewer``.

Next, download an example MBTiles file from
`MapBox <http://mapbox.com/>`_, such as
`Geography Class <http://tiles.mapbox.com/mapbox/map/geography-class>`_.
We can quickly find out more about this tile set with the
``tc-info`` command. For example, to count the number of tiles:

::

    $ ./tc-info -t count geography-class.mbtiles
    87381

To calculate the bounding pyramid:

::

    $ ./tc-info -t bounding-pyramid -r geography-class.mbtiles
    0/0/0:+1/+1
    1/0/0:+2/+2
    2/0/0:+4/+4
    3/0/0:+8/+8
    4/0/0:+16/+16
    5/0/0:+32/+32
    6/0/0:+64/+64
    7/0/0:+128/+128
    8/0/0:+256/+256

To check for missing tiles against a bounding pyramid:

::

    $ ./tc-info -b 0/0/0:8/*/* -t completion geography-class.mbtiles
    0 1/1 (100%)
    1 4/4 (100%)
    2 16/16 (100%)
    3 64/64 (100%)
    4 256/256 (100%)
    5 1024/1024 (100%)
    6 4096/4096 (100%)
    7 16384/16384 (100%)
    8 65536/65536 (100%)

This shows, for each zoom level, the number of tiles at that zoom
level, the total number of tiles expected at that zoom level for
the specified bounding pyramid (``0/0/0:8/*/*`` means all tiles
from level 0 to level 8), and a percentage completion. This can be
useful for checking that a tile set is complete.

Now, display this MBTiles tile set on top of the
`OpenStreetMap <http://www.openstreetmap.org/>`_ tiles and a debug
tile layer:

::

    $ ./tc-viewer tiles.openstreetmap_org geography-class.mbtiles tiles.debug.black

You'll need to point your browser at http://localhost:8080/ and
choose your favourite library.

``tc-info`` and ``tc-viewer`` are utility programs. Normally you
use TileCloud by writing short Python programs that connect the
TileCloud's modules to perform the action that you want.

As a first example, run the following:

::

    $ PYTHONPATH=. examples/download.py

This will download a few tiles from
`OpenStreetMap <http://www.openstreetmap.org/>`_ and save them in a
local MBTiles file called ``local.mbtiles``. Look at the source
code to ``examples/download.py`` to see how it works. If there are
problems with the download, just interrupt it with ``Ctrl-C`` and
re-run it: the program will automatically resume where it left
off.

Once you have downloaded a few tiles, you can view them directly
with ``tc-viewer``:

::

    $ ./tc-viewer --root=4/8/5 local.mbtiles tiles.debug.black

Point your browser at http://localhost:8080 as usual. The
``--root`` option to ``tc-viewer`` instructs the viewer to start at
a defined tile, rather than at 0/0/0, so you don't have to zoom in
to find the tiles that you downloaded.

Tile coordinates, tile layouts, tile grids and bounding pyramids
================================================================

TileCloud always represents tile coordinates as strings like ``z/x/y``.
TileCloud primarily works in tile coordinates, although geographic coordinates
can be used in some places.

Tile layouts convert tile coordinates to and from strings for use in paths,
URLs, keys, etc.

Tile grids are used to convert tile coordinates to and from geographic
coordinates, and to relate tiles with different z values.

Bounding pyramids represent a range of tiles in the x, y and z directions.  The
format is basically ``minz/minx/miny:maxz/maxx/maxy`` but ``maxz`` is optional
and ``maxz``, ``maxx`` and ``maxy`` can be prefixed with an ``+`` sign to
indicate that they are relative to the corresponding ``min`` value.  This is
probably best demonstrated by a few examples:

``4/10/20:15/25``
  This corresponds to a range of tiles with z=4, x=10..15 and y=20..25

``4/10/20:+5/+5``
  This is the same range (z=4, x=10..15, y=20..25) but expressed using relative
  sizes.

``4/10/20:5/15/20``
  This is the same range of tiles above, but also includes all the tiles at
  level z=5 which overlap the above range.  TileCloud uses the tile grid to
  calculate which tiles from level z=5 to include.

``4/10/20:+1/+5/+5``
  This represents the range same as the previous example using a relative
  ``maxz``.

Quick tile generation
=====================

The ``tc-copy`` command can be used to copy tiles between different
TileStores. If a TileStore has the side effect of generating tiles,
then it functions as a quick tile generation utility. First, some
quick examples.

To convert from one tile format to another, just copy from source
to destination. For example, to convert an MBTiles file in to a ZIP
file, just run:

::

    $ ./tc-copy geography-class.mbtiles geography-class.zip

You can check this worked with ``unzip``:

::

    $ unzip -t geography-class.zip

Equally, ``tc-copy`` can be used to download multiple tiles:

::

    $ ./tc-copy --bounding-pyramid 4/0/0:0/16/16 tiles.openstreetmap_org osm-up-to-z4.mbtiles

Here we downloaded zoom levels 0 to 4 of the OpenStreetMap tiles
into a local MBTiles file. The ``--bounding-pyramid`` option is
required because otherwise we would download *all* OpenStreetMap
tiles -- which might take some time (and also contravene
OpenStreetMap's tile usage policy). Note that, by default,
``tc-copy`` won't overwrite tiles if they already exist in the
destination. This means that you can interrupt the above command
and restart it, and it will resume where it was interrupted. If you
want to overwrite tiles in the destination then pass the
``--overwrite`` option to ``tc-copy``.

In the same way, ``tc-copy`` can also be used to upload tiles. For
example, to upload an MBTiles file to S3, just use:

::

    $ ./tc-copy osm-up-to-z4.mbtiles s3://bucket/prefix/%(z)d/%(x)d/%(y)d.jpg

``bucket`` is the name of your S3 bucket. You'll need to have set
the ``AWS_ACCESS_KEY_ID`` and ``AWS_SECRET_ACCESS_KEY`` environment
variables to have permission to upload to S3. The rest of the
destination (``prefix/%(z)d/%(x)d/%(y)d.jpg``) is a template
describing the layout of the tiles in S3. It's a normal Python
format string: ``%(x)d`` means substitute the tile's ``x``
coordinate as a decimal integer.

You can pass the same ``s3://`` URL to ``tc-viewer``. This allows
you to visualise your tiles stored in S3 with your favourite
mapping library. For example:

::

    $ ./tc-viewer s3://bucket/prefix/%(z)d/%(x)d/%(y)d.jpg

Here, ``tc-viewer`` is acting as a proxy, serving tiles stored in
S3 over HTTP, bypassing any caches or access controls (assuming you
have the correct credentials, of course). This allows you to
visualize the exact tiles that you've stored.

Rendering the World
===================

At `FOSS4G-NA <http://foss4g-na.org/>`_,
`MapBox <http://mapbox.com/>`_ presented an excellent strategy for
`rendering the world <http://mapbox.com/blog/rendering-the-world/>`_.
TileCloud supports the subdivision strategy. To run the demo,
execute:

::

    $ python examples/renderingtheworld.py

This will generate tiles from a WMTS tile server and save them in a
local MBTiles tiles. When the above command is complete, you can
see the bounding pyramid of the generated tiles:

::

    $ ./tc-info -t bounding-pyramid -r medford_buildings.mbtiles
    0/0/0:+1/+1
    1/0/0:+1/+1
    2/0/1:+1/+1
    3/1/2:+1/+1
    4/2/5:+1/+1
    5/5/11:+1/+1
    6/10/23:+1/+1
    7/20/47:+1/+1
    8/40/94:+2/+2
    9/80/189:+2/+1
    10/162/378:+1/+2
    11/324/757:+2/+2
    12/649/1514:+3/+3
    13/1299/3028:+4/+5
    14/2598/6057:+7/+8
    15/5196/12114:+13/+15

You can look at these tiles (which show buildings in Medford, OR)
with the command:

::

    ./tc-viewer --root=7/20/47 tiles.openstreetmap_org medford_buildings.mbtiles

A cheap-and-cheerful tile server
================================

``tc-viewer`` can be used as a lightweight tile server, which can
be useful for development, debugging and off-line demos. The
TileStores passed as arguments to ``tc-viewer`` are available at
the URL:

::

    http://localhost:8080/tiles/{index}/tiles/{z}/{x}/{y}

where ``{index}`` is the index of the TileStore on the command line
(starting from 0 for the first tile store), and ``{z}``, ``{x}``
and ``{y}`` are the components of the tile coordinate. The second
``tiles`` in the URL is present to work around assumptions made by
OpenWebGlobe. This layout is directly usable by most mapping
libraries, see the code in ``views/*.tpl`` for examples. The host
and port can be set with the ``--host`` and ``--port`` command line
options, respectively.

Note that there is no file extension. ``tc-viewer`` will
automatically set the correct content type and content encoding
headers if it can determine them, and, failing this, most browsers
will figure it out for themselves.

For convenience, ``tc-viewer`` serves everything in the ``static``
directory under the URL ``/static``. This can be used to serve your
favourite mapping library and/or application code directly for
testing purposes.

By default, ``tc-viewer`` will use
`Tornado <http://www.tornadoweb.org/>`_ as a web server, if it is
available, otherwise it will fall back to
`WSGIRef <http://docs.python.org/library/wsgiref.html>`_. Tornado
has reasonably good performance, and is adequate for local
development and off-line demos, especially when used with a MBTiles
TileStore. WSGIRef has very poor performance (it handles only one
request at a time) and as such can be used as a "slow" tile server,
ideal for debugging tile loading code or testing how your web
application performs over a slow network connection. ``tc-viewer``
is particularly slow when used to proxy tiles being served by a
remote server. You can set the server explicitly with the
``--server`` option.

``tc-viewer`` sets the ``Access-Control-Allow-Origin`` header to
``*`` for all the tiles it serves, this allows the tiles to be used
as textures for WebGL applications running on different
hosts/ports. For more information, see
`Cross-Domain Textures <https://developer.mozilla.org/en/WebGL/Cross-Domain_Textures>`_.

``tc-viewer`` is designed as a development tool, and the power that
it offers comes at the expense of fragility. It makes many
assumptions - including the benevolence of the user - that make it
entirely unsuitable as a generic tile server. It should only be
used in development or demonstration environments.

Comparing mapping libraries
===========================

``tc-viewer`` supports most popular web mapping libraries
out-of-the box. This can be very useful for quick, practical
comparisons. If your favourite mapping library is missing, please
submit an `issue <https://github.com/camptocamp/tilecloud/issues>`_,
or, even better, a
`pull request <https://github.com/camptocamp/tilecloud/pulls>`_.

Contributing
============

Please report bugs and feature requests using the
`GitHub issue tracker <https://github.com/camptocamp/tilecloud/issues>`_.

If you'd like to contribute to TileCloud, please install the development
requirements:

::

    $ pip install -r dev-requirements.txt

TileCloud comes with unit tests in the ``tilecloud/tests``
directory. You can run these with the command:

::

    $ make test

This is equivalent to:

::

    $ python setup.py nosetests

For pull requests, it is very much appreciated if your code passes
`pep8 <http://pypi.python.org/pypi/pep8>`_ and
`pyflakes <http://pypi.python.org/pypi/pyflakes>`_ without
warnings, with the exception of pep8 warning "E501 line too long",
which is allowed. You can run pep8 and pyflakes on the codebase
with the command:

::

    $ make pep8 pyflakes

License
=======

Copyright (c) 2012, Tom Payne twpayne@gmail.com All rights
reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions
are met:


-  Redistributions of source code must retain the above copyright
   notice, this list of conditions and the following disclaimer.

-  Redistributions in binary form must reproduce the above
   copyright notice, this list of conditions and the following
   disclaimer in the documentation and/or other materials provided
   with the distribution.


THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,
INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED
OF THE POSSIBILITY OF SUCH DAMAGE.

vim: set filetype=rst spell spelllang=en textwidth=0:
