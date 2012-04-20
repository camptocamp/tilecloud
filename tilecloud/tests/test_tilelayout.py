import unittest
from urlparse import urlparse
from cgi import parse_qs

from tilecloud import TileCoord, TileLayout, Grid
from tilecloud.layout.osm import OSMTileLayout
from tilecloud.layout.wmts import WMTSTileLayout
from tilecloud.layout.wms import WMSTileLayout
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


class TestWMTSTileLayout(unittest.TestCase):

    def setUp(self):
        self.rest = WMTSTileLayout(
                url='test',
                layer='layer',
                style='default',
                format='.png',
                dimensions=(('DATE', '2011'),),
                tile_matrix_set='swissgrid',
                request_encoding='REST',
        )
        self.kvp = WMTSTileLayout(
                url='test',
                layer='layer',
                style='default',
                format='.png',
                dimensions=(('DATE', '2011'),),
                tile_matrix_set='swissgrid',
                request_encoding='KVP',
        )

    def test_filename(self):
        self.assertEqual(self.rest.filename(TileCoord(1, 2, 3)), 'test/1.0.0/layer/default/2011/swissgrid/1/3/2.png')
        self.assertEqual(self.kvp.filename(TileCoord(1, 2, 3)), 'test?Service=WMTS&Request=GetTile&Format=.png&Version=1.0.0&Layer=layer&Style=default&DATE=2011&TileMatrixSet=swissgrid&TileMatrix=1&TileRow=3&TileCol=2')


class TestWMSTileLayout(unittest.TestCase):
    def setUp(self):
        self.grid = Grid(
            resolutions=(100, 50, 0.0001),
            max_extent=(420000, 30000, 900000, 350000),
            tile_size=100,
            top=1)

    def test_png(self):
        layout = WMSTileLayout(url='http://example.com/folder',
             layers='l1,l2', srid=1000, image_format='png', grid=self.grid)
        result = urlparse(layout.filename(TileCoord(0, 0, 0)))
        self.assertEqual(result.netloc, 'example.com')
        self.assertEqual(result.path, '/folder')
        query = parse_qs(result.query)
        self.assertEqual(query['LAYERS'], ['l1,l2'])
        self.assertEqual(query['FORMAT'], ['image/png'])
        self.assertEqual(query['TRANSPARENT'], ['TRUE'])
        self.assertEqual(query['SERVICE'], ['WMS'])
        self.assertEqual(query['VERSION'], ['1.1.1'])
        self.assertEqual(query['REQUEST'], ['GetMap'])
        self.assertEqual(query['SRS'], ['EPSG:1000'])
        self.assertEqual(query['WIDTH'], ['100'])
        self.assertEqual(query['HEIGHT'], ['100'])
        bbox = [float(i) for i in query['BBOX'][0].split(',')]
        self.assertEqual(len(bbox), 4)
        self.assertEqual(bbox[0], 420000.0)
        self.assertEqual(bbox[1], 340000.0)
        self.assertEqual(bbox[2], 430000.0)
        self.assertEqual(bbox[3], 350000.0)

    def test_jpeg(self):
        layout = WMSTileLayout(url='http://example.com/folder',
                layers='l1,l2', srid=1000, image_format='jpeg', grid=self.grid)
        result = urlparse(layout.filename(TileCoord(0, 0, 0)))
        self.assertEqual(result.netloc, 'example.com')
        self.assertEqual(result.path, '/folder')
        query = parse_qs(result.query)
        self.assertEqual(query['LAYERS'], ['l1,l2'])
        self.assertEqual(query['FORMAT'], ['image/jpeg'])
        self.assertEqual(query['TRANSPARENT'], ['FALSE'])
        self.assertEqual(query['SERVICE'], ['WMS'])
        self.assertEqual(query['VERSION'], ['1.1.1'])
        self.assertEqual(query['REQUEST'], ['GetMap'])
        self.assertEqual(query['SRS'], ['EPSG:1000'])
        self.assertEqual(query['WIDTH'], ['100'])
        self.assertEqual(query['HEIGHT'], ['100'])
        bbox = [float(i) for i in query['BBOX'][0].split(',')]
        self.assertEqual(len(bbox), 4)
        self.assertEqual(bbox[0], 420000.0)
        self.assertEqual(bbox[1], 340000.0)
        self.assertEqual(bbox[2], 430000.0)
        self.assertEqual(bbox[3], 350000.0)

    def test_buffer(self):
        layout = WMSTileLayout(url='http://example.com/folder',
                layers='l1,l2', srid=1000, image_format='png',
                grid=self.grid, buffer=10)
        result = urlparse(layout.filename(TileCoord(0, 0, 0)))
        self.assertEqual(result.netloc, 'example.com')
        self.assertEqual(result.path, '/folder')
        query = parse_qs(result.query)
        self.assertEqual(query['LAYERS'], ['l1,l2'])
        self.assertEqual(query['FORMAT'], ['image/png'])
        self.assertEqual(query['TRANSPARENT'], ['TRUE'])
        self.assertEqual(query['SERVICE'], ['WMS'])
        self.assertEqual(query['VERSION'], ['1.1.1'])
        self.assertEqual(query['REQUEST'], ['GetMap'])
        self.assertEqual(query['SRS'], ['EPSG:1000'])
        self.assertEqual(query['WIDTH'], ['120'])
        self.assertEqual(query['HEIGHT'], ['120'])
        bbox = [float(i) for i in query['BBOX'][0].split(',')]
        self.assertEqual(len(bbox), 4)
        self.assertEqual(bbox[0], 419000.0)
        self.assertEqual(bbox[1], 339000.0)
        self.assertEqual(bbox[2], 431000.0)
        self.assertEqual(bbox[3], 351000.0)

    def test_subx_metric(self):
        layout = WMSTileLayout(url='http://example.com/folder',
                layers='l1,l2', srid=1000, image_format='png',
                grid=self.grid)
        result = urlparse(layout.filename(TileCoord(2, 0, 0)))
        self.assertEqual(result.netloc, 'example.com')
        self.assertEqual(result.path, '/folder')
        query = parse_qs(result.query)
        self.assertEqual(query['LAYERS'], ['l1,l2'])
        self.assertEqual(query['FORMAT'], ['image/png'])
        self.assertEqual(query['TRANSPARENT'], ['TRUE'])
        self.assertEqual(query['SERVICE'], ['WMS'])
        self.assertEqual(query['VERSION'], ['1.1.1'])
        self.assertEqual(query['REQUEST'], ['GetMap'])
        self.assertEqual(query['SRS'], ['EPSG:1000'])
        self.assertEqual(query['WIDTH'], ['100'])
        self.assertEqual(query['HEIGHT'], ['100'])
        bbox = [float(i) for i in query['BBOX'][0].split(',')]
        self.assertEqual(len(bbox), 4)
        self.assertEqual(bbox[0], 420000.0)
        self.assertEqual(bbox[1], 349999.99)
        self.assertEqual(bbox[2], 420000.01)
        self.assertEqual(bbox[3], 350000.0)


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
