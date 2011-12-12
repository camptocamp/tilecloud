import errno
import os
import os.path

from tilecloud import Tile, TileStore



class FilesystemTileStore(TileStore):
    """Tiles stored in a filesystem"""

    def __init__(self, tile_layout):
        self.tile_layout = tile_layout

    def delete_one(self, tile):
        filename = self.tile_layout.filename(tile.tilecoord)
        if os.path.exists(filename):
            os.remove(filename)
        return tile

    def get_all(self):
        for tile in self.list():
            with open(tile.path) as file:
                tile.data = file.read()
            yield tile

    def get_one(self, tile):
        filename = self.tile_layout.filename(tile.tilecoord)
        try:
            with open(filename) as file:
                tile.data = file.read()
            return tile
        except IOError as e:
            if e.errno == errno.ENOENT:
                return None
            else:
                raise

    def list(self):
        top = getattr(self.tile_layout, 'prefix', '.')
        for dirpath, dirnames, filenames in os.walk(top):
            for filename in filenames:
                path = os.path.join(dirpath, filename)
                tilecoord = self.tile_layout.tilecoord(path)
                if tilecoord:
                    yield Tile(tilecoord, path=path)

    def put_one(self, tile):
        filename = self.tile_layout.filename(tile.tilecoord)
        dirname = os.path.dirname(filename)
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        with open(filename, 'w') as file:
            if hasattr(tile, 'data'):
                file.write(tile.data)
            else:
                assert False
        return tile
