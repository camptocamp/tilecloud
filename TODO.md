Core
----

* Add TileStore.content_type
* Generate BoundingPyramid from coordinates (pyproj)

Viewer
------

* Generate semi-transparent TileCoord tiles
* Generate KML layer
* Add OpenWebGlobe elevation layers

TileStores
----------

* ThumbnailTileStore
* WMSTileStore
* TileJSONTileStore (https://github.com/mapbox/TileJSON)
* Add WorldWindTileStore (http://worldwindcentral.com/wiki/TileService)
* Add TMSTileStore (http://wiki.osgeo.org/wiki/Tile_Map_Service_Specification)
* Extend MaskTileStore to support BoundingPyramids
* Add periodic commit to MBTilesStileStore
* Add periodic save to MaskTileStore

Filters
-------

* Add PNG optimizer
* Add reprojector
