import os
from subprocess import call  # nosec
from tempfile import NamedTemporaryFile

from tilecloud import Tile


class OptiPNG:
    """Optimize PNG tiles with optipng."""

    def __init__(self, options: list[str], arg0: str = "/usr/bin/optipng") -> None:
        self.args = [arg0, "-q", *list(options)]

    def __call__(self, tile: Tile) -> Tile:
        with NamedTemporaryFile(delete=False, suffix=".png") as ntf:
            try:
                assert tile.data is not None
                ntf.write(tile.data)
                ntf.close()
                retcode = call([*self.args, ntf.name])  # noqa: S603
                if retcode == 0:
                    with open(ntf.name, "rb") as file:
                        tile.data = file.read()
            finally:
                try:
                    os.unlink(ntf.name)
                except OSError:
                    pass
            return tile
