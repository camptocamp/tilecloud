from tilecloud.layout.i3d import I3DTileLayout
from tilecloud.layout.wrapped import WrappedTileLayout
from tilecloud.store.s3 import S3TileStore


tile_store = S3TileStore('map3d', WrappedTileLayout(I3DTileLayout(), 'data/image/ch.swisstopo.swissimage/', '.png'))
