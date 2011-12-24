import os
from subprocess import call
from tempfile import NamedTemporaryFile


class OptiPNG(object):

    def __init__(self, options, arg0='/usr/bin/optipng'):
        self.args = [arg0, '-q'] + list(options)

    def __call__(self, tile):
        ntf = NamedTemporaryFile(delete=False, suffix='.png')
        try:
            ntf.write(tile.data)
            ntf.close()
            retcode = call(self.args + [ntf.name])
            if retcode == 0:
                with open(ntf.name) as f:
                    tile.data = f.read()
        finally:
            try:
                os.unlink(ntf.name)
            except IOError:
                pass
        return tile
