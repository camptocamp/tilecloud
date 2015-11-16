from collections import defaultdict
from datetime import datetime
import re
import os.path
import zipfile

from tilecloud import Tile, TileStore
from tilecloud.layout.osm import OSMTileLayout
from tilecloud.layout.wrapped import WrappedTileLayout


class ZipTileStore(TileStore):

    def __init__(self, zipfile, layout=None, **kwargs):
        TileStore.__init__(self, **kwargs)
        self.zipfile = zipfile
        self.layout = layout
        if self.layout is None:
            extension_count = defaultdict(int)
            for name in self.zipfile.namelist():
                extension_count[os.path.splitext(name)[1]] += 1
            for extension, count in sorted(extension_count.items(), key=lambda p: tuple(reversed(p)), reverse=True):
                if re.match(r'\.(jpe?g|png)\Z', extension, re.I):
                    self.layout = WrappedTileLayout(OSMTileLayout(), suffix=extension)
                    break
        if self.layout is None:
            self.layout = OSMTileLayout()

    def __contains__(self, tile):
        if not tile:
            return False
        try:
            filename = self.layout.filename(tile.tilecoord)
            self.zipfile.getinfo(filename)
            return True
        except KeyError:
            return False

    def get_one(self, tile):
        if hasattr(tile, 'zipinfo'):
            tile.data = self.zipfile.read(tile.zipinfo)
        else:
            filename = self.layout.filename(tile.tilecoord)
            tile.data = self.zipfile.read(filename)
        return tile

    def list(self):
        for zipinfo in self.zipfile.infolist():
            try:
                yield Tile(self.layout.tilecoord(zipinfo.filename), zipinfo=zipinfo)
            except ValueError:
                pass

    def put_one(self, tile):
        filename = self.layout.filename(tile.tilecoord)
        zipinfo = zipfile.ZipInfo(filename)
        zipinfo.compress_type = getattr(self, 'compress_type', zipfile.ZIP_DEFLATED)
        zipinfo.date_time = datetime.now().timetuple()[:6]
        zipinfo.external_attr = 0o644 << 16
        self.zipfile.writestr(zipinfo, tile.data)
        return tile
