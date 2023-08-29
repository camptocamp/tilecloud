import unittest
from urllib.parse import parse_qs, urlparse

from tilecloud import TileCoord, TileLayout
from tilecloud.grid.free import FreeTileGrid
from tilecloud.layout.osm import OSMTileLayout
from tilecloud.layout.template import TemplateTileLayout
from tilecloud.layout.tilecache import TileCacheDiskLayout
from tilecloud.layout.wms import WMSTileLayout
from tilecloud.layout.wmts import WMTSTileLayout
from tilecloud.layout.wrapped import WrappedTileLayout


class TestTileLayout(unittest.TestCase):
    def test_filename(self) -> None:
        self.assertRaises(NotImplementedError, TileLayout().filename, None)

    def test_tilecoord(self) -> None:
        self.assertRaises(NotImplementedError, TileLayout().tilecoord, None)


class TestOSMTileLayout(unittest.TestCase):
    def setUp(self) -> None:
        self.tilelayout = OSMTileLayout()

    def test_filename(self) -> None:
        assert self.tilelayout.filename(TileCoord(1, 2, 3)) == "1/2/3"

    def test_tilecoord(self) -> None:
        assert self.tilelayout.tilecoord("1/2/3") == TileCoord(1, 2, 3)
        self.assertRaises(ValueError, self.tilelayout.tilecoord, "1/2/")


class TestWMTSTileLayout(unittest.TestCase):
    def setUp(self) -> None:
        self.rest = WMTSTileLayout(
            url="test",
            layer="layer",
            style="default",
            format_pattern=".png",
            dimensions_name=("DATE",),
            tile_matrix_set="swissgrid",
            request_encoding="REST",
        )
        self.kvp = WMTSTileLayout(
            url="test",
            layer="layer",
            style="default",
            format_pattern=".png",
            dimensions_name=("DATE",),
            tile_matrix_set="swissgrid",
            request_encoding="KVP",
        )
        self.rest_nourl = WMTSTileLayout(
            layer="layer",
            style="default",
            format_pattern=".png",
            dimensions_name=("DATE",),
            tile_matrix_set="swissgrid",
            request_encoding="REST",
        )
        self.kvp_nourl = WMTSTileLayout(
            layer="layer",
            style="default",
            format_pattern=".png",
            dimensions_name=("DATE",),
            tile_matrix_set="swissgrid",
            request_encoding="KVP",
        )

    def test_filename(self) -> None:
        assert (
            self.rest.filename(TileCoord(1, 2, 3), {"dimension_DATE": "2011"})
            == "test/1.0.0/layer/default/2011/swissgrid/1/3/2.png"
        )
        assert (
            self.kvp.filename(TileCoord(1, 2, 3), {"dimension_DATE": "2011"})
            == "test?Service=WMTS&Request=GetTile&Format=.png&Version=1.0.0&Layer=layer&Style=default&DATE=2011&TileMatrixSet=swissgrid&TileMatrix=1&TileRow=3&TileCol=2"
        )

    def test_filename_without_url(self) -> None:
        # s3 url it shouldn't starts with a /
        assert (
            self.rest_nourl.filename(TileCoord(1, 2, 3), {"dimension_DATE": "2011"})
            == "1.0.0/layer/default/2011/swissgrid/1/3/2.png"
        )
        assert (
            self.kvp_nourl.filename(TileCoord(1, 2, 3), {"dimension_DATE": "2011"})
            == "?Service=WMTS&Request=GetTile&Format=.png&Version=1.0.0&Layer=layer&Style=default&DATE=2011&TileMatrixSet=swissgrid&TileMatrix=1&TileRow=3&TileCol=2"
        )


class TestWMSTileLayout(unittest.TestCase):
    def setUp(self) -> None:
        self.tilegrid = FreeTileGrid(
            resolutions=(1000000, 500000, 1),
            max_extent=(420000, 30000, 900000, 350000),
            tile_size=100,
            scale=10000,
        )

    def test_png(self) -> None:
        layout = WMSTileLayout(
            url="http://example.com/folder",
            layers="l1,l2",
            srs="EPSG:1000",
            format_pattern="image/png",
            tilegrid=self.tilegrid,
        )
        result = urlparse(layout.filename(TileCoord(0, 0, 0)))
        assert result.netloc == "example.com"
        assert result.path == "/folder"
        query = parse_qs(result.query)
        assert query["LAYERS"] == ["l1,l2"]
        assert query["FORMAT"] == ["image/png"]
        assert query["TRANSPARENT"] == ["TRUE"]
        assert query["SERVICE"] == ["WMS"]
        assert query["VERSION"] == ["1.1.1"]
        assert query["REQUEST"] == ["GetMap"]
        assert query["SRS"] == ["EPSG:1000"]
        assert query["WIDTH"] == ["100"]
        assert query["HEIGHT"] == ["100"]
        bbox = [float(i) for i in query["BBOX"][0].split(",")]
        assert bbox == [420000.0, 340000.0, 430000.0, 350000.0]

    def test_jpeg(self) -> None:
        layout = WMSTileLayout(
            url="http://example.com/folder",
            layers="l1,l2",
            srs="EPSG:1000",
            format_pattern="image/jpeg",
            tilegrid=self.tilegrid,
        )
        result = urlparse(layout.filename(TileCoord(0, 0, 0)))
        assert result.netloc == "example.com"
        assert result.path == "/folder"
        query = parse_qs(result.query)
        assert query["LAYERS"] == ["l1,l2"]
        assert query["FORMAT"] == ["image/jpeg"]
        assert query["TRANSPARENT"] == ["FALSE"]
        assert query["SERVICE"] == ["WMS"]
        assert query["VERSION"] == ["1.1.1"]
        assert query["REQUEST"] == ["GetMap"]
        assert query["SRS"] == ["EPSG:1000"]
        assert query["WIDTH"] == ["100"]
        assert query["HEIGHT"] == ["100"]
        bbox = [float(i) for i in query["BBOX"][0].split(",")]
        assert bbox == [420000.0, 340000.0, 430000.0, 350000.0]

    def test_border(self) -> None:
        layout = WMSTileLayout(
            url="http://example.com/folder",
            layers="l1,l2",
            srs="EPSG:1000",
            format_pattern="image/png",
            tilegrid=self.tilegrid,
            border=10,
        )
        result = urlparse(layout.filename(TileCoord(0, 0, 0)))
        assert result.netloc == "example.com"
        assert result.path == "/folder"
        query = parse_qs(result.query)
        assert query["LAYERS"] == ["l1,l2"]
        assert query["FORMAT"] == ["image/png"]
        assert query["TRANSPARENT"] == ["TRUE"]
        assert query["SERVICE"] == ["WMS"]
        assert query["VERSION"] == ["1.1.1"]
        assert query["REQUEST"] == ["GetMap"]
        assert query["SRS"] == ["EPSG:1000"]
        assert query["WIDTH"] == ["120"]
        assert query["HEIGHT"] == ["120"]
        bbox = [float(i) for i in query["BBOX"][0].split(",")]
        assert len(bbox) == 4
        assert bbox == [419000.0, 339000.0, 431000.0, 351000.0]

    def test_subx_metric(self) -> None:
        layout = WMSTileLayout(
            url="http://example.com/folder",
            layers="l1,l2",
            srs="EPSG:1000",
            format_pattern="image/png",
            tilegrid=self.tilegrid,
        )
        result = urlparse(layout.filename(TileCoord(2, 0, 0)))
        assert result.netloc == "example.com"
        assert result.path == "/folder"
        query = parse_qs(result.query)
        assert query["LAYERS"] == ["l1,l2"]
        assert query["FORMAT"] == ["image/png"]
        assert query["TRANSPARENT"] == ["TRUE"]
        assert query["SERVICE"] == ["WMS"]
        assert query["VERSION"] == ["1.1.1"]
        assert query["REQUEST"] == ["GetMap"]
        assert query["SRS"] == ["EPSG:1000"]
        assert query["WIDTH"] == ["100"]
        assert query["HEIGHT"] == ["100"]
        bbox = [float(i) for i in query["BBOX"][0].split(",")]
        assert bbox == [420000.0, 349999.99, 420000.01, 350000.0]

    def test_metatile(self) -> None:
        layout = WMSTileLayout(
            url="http://example.com/folder",
            layers="l1,l2",
            srs="EPSG:1000",
            format_pattern="image/png",
            tilegrid=self.tilegrid,
        )
        result = urlparse(layout.filename(TileCoord(1, 0, 0, 2)))
        assert result.netloc == "example.com"
        assert result.path == "/folder"
        query = parse_qs(result.query)
        assert query["LAYERS"] == ["l1,l2"]
        assert query["FORMAT"] == ["image/png"]
        assert query["TRANSPARENT"] == ["TRUE"]
        assert query["SERVICE"] == ["WMS"]
        assert query["VERSION"] == ["1.1.1"]
        assert query["REQUEST"] == ["GetMap"]
        assert query["SRS"] == ["EPSG:1000"]
        assert query["WIDTH"] == ["200"]
        assert query["HEIGHT"] == ["200"]
        bbox = [float(i) for i in query["BBOX"][0].split(",")]
        assert bbox == [420000.0, 340000.0, 430000.0, 350000.0]

    def test_metatile_border(self) -> None:
        layout = WMSTileLayout(
            url="http://example.com/folder",
            layers="l1,l2",
            srs="EPSG:1000",
            format_pattern="image/png",
            tilegrid=self.tilegrid,
            border=5,
        )
        result = urlparse(layout.filename(TileCoord(1, 0, 0, 2)))
        assert result.netloc == "example.com"
        assert result.path == "/folder"
        query = parse_qs(result.query)
        assert query["LAYERS"] == ["l1,l2"]
        assert query["FORMAT"] == ["image/png"]
        assert query["TRANSPARENT"] == ["TRUE"]
        assert query["SERVICE"] == ["WMS"]
        assert query["VERSION"] == ["1.1.1"]
        assert query["REQUEST"] == ["GetMap"]
        assert query["SRS"] == ["EPSG:1000"]
        assert query["WIDTH"] == ["210"]
        assert query["HEIGHT"] == ["210"]
        bbox = [float(i) for i in query["BBOX"][0].split(",")]
        assert bbox == [419750.0, 339750.0, 430250.0, 350250.0]

    def test_params(self) -> None:
        layout = WMSTileLayout(
            url="http://example.com/folder",
            layers="l1,l2",
            srs="EPSG:1000",
            format_pattern="image/png",
            tilegrid=self.tilegrid,
            params={"TRANSPARENT": "FALSE", "PARAM": "Value", "FILTER": 'l1:"field" = ' "{PARAM}" ""},
        )
        result = urlparse(layout.filename(TileCoord(0, 0, 0)))
        assert result.netloc == "example.com"
        assert result.path == "/folder"
        query = parse_qs(result.query)
        assert query["PARAM"] == ["Value"]
        assert query["FILTER"] == ['l1:"field" = ' "Value" ""]
        assert query["LAYERS"] == ["l1,l2"]
        assert query["FORMAT"] == ["image/png"]
        assert query["TRANSPARENT"] == ["FALSE"]
        assert query["SERVICE"] == ["WMS"]
        assert query["VERSION"] == ["1.1.1"]
        assert query["REQUEST"] == ["GetMap"]
        assert query["SRS"] == ["EPSG:1000"]
        assert query["WIDTH"] == ["100"]
        assert query["HEIGHT"] == ["100"]
        bbox = [float(i) for i in query["BBOX"][0].split(",")]
        assert bbox == [420000.0, 340000.0, 430000.0, 350000.0]


class TestTemplateTileLayout(unittest.TestCase):
    def setUp(self) -> None:
        self.tilelayout = TemplateTileLayout("%(z)d/%(x)d/%(y)d")

    def test_filename(self) -> None:
        assert self.tilelayout.filename(TileCoord(1, 2, 3)) == "1/2/3"

    def test_tilecoord(self) -> None:
        assert self.tilelayout.tilecoord("1/2/3") == TileCoord(1, 2, 3)


class TestWrappedTileLayout(unittest.TestCase):
    def setUp(self) -> None:
        self.tilelayout = WrappedTileLayout(OSMTileLayout(), "prefix/", ".suffix")

    def test_filename(self) -> None:
        assert self.tilelayout.filename(TileCoord(1, 2, 3)) == "prefix/1/2/3.suffix"

    def test_tilecoord(self) -> None:
        assert self.tilelayout.tilecoord("prefix/1/2/3.suffix") == TileCoord(1, 2, 3)
        self.assertRaises(ValueError, self.tilelayout.tilecoord, "prefix//1/2/3.suffix")


class TestTileCacheDiskLayout(unittest.TestCase):
    def setUp(self) -> None:
        self.tilelayout = TileCacheDiskLayout()

    def test_filename(self) -> None:
        assert "01/123/456/789/987/654/321" == self.tilelayout.filename(TileCoord(1, 123456789, 987654321))

    def test_tilecoord(self) -> None:
        assert TileCoord(1, 123456789, 987654321) == self.tilelayout.tilecoord("01/123/456/789/987/654/321")
