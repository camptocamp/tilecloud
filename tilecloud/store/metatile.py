from collections.abc import Iterable, Iterator
from io import BytesIO
from typing import Any

from PIL import Image

from tilecloud import NotSupportedOperation, Tile, TileStore
from tilecloud.lib.PIL_ import FORMAT_BY_CONTENT_TYPE


class MetaTileSplitterTileStore(TileStore):
    """A tile store that splits metatiles into tiles."""

    def __init__(self, format_pattern: str, tile_size: int = 256, border: int = 0, **kwargs: Any) -> None:
        self.format = format_pattern
        self.tile_size = tile_size
        self.border = border
        TileStore.__init__(self, **kwargs)

    def get(self, tiles: Iterable[Tile | None]) -> Iterator[Tile]:
        for metatile in tiles:
            if not metatile:
                continue
            if isinstance(metatile.data, bytes):
                metaimage = Image.open(BytesIO(metatile.data))
                for tilecoord in metatile.tilecoord:
                    if metatile.error:
                        yield Tile(
                            tilecoord,
                            metadata=metatile.metadata,
                            error=metatile.error,
                            metatile=metatile,
                        )
                        continue
                    if metatile.data is None:
                        yield Tile(
                            tilecoord,
                            metadata=metatile.metadata,
                            error="Metatile data is None",
                            metatile=metatile,
                        )
                        continue

                    x = (  # pylint: disable=invalid-name
                        self.border + (tilecoord.x - metatile.tilecoord.x) * self.tile_size
                    )
                    y = (  # pylint: disable=invalid-name
                        self.border + (tilecoord.y - metatile.tilecoord.y) * self.tile_size
                    )
                    image = metaimage.crop((x, y, x + self.tile_size, y + self.tile_size))
                    bytes_io = BytesIO()
                    image.save(bytes_io, FORMAT_BY_CONTENT_TYPE[self.format])
                    yield Tile(
                        tilecoord,
                        data=bytes_io.getvalue(),
                        content_type=self.format,
                        metadata=metatile.metadata,
                        metatile=metatile,
                    )

    def get_one(self, tile: Tile) -> Tile:
        raise NotSupportedOperation

    def put_one(self, tile: Tile) -> Tile:
        raise NotSupportedOperation

    def delete_one(self, tile: Tile) -> Tile:
        raise NotSupportedOperation
