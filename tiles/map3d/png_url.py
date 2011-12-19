from tilecloud.layout.i3d import I3DTileLayout
from tilecloud.layout.wrapped import WrappedTileLayout
from tilecloud.store.url import URLTileStore


tile_store = URLTileStore((WrappedTileLayout(I3DTileLayout(), 'http://mf-map3d0i.bgdi.admin.ch/data/image/ch.swisstopo.swissimage-20111025/', '.png'),), headers={'Referer': 'http://mf-map3d0i.bgdi.admin.ch/'})
