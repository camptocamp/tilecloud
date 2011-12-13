Core
----

* Add Makefile
* Add TileStore.content_type
* Generate BoundingPyramid from coordinates (pyproj)

Viewer
------

* Generate semi-transparent TileCoord tiles
* Use single tile for 404
* Generate KML layer

TileStores
----------

* ThumbnailTileStore
* WMSTileStore
* HTTPTileStore
* TileJSONTileStore (https://github.com/mapbox/TileJSON)
* Debug tilestore generating images with tile coordinates
* Extend MaskTileStore to support BoundingPyramids
* Check y-order in MBTilesStileStore
* Add periodic commit to MBTilesStileStore
* Add periodic save to MaskTileStore

Filters
-------

* Add PNG optimizer

