import unittest
from io import BytesIO

from PIL import Image

from tilecloud import Tile, TileCoord
from tilecloud.store.metatile import MetaTileSplitterTileStore


class TestMetaTileSplitterTileStore(unittest.TestCase):
    def setUp(self) -> None:
        self.mtsts = MetaTileSplitterTileStore("image/png", tile_size=2)

    def test_get(self) -> None:
        image = Image.new("RGBA", (4, 4))
        image.paste((255, 0, 0, 0), (0, 0, 2, 2))
        image.paste((0, 255, 0, 0), (0, 2, 2, 4))
        image.paste((0, 0, 255, 0), (2, 0, 4, 2))
        image.paste((0, 0, 0, 255), (2, 2, 4, 4))
        string_io = BytesIO()
        image.save(string_io, "PNG")
        tile = Tile(TileCoord(1, 0, 0, 2), data=string_io.getvalue())
        tiles = list(self.mtsts.get([tile]))
        self.assertEqual(len(tiles), 4)
        self.assertEqual(tiles[0].tilecoord, TileCoord(1, 0, 0))
        image = Image.open(BytesIO(tiles[0].data))
        self.assertEqual(image.size, (2, 2))
        self.assertEqual(image.getcolors(), [(4, (255, 0, 0, 0))])
        self.assertEqual(tiles[1].tilecoord, TileCoord(1, 0, 1))
        image = Image.open(BytesIO(tiles[1].data))
        self.assertEqual(image.size, (2, 2))
        self.assertEqual(image.getcolors(), [(4, (0, 255, 0, 0))])
        self.assertEqual(tiles[2].tilecoord, TileCoord(1, 1, 0))
        image = Image.open(BytesIO(tiles[2].data))
        self.assertEqual(image.size, (2, 2))
        self.assertEqual(image.getcolors(), [(4, (0, 0, 255, 0))])
        self.assertEqual(tiles[3].tilecoord, TileCoord(1, 1, 1))
        image = Image.open(BytesIO(tiles[3].data))
        self.assertEqual(image.size, (2, 2))
        self.assertEqual(image.getcolors(), [(4, (0, 0, 0, 255))])


class TestMetaTileSplitterTileStoreWithBorder(unittest.TestCase):
    def setUp(self) -> None:
        self.mtsts = MetaTileSplitterTileStore("image/png", tile_size=2, border=2)

    def test_get(self) -> None:
        image = Image.new("RGBA", (8, 8))
        image.paste((255, 0, 0, 0), (0, 0, 4, 4))
        image.paste((0, 255, 0, 0), (0, 4, 4, 8))
        image.paste((0, 0, 255, 0), (4, 0, 8, 4))
        image.paste((0, 0, 0, 255), (4, 4, 8, 8))
        string_io = BytesIO()
        image.save(string_io, "PNG")
        tile = Tile(TileCoord(1, 0, 0, 2), data=string_io.getvalue())
        tiles = list(self.mtsts.get([tile]))
        self.assertEqual(len(tiles), 4)
        self.assertEqual(tiles[0].tilecoord, TileCoord(1, 0, 0))
        image = Image.open(BytesIO(tiles[0].data))
        self.assertEqual(image.size, (2, 2))
        self.assertEqual(image.getcolors(), [(4, (255, 0, 0, 0))])
        self.assertEqual(tiles[1].tilecoord, TileCoord(1, 0, 1))
        image = Image.open(BytesIO(tiles[1].data))
        self.assertEqual(image.size, (2, 2))
        self.assertEqual(image.getcolors(), [(4, (0, 255, 0, 0))])
        self.assertEqual(tiles[2].tilecoord, TileCoord(1, 1, 0))
        image = Image.open(BytesIO(tiles[2].data))
        self.assertEqual(image.size, (2, 2))
        self.assertEqual(image.getcolors(), [(4, (0, 0, 255, 0))])
        self.assertEqual(tiles[3].tilecoord, TileCoord(1, 1, 1))
        image = Image.open(BytesIO(tiles[3].data))
        self.assertEqual(image.size, (2, 2))
        self.assertEqual(image.getcolors(), [(4, (0, 0, 0, 255))])
