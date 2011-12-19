from tilecloud import BoundingPyramid
from tilecloud.layout.osm import OSMTileLayout
from tilecloud.layout.wrapped import WrappedTileLayout
from tilecloud.store.s3 import S3TileStore


tile_store = S3TileStore('map3d', WrappedTileLayout(OSMTileLayout(), 'data/elevation/DHM25-20111026/tiles/', '.json'), content_type='application/json', bounding_pyramid=BoundingPyramid.from_string('19/270688/182540:278048/186934'))
