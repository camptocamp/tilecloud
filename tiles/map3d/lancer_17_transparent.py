from tilecloud.layout.i3d import I3DTileLayout
from tilecloud.layout.wrapped import WrappedTileLayout
from tilecloud.store.log import LogTileStore


tile_store = LogTileStore(WrappedTileLayout(I3DTileLayout(), 'data/image/ch.swisstopo.swissimage/', '.png'), open('lancer-17.log'))
