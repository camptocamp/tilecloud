from tilecloud.layout.osm import OSMTileLayout
from tilecloud.layout.wrapped import WrappedTileLayout
from tilecloud.store.log import LogTileStore


tile_store = LogTileStore(WrappedTileLayout(OSMTileLayout(), 'data/image/ch.swisstopo.swissimage-20111129/tiles/', '.jpg'), open('lancer-16.log'))
