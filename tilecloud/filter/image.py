"""
This module includes filters doing manipulations on the tile image.

It requires the PIL lib.
"""

from io import BytesIO
from typing import Any, Callable, Optional

import PIL.Image

from tilecloud import Tile, TileStore
from tilecloud.lib.PIL_ import FORMAT_BY_CONTENT_TYPE


class ImageFormatConverter:
    """
    Create a filter that converts a tile into the desired format.

        content_type:
        The content type representing the format to convert the tile image
        to.

        kwargs:
        Extra arguments passed to ``PIL`` when opening the tile image.
    """

    def __init__(self, content_type: str, **kwargs: Any):
        self.content_type = content_type
        self.kwargs = kwargs
        self.format = FORMAT_BY_CONTENT_TYPE[content_type]

    def __call__(self, tile: Tile) -> Tile:
        if tile.content_type != self.content_type:
            assert tile.data is not None
            bytes_io = BytesIO()
            PIL.Image.open(BytesIO(tile.data)).save(bytes_io, self.format, **self.kwargs)
            tile.content_type = self.content_type
            tile.data = bytes_io.getvalue()
        return tile


class MergeFilter:
    """
    Create a filter that merges the tile with tiles of the same coordinates.

        tilestores:
        A collection of :class:`TileStore` objects from which tiles to
        merge with the currently handled tile are read.

        content_type:
        The content type to set in the tile. If ``None`` the content
        type of the first tile found in the stream is used for every
        other tile. Default is ``None``.
    """

    def __init__(self, tilestores: list[TileStore], content_type: Optional[str] = None, **kwargs: Any):
        self.tilestores = list(tilestores)
        self.content_type = content_type
        self.kwargs = kwargs

    def __call__(self, tile: Tile) -> Tile:
        assert tile.data is not None
        image = PIL.Image.open(BytesIO(tile.data))
        for tilestore in self.tilestores:
            sub_tile = tilestore.get_one(Tile(tile.tilecoord))
            if sub_tile is not None:
                assert sub_tile.data is not None
                image2 = PIL.Image.open(BytesIO(sub_tile.data))
                image.paste(image2, None, image2)
        content_type = self.content_type
        if content_type is None:
            content_type = tile.content_type
        assert content_type is not None
        bytes_io = BytesIO()
        image.save(bytes_io, FORMAT_BY_CONTENT_TYPE[content_type], **self.kwargs)
        tile.content_type = content_type
        tile.data = bytes_io.getvalue()
        return tile


class PILImageFilter:
    """
    Create a filter to filter the tile image (with the PIL ``filter`` function).

        filter:
        The filter to pass to the PIL ``filter`` function.

        kwargs:
        Extra params passed to the PIL ``save`` function.
    """

    def __init__(self, filter_pattern: Callable[[Tile], Tile], **kwargs: Any):
        self.filter = filter_pattern
        self.kwargs = kwargs

    def __call__(self, tile: Tile) -> Tile:
        assert tile.data is not None
        image = PIL.Image.open(BytesIO(tile.data))
        image = image.filter(self.filter)  # type: ignore[no-untyped-call]
        bytes_io = BytesIO()
        assert tile.content_type is not None
        image.save(bytes_io, FORMAT_BY_CONTENT_TYPE.get(tile.content_type, "PNG"), **self.kwargs)
        tile.data = bytes_io.getvalue()
        return tile
