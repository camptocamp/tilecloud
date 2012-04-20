import unittest

from os.path import dirname
from hashlib import md5

from tilecloud import Grid, Tile, TileCoord, MetaTileCoord
from tilecloud.store.metatile import MetaTileStore, MetaTileToTileStore


class TestMetaTile(unittest.TestCase):

    def setUp(self):
        self.grid = Grid(
            resolutions=(1000, 500, 200, 100),
            max_extent=(420000, 30000, 900000, 350000),
            tile_size=256,
            top=1)

    def test_tilestore(self):
        metatile_store = MetaTileStore(grid=self.grid, meta_size=2)
        metatiles = [t for t in metatile_store.list()]
        self.assertEqual(len(metatiles), 95)
        self.assertEqual(metatiles[0].tilecoord, MetaTileCoord(2, 0, 0, 0))
        self.assertEqual(metatiles[1].tilecoord, MetaTileCoord(2, 1, 0, 0))
        self.assertEqual(metatiles[2].tilecoord, MetaTileCoord(2, 1, 0, 2))
        self.assertEqual(metatiles[3].tilecoord, MetaTileCoord(2, 1, 2, 0))
        self.assertEqual(metatiles[4].tilecoord, MetaTileCoord(2, 1, 2, 2))
        self.assertEqual(metatiles[5].tilecoord, MetaTileCoord(2, 2, 0, 0))

    def test_extent_tilestore(self):
        metatile_store = MetaTileStore(grid=self.grid, meta_size=2,
                extent=(600000, 200000, 600001, 200001))
        metatiles = [t for t in metatile_store.list()]
        self.assertEqual(len(metatiles), 4)
        self.assertEqual(metatiles[0].tilecoord, MetaTileCoord(2, 0, 0, 0))
        self.assertEqual(metatiles[1].tilecoord, MetaTileCoord(2, 1, 0, 0))
        self.assertEqual(metatiles[2].tilecoord, MetaTileCoord(2, 2, 2, 2))
        self.assertEqual(metatiles[3].tilecoord, MetaTileCoord(2, 3, 6, 6))

    def test_children(self):
        metatile = MetaTileCoord(2, 17, 4, 2)
        tiles = [t for t in metatile]
        self.assertEqual(len(tiles), 4)
        self.assertEqual(tiles[0], TileCoord(17, 4, 2))
        self.assertEqual(tiles[1], TileCoord(17, 4, 3))
        self.assertEqual(tiles[2], TileCoord(17, 5, 2))
        self.assertEqual(tiles[3], TileCoord(17, 5, 3))

    def test_crop(self):
        cropper = MetaTileToTileStore(tile_size=256, buffer=32, image_format='png')
        tiles = [t for t in cropper.get([Tile(MetaTileCoord(2, 0, 0, 0),
                data=open(dirname(__file__) + '/crop.png', 'rb').read())])]

        self.assertEqual(len(tiles), 4)
        self.assertEqual(md5(tiles[0].data).hexdigest(), 'aafb6624f12302acea3b7ab650daa4fa')
        self.assertEqual(md5(tiles[1].data).hexdigest(), '993fccad544bb06ac419ff27fc0f5f3b')
        self.assertEqual(md5(tiles[2].data).hexdigest(), '466aa73bb2c32f65c6f887cb285b3ada')
        self.assertEqual(md5(tiles[3].data).hexdigest(), 'ce61e93104ae85fb0fef0337937ccb2c')
