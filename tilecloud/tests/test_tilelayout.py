import unittest
from urlparse import urlparse
from cgi import parse_qs

from tilecloud import TileCoord, TileLayout
from tilecloud.layout.osm import OSMTileLayout
from tilecloud.layout.template import TemplateTileLayout
from tilecloud.layout.tilecache import TileCacheDiskLayout
from tilecloud.layout.wms import WMSTileLayout
from tilecloud.layout.wmts import WMTSTileLayout
from tilecloud.layout.wrapped import WrappedTileLayout
from tilecloud.grid.free import FreeTileGrid


class TestTileLayout(unittest.TestCase):

    def test_filename(self):
        self.assertRaises(NotImplementedError, TileLayout().filename, None)

    def test_tilecoord(self):
        self.assertRaises(NotImplementedError, TileLayout().tilecoord, None)


class TestOSMTileLayout(unittest.TestCase):

    def setUp(self):
        self.tilelayout = OSMTileLayout()

    def test_filename(self):
        self.assertEqual(self.tilelayout.filename(TileCoord(1, 2, 3)), '1/2/3')

    def test_tilecoord(self):
        self.assertEqual(self.tilelayout.tilecoord('1/2/3'), TileCoord(1, 2, 3))
        self.assertRaises(ValueError, self.tilelayout.tilecoord, '1/2/')


class TestWMTSTileLayout(unittest.TestCase):

    def setUp(self):
        self.rest = WMTSTileLayout(
            url='test',
            layer='layer',
            style='default',
            format='.png',
            dimensions=(('DATE', '2011'),),
            tile_matrix_set='swissgrid',
            request_encoding='REST')
        self.kvp = WMTSTileLayout(
            url='test',
            layer='layer',
            style='default',
            format='.png',
            dimensions=(('DATE', '2011'),),
            tile_matrix_set='swissgrid',
            request_encoding='KVP')

    def test_filename(self):
        self.assertEqual(self.rest.filename(TileCoord(1, 2, 3)), 'test/1.0.0/layer/default/2011/swissgrid/1/3/2.png')
        self.assertEqual(self.kvp.filename(TileCoord(1, 2, 3)), 'test?Service=WMTS&Request=GetTile&Format=.png&Version=1.0.0&Layer=layer&Style=default&DATE=2011&TileMatrixSet=swissgrid&TileMatrix=1&TileRow=3&TileCol=2')


class TestWMSTileLayout(unittest.TestCase):

    def setUp(self):
        self.tilegrid = FreeTileGrid(
            resolutions=(1000000, 500000, 1),
            max_extent=(420000, 30000, 900000, 350000),
            tile_size=100, scale=10000)

    def test_png(self):
        layout = WMSTileLayout(
            url='http://example.com/folder',
            layers='l1,l2',
            srs='EPSG:1000',
            format='image/png',
            tilegrid=self.tilegrid)
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
        layout = WMSTileLayout(
            url='http://example.com/folder',
            layers='l1,l2',
            srs='EPSG:1000',
            format='image/jpeg',
            tilegrid=self.tilegrid)
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

    def test_border(self):
        layout = WMSTileLayout(
            url='http://example.com/folder',
            layers='l1,l2',
            srs='EPSG:1000',
            format='image/png',
            tilegrid=self.tilegrid,
            border=10)
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
        layout = WMSTileLayout(
            url='http://example.com/folder',
            layers='l1,l2',
            srs='EPSG:1000',
            format='image/png',
            tilegrid=self.tilegrid)
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

    def test_metatile(self):
        layout = WMSTileLayout(
            url='http://example.com/folder',
            layers='l1,l2',
            srs='EPSG:1000',
            format='image/png',
            tilegrid=self.tilegrid)
        result = urlparse(layout.filename(TileCoord(1, 0, 0, 2)))
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
        self.assertEqual(query['WIDTH'], ['200'])
        self.assertEqual(query['HEIGHT'], ['200'])
        bbox = [float(i) for i in query['BBOX'][0].split(',')]
        self.assertEqual(len(bbox), 4)
        self.assertEqual(bbox[0], 420000.0)
        self.assertEqual(bbox[1], 340000.0)
        self.assertEqual(bbox[2], 430000.0)
        self.assertEqual(bbox[3], 350000.0)

    def test_metatile_border(self):
        layout = WMSTileLayout(
            url='http://example.com/folder',
            layers='l1,l2',
            srs='EPSG:1000',
            format='image/png',
            tilegrid=self.tilegrid,
            border=5)
        result = urlparse(layout.filename(TileCoord(1, 0, 0, 2)))
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
        self.assertEqual(query['WIDTH'], ['210'])
        self.assertEqual(query['HEIGHT'], ['210'])
        bbox = [float(i) for i in query['BBOX'][0].split(',')]
        self.assertEqual(len(bbox), 4)
        self.assertEqual(bbox[0], 419750.0)
        self.assertEqual(bbox[1], 339750.0)
        self.assertEqual(bbox[2], 430250.0)
        self.assertEqual(bbox[3], 350250.0)


class TestTemplateTileLayout(unittest.TestCase):

    def setUp(self):
        self.tilelayout = TemplateTileLayout('%(z)d/%(x)d/%(y)d')

    def test_filename(self):
        self.assertEqual(self.tilelayout.filename(TileCoord(1, 2, 3)), '1/2/3')

    def test_tilecoord(self):
        self.assertEqual(self.tilelayout.tilecoord('1/2/3'), TileCoord(1, 2, 3))


class TestWrappedTileLayout(unittest.TestCase):

    def setUp(self):
        self.tilelayout = WrappedTileLayout(OSMTileLayout(), 'prefix/', '.suffix')

    def test_filename(self):
        self.assertEqual(self.tilelayout.filename(TileCoord(1, 2, 3)), 'prefix/1/2/3.suffix')

    def test_tilecoord(self):
        self.assertEqual(self.tilelayout.tilecoord('prefix/1/2/3.suffix'), TileCoord(1, 2, 3))
        self.assertRaises(ValueError, self.tilelayout.tilecoord, 'prefix//1/2/3.suffix')


class TestTileCacheDiskLayout(unittest.TestCase):

    def setUp(self):
        self.tilelayout = TileCacheDiskLayout()

    def test_filename(self):
        self.assertEqual('01/123/456/789/987/654/321', self.tilelayout.filename(TileCoord(1, 123456789, 987654321)))

    def test_tilecoord(self):
        self.assertEqual(TileCoord(1, 123456789, 987654321), self.tilelayout.tilecoord('01/123/456/789/987/654/321'))
