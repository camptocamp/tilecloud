import os.path
import re
import zipfile
from collections import defaultdict
from collections.abc import Iterator
from datetime import datetime
from typing import Any, Optional

from tilecloud import NotSupportedOperation, Tile, TileLayout, TileStore
from tilecloud.layout.osm import OSMTileLayout
from tilecloud.layout.wrapped import WrappedTileLayout


class ZipTileStore(TileStore):
    def __init__(
        self, zipfile: zipfile.ZipFile, layout: Optional[TileLayout] = None, **kwargs: Any
    ):  # pylint: disable=redefined-outer-name
        TileStore.__init__(self, **kwargs)
        self.zipfile = zipfile
        if layout is None:
            extension_count: dict[str, int] = defaultdict(int)
            for name in self.zipfile.namelist():
                extension_count[os.path.splitext(name)[1]] += 1
            for extension, _ in sorted(
                extension_count.items(), key=lambda p: tuple(reversed(p)), reverse=True
            ):
                if re.match(r"\.(jpe?g|png)\Z", extension, re.I):
                    layout = WrappedTileLayout(OSMTileLayout(), suffix=extension)
                    break
        if layout is None:
            layout = OSMTileLayout()
        self.layout = layout

    def __contains__(self, tile: Tile) -> bool:
        if not tile:
            return False
        try:
            filename = self.layout.filename(tile.tilecoord, tile.metadata)
            self.zipfile.getinfo(filename)
            return True
        except KeyError:
            return False

    def get_one(self, tile: Tile) -> Optional[Tile]:
        if tile is None:
            return None
        if hasattr(tile, "zipinfo"):
            tile.data = self.zipfile.read(tile.zipinfo)
        else:
            filename = self.layout.filename(tile.tilecoord, tile.metadata)
            tile.data = self.zipfile.read(filename)
        return tile

    def list(self) -> Iterator[Tile]:
        for zipinfo in self.zipfile.infolist():
            try:
                yield Tile(self.layout.tilecoord(zipinfo.filename), zipinfo=zipinfo)
            except ValueError:
                pass

    def put_one(self, tile: Tile) -> Tile:
        if tile is None:
            return None
        assert tile.data is not None
        filename = self.layout.filename(tile.tilecoord, tile.metadata)
        zipinfo = zipfile.ZipInfo(filename)
        zipinfo.compress_type = getattr(self, "compress_type", zipfile.ZIP_DEFLATED)
        zipinfo.date_time = datetime.now().timetuple()[:6]
        zipinfo.external_attr = 0o644 << 16
        self.zipfile.writestr(zipinfo, tile.data)
        return tile

    def delete_one(self, tile: Tile) -> Tile:
        raise NotSupportedOperation()
