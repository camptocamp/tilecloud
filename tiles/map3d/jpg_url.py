from tilecloud.layout.osm import OSMTileLayout
from tilecloud.layout.wrapped import WrappedTileLayout
from tilecloud.store.url import URLTileStore


tile_store = URLTileStore((WrappedTileLayout(OSMTileLayout(), 'http://mf-map3d0i.bgdi.admin.ch/data/image/ch.swisstopo.swissimage-20111129/tiles/', '.jpg'),), headers={'Referer': 'http://mf-map3d0i.bgdi.admin.ch/'})
