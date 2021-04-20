import os
from subprocess import call
from tempfile import NamedTemporaryFile
from typing import List

from tilecloud import Tile


class OptiPNG:
    def __init__(self, options: List[str], arg0: str = "/usr/bin/optipng"):
        self.args = [arg0, "-q"] + list(options)

    def __call__(self, tile: Tile) -> Tile:
        ntf = NamedTemporaryFile(delete=False, suffix=".png")
        try:
            assert tile.data is not None
            ntf.write(tile.data)
            ntf.close()
            retcode = call(self.args + [ntf.name])
            if retcode == 0:
                with open(ntf.name, "rb") as f:
                    tile.data = f.read()
        finally:
            try:
                os.unlink(ntf.name)
            except IOError:
                pass
        return tile
