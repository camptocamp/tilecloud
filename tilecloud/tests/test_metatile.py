from io import BytesIO

import pytest
from PIL import Image

from tilecloud import Tile, TileCoord
from tilecloud.lib.PIL_ import FORMAT_BY_CONTENT_TYPE
from tilecloud.store.metatile import MetaTileSplitterTileStore


@pytest.mark.parametrize("mime_type", ["image/png"])
def test_split(mime_type: str) -> None:
    """
    Test splitting a metatile into tiles without border.
    """
    mtsts = MetaTileSplitterTileStore(mime_type, tile_size=2, save_options={"lossless": True})
    image = Image.new("RGBA", (4, 4))
    image.paste((255, 0, 0, 0), (0, 0, 2, 2))
    image.paste((0, 255, 0, 0), (0, 2, 2, 4))
    image.paste((0, 0, 255, 0), (2, 0, 4, 2))
    image.paste((0, 0, 0, 255), (2, 2, 4, 4))
    string_io = BytesIO()
    image.save(string_io, FORMAT_BY_CONTENT_TYPE[mime_type])
    tile = Tile(TileCoord(1, 0, 0, 2), data=string_io.getvalue())
    tiles = list(mtsts.get([tile]))
    assert len(tiles) == 4
    assert tiles[0].tilecoord == TileCoord(1, 0, 0)
    image = Image.open(BytesIO(tiles[0].data))
    assert image.size == (2, 2)
    assert image.getpixel((0, 0)) == (255, 0, 0, 0)
    assert tiles[1].tilecoord == TileCoord(1, 0, 1)
    image = Image.open(BytesIO(tiles[1].data))
    assert image.size == (2, 2)
    assert image.getpixel((0, 0)) == (0, 255, 0, 0)
    assert tiles[2].tilecoord == TileCoord(1, 1, 0)
    image = Image.open(BytesIO(tiles[2].data))
    assert image.size == (2, 2)
    assert image.getpixel((0, 0)) == (0, 0, 255, 0)
    assert tiles[3].tilecoord == TileCoord(1, 1, 1)
    image = Image.open(BytesIO(tiles[3].data))
    assert image.size == (2, 2)
    assert image.getpixel((0, 0)) == (0, 0, 0, 255)


@pytest.mark.parametrize("mime_type", ["image/png"])
def test_split_border(mime_type: str) -> None:
    """
    Test splitting a metatile into tiles with border.
    """
    mtsts = MetaTileSplitterTileStore(mime_type, tile_size=2, border=2, save_options={"lossless": True})
    image = Image.new("RGBA", (8, 8))
    image.paste((255, 0, 0, 0), (0, 0, 4, 4))
    image.paste((0, 255, 0, 0), (0, 4, 4, 8))
    image.paste((0, 0, 255, 0), (4, 0, 8, 4))
    image.paste((0, 0, 0, 255), (4, 4, 8, 8))
    string_io = BytesIO()
    image.save(string_io, FORMAT_BY_CONTENT_TYPE[mime_type])
    tile = Tile(TileCoord(1, 0, 0, 2), data=string_io.getvalue())
    tiles = list(mtsts.get([tile]))
    assert len(tiles) == 4
    assert tiles[0].tilecoord == TileCoord(1, 0, 0)
    image = Image.open(BytesIO(tiles[0].data))
    assert image.size == (2, 2)
    assert image.getpixel((0, 0)) == (255, 0, 0, 0)
    assert tiles[1].tilecoord == TileCoord(1, 0, 1)
    image = Image.open(BytesIO(tiles[1].data))
    assert image.size == (2, 2)
    assert image.getpixel((0, 0)) == (0, 255, 0, 0)
    assert tiles[2].tilecoord == TileCoord(1, 1, 0)
    image = Image.open(BytesIO(tiles[2].data))
    assert image.size == (2, 2)
    assert image.getpixel((0, 0)) == (0, 0, 255, 0)
    assert tiles[3].tilecoord == TileCoord(1, 1, 1)
    image = Image.open(BytesIO(tiles[3].data))
    assert image.size == (2, 2)
    assert image.getpixel((0, 0)) == (0, 0, 0, 255)
