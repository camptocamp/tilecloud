import unittest

from tilecloud import TileCoord, TileLayout
from tilecloud.layout.osm import OSMTileLayout
from tilecloud.layout.template import TemplateTileLayout
from tilecloud.layout.wrapped import WrappedTileLayout


class TestTileLayout(unittest.TestCase):

    def test_filename(self):
        self.assertRaises(NotImplementedError, TileLayout().filename, None)

    def test_tilecoord(self):
        self.assertRaises(NotImplementedError, TileLayout().tilecoord, None)


class TestOSMTileLayout(unittest.TestCase):

    def setUp(self):
        self.tile_layout = OSMTileLayout()

    def test_filename(self):
        self.assertEqual(self.tile_layout.filename(TileCoord(1, 2, 3)), '1/2/3')

    def test_tilecoord(self):
        self.assertEqual(self.tile_layout.tilecoord('1/2/3'), TileCoord(1, 2, 3))
        self.assertRaises(ValueError, self.tile_layout.tilecoord, '1/2/')


class TestTemplateTileLayout(unittest.TestCase):

    def setUp(self):
        self.tile_layout = TemplateTileLayout('%(z)d/%(x)d/%(y)d')

    def test_filename(self):
        self.assertEqual(self.tile_layout.filename(TileCoord(1, 2, 3)), '1/2/3')

    def test_tilecoord(self):
        self.assertEqual(self.tile_layout.tilecoord('1/2/3'), TileCoord(1, 2, 3))


class TestWrappedTileLayout(unittest.TestCase):

    def setUp(self):
        self.tile_layout = WrappedTileLayout(OSMTileLayout(), 'prefix/', '.suffix')

    def test_filename(self):
        self.assertEqual(self.tile_layout.filename(TileCoord(1, 2, 3)), 'prefix/1/2/3.suffix')

    def test_tilecoord(self):
        self.assertEqual(self.tile_layout.tilecoord('prefix/1/2/3.suffix'), TileCoord(1, 2, 3))
        self.assertRaises(ValueError, self.tile_layout.tilecoord, 'prefix//1/2/3.suffix')
