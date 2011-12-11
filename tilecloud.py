#!/usr/bin/env python

# FIXME handle S3 403/404
# TODO generate tilecoords from coordinate systems (pyproj)
# TODO extend BinaryMaskTileStore to support multiple zs
# TODO PNG optimizer
# TODO periodically flush BinaryMaskTileStore

from cStringIO import StringIO
import collections
from gzip import GzipFile
from itertools import imap, islice
import logging
import os
import os.path
import re
from ssl import SSLError
import sys

import boto.s3.connection
import PIL.Image


if __name__ == '__main__':
    logger = logging.getLogger(os.path.basename(sys.argv[0]))
else:
    logger = logging.getLogger(__name__)


def consume(iterator, n):
    "Advance the iterator n-steps ahead. If n is none, consume entirely."
    # Use functions that consume iterators at C speed.
    if n is None:
        # feed the entire iterator into a zero-length deque
        collections.deque(iterator, maxlen=0)
    else:
        # advance to the empty slice starting at position n
        next(islice(iterator, n, n), None)


class Bounds(object):

    def __init__(self, start=None, stop=None):
        self.start = start
        if stop is None:
            self.stop = self.start + 1 if start is not None else None
        else:
            assert start is not None
            self.stop = stop

    def __contains__(self, key):
        if self.start is None:
            return False
        else:
            return self.start <= key < self.stop

    def __len__(self):
        if self.start is None:
            return 0
        else:
            return self.stop - self.start

    def __iter__(self):
        if self.start is not None:
            for i in xrange(self.start, self.stop):
                yield i

    def __repr__(self):
        if self.start is None:
            return '%s(None)' % (self.__class__.__name__,)
        else:
            return '%s(%r, %r)' % (self.__class__.__name__, self.start, self.stop)

    def add(self, value):
        if self.start is None:
            self.start = value
            self.stop = value + 1
        else:
            self.start = min(self.start, value)
            self.stop = max(self.stop, value + 1)

    def update(self, other):
        if self.start is None:
            self.start = other.start
            self.stop = other.stop
        else:
            self.start = min(self.start, other.start)
            self.stop = max(self.stop, other.stop)

    def union(self, other):
        if self and other:
            return Bounds(min(self.start, other.start), max(self.start, other.start))
        elif self:
            return Bounds(self.start, self.stop)
        elif other:
            return Bounds(other.start, other.stop)
        else:
            return Bounds()


class BoundingPyramid(object):

    def __init__(self, bounds=None):
        self.bounds = bounds or {}

    def __contains__(self, tilecoord):
        if tilecoord.z not in self.bounds:
            return False
        xbounds, ybounds = self.bounds[tilecoord.z]
        return tilecoord.x in xbounds and tilecoord.y in ybounds

    def __iter__(self):
        return self.itertopdown()

    def __len__(self):
        return sum(len(xbounds) * len(ybounds) for xbounds, ybounds in self.bounds.itervalues())

    def add(self, tilecoord):
        if tilecoord.z in self.bounds:
            xbounds, ybounds = self.bounds[tilecoord.z]
            xbounds.add(tilecoord.x)
            ybounds.add(tilecoord.y)
        else:
            self.bounds[tilecoord.z] = (Bounds(tilecoord.x), Bounds(tilecoord.y))

    def filldown(self, bottom, start=None):
        if start is None:
            start = max(self.bounds)
        for z in xrange(start, bottom):
            xbounds, ybounds = self.bounds[z]
            self.add(TileCoord(z + 1, xbounds.start * 2, ybounds.start * 2))
            self.add(TileCoord(z + 1, xbounds.stop * 2, ybounds.stop * 2))

    def fillup(self, top=0):
        for z in xrange(max(self.bounds), top, -1):
            xbounds, ybounds = self.bounds[z]
            self.add(TileCoord(z - 1, xbounds.start // 2, ybounds.start // 2))
            self.add(TileCoord(z - 1, xbounds.stop // 2, ybounds.stop // 2))

    def iterbottomup(self):
        for z in reversed(sorted(self.bounds.keys())):
            for tilecoord in self.ziter(z):
                yield tilecoord

    def itertopdown(self):
        for z in sorted(self.bounds.keys()):
            for tilecoord in self.ziter(z):
                yield tilecoord

    def ziter(self, z):
        if z in self.bounds:
            xbounds, ybounds = self.bounds[z]
            for x in xbounds:
                for y in ybounds:
                    yield TileCoord(z, x, y)

    @classmethod
    def from_string(cls, s):
        match = re.match(r'(?P<z1>\d+)/(?P<x1>\d+)/(?P<y1>\d+):(?:(?P<z2>\d+)/)?(?P<x2>\d+)/(?P<y2>\d+)\Z', s)
        if not match:
            raise RuntimeError # FIXME
        z1 = int(match.group('z1'))
        xbounds = Bounds(int(match.group('x1')), int(match.group('x2')))
        ybounds = Bounds(int(match.group('y1')), int(match.group('y2')))
        result = cls({z1: (xbounds, ybounds)})
        if match.group('z2'):
            z2 = int(match.group('z2'))
            if z1 < z2:
                result.filldown(z2)
            elif z1 > z2:
                result.fillup(z2)
        return result



class TileCoord(object):
    """A tile coordinate"""

    def __init__(self, z, x, y):
        self.z = z
        self.x = x
        self.y = y

    def __repr__(self):
        return '%s(%r, %r, %r)' % (self.__class__.__name__, self.z, self.x, self.y)

    def __str__(self):
        return '%d/%d/%d' % (self.z, self.x, self.y)

    def normalize(self):
        return (float(self.x) / (1 << self.z), float(self.y) / (1 << self.z))

    @classmethod
    def from_normalized_coord(cls, z, xy):
        return cls(z, int(xy[0] * (1 << z)), int(xy[1] * (1 << z)))



class TileLayout(object):
    """Maps tile coordinates to filenames and vice versa"""

    def __init__(self, pattern, filename_re):
        self.pattern = pattern
        self.filename_re = filename_re

    def filename(self, tilecoord):
        """Return the filename for the given tile coordinate"""
        raise NotImplementedError

    def tilecoord(self, filename):
        """Return the tile coordinate for the given filename"""
        match = self.filename_re.match(filename)
        if not match:
            raise RuntimeError # FIXME
        return self._tilecoord(match)

    def _tilecoord(self, match):
        raise NotImplementedError



class OSMTileLayout(TileLayout):
    """OpenStreetMap tile layout"""

    PATTERN = r'[0-9]+/[0-9]+/[0-9]+'
    RE = re.compile(r'([0-9]+)/([0-9]+)/([0-9]+)\Z')

    def __init__(self):
        TileLayout.__init__(self, self.PATTERN, self.RE)

    def filename(self, tilecoord):
        return '%d/%d/%d' % (tilecoord.z, tilecoord.x, tilecoord.y)

    def _tilecoord(self, match):
        return TileCoord(*map(int, match.groups()))



class I3DTileLayout(TileLayout):
    """I3D (FHNW/OpenWebGlobe) tile layout"""

    PATTERN = r'(?:[0-3]{2}/)*[0-3]{1,2}'
    RE = re.compile(PATTERN + r'\Z')

    def __init__(self):
        TileLayout.__init__(self, self.PATTERN, self.RE)

    def filename(self, tilecoord):
        return '/'.join(re.findall(r'[0-3]{1,2}', I3DTileLayout.quadcode_from_tilecoord(tilecoord)))

    def _tilecoord(self, match):
        return I3DTileLayout.tilecoord_from_quadcode(re.sub(r'/', '', match.group()))

    @staticmethod
    def quadcode_from_tilecoord(tilecoord):
        x, y = tilecoord.x, tilecoord.y
        result = ''
        for i in xrange(0, tilecoord.z):
            result += '0123'[(x & 1) + ((y & 1) << 1)]
            x >>= 1
            y >>= 1
        return result[::-1]

    @staticmethod
    def tilecoord_from_quadcode(quadcode):
        z, x, y = len(quadcode), 0, 0
        for i, c in enumerate(quadcode):
            mask = 1 << (z - i - 1)
            if c == '1' or c == '3':
                x |= mask
            if c == '2' or c == '3':
                y |= mask
        return TileCoord(z, x, y)



class WrappedTileLayout(object):
    """A tile layout with an option prefix and/or suffix"""

    def __init__(self, tile_layout, prefix='', suffix=''):
        self.tile_layout = tile_layout
        self.prefix = prefix
        self.suffix = suffix
        prefix_re = re.escape(self.prefix)
        suffix_re = re.escape(self.suffix)
        self.pattern = ''.join((prefix_re, tile_layout.pattern, suffix_re))
        self.filename_re = re.compile(''.join((prefix_re, r'(', self.tile_layout.pattern, r')', suffix_re, r'\Z')))

    def filename(self, tilecoord):
        return ''.join((self.prefix, self.tile_layout.filename(tilecoord), self.suffix))

    def tilecoord(self, filename):
        match = self.filename_re.match(filename)
        if not match:
            raise RuntimeError # FIXME
        return self.tile_layout.tilecoord(match.group(1))



class Tile(object):
    """An actual tile with optional metadata"""

    def __init__(self, tilecoord, **kwargs):
        self.tilecoord = tilecoord
        for key, value in kwargs.items():
            setattr(self, key, value)



class TileStore(object):
    """A tile store"""

    def delete(self, tiles):
        """A generator that has the side effect of deleting the specified tiles from the store"""
        return imap(self.delete_one, tiles)

    def delete_one(self, tile):
        """A function that deletes tile from the store and returns the tile"""
        raise NotImplementedError

    def get(self, tiles):
        """A generator that returns the specified tiles and their data from the store"""
        return imap(self.get_one, tiles)

    def get_all(self):
        """A generator that returns all the tiles in the store with their data"""
        return self.imap(self.get_one, self.list())

    def get_one(self, tile):
        """A function that gets the specified tile and its data from the store"""
        raise NotImplementedError

    def list(self):
        """A generator that returns the tiles in the store without necessarily retrieving their data"""
        raise NotImplementedError

    def put(self, tiles):
        """A generator that has the side effect of putting the specified tiles in the store"""
        return imap(self.put_one, tiles)

    def put_one(self, tile):
        """A function that puts tile in the store and returns the tile"""
        raise NotImplementedError



class BoundingPyramidTileStore(TileStore):
    """All tiles in a bounding box"""

    def __init__(self, bounding_pyramid=None):
        self.bounding_pyramid = bounding_pyramid or BoundingPyramid()

    def list(self):
        for tilecoord in self.bounding_pyramid:
            yield Tile(tilecoord)

    def put_one(self, tile):
        self.bounding_pyramid.add(tile.tilecoord)
        return tile



class FilesystemTileStore(TileStore):
    """Tiles stored in a filesystem"""

    def __init__(self, tile_layout):
        self.tile_layout = tile_layout

    def delete_one(self, tile):
        filename = self.tile_layout.filename(tile.tilecoord)
        if os.path.exists(filename):
            os.remove(filename)
        return tile

    def get_one(self, tile):
        filename = self.tile_layout.filename(tile.tilecoord)
        with open(filename) as file:
            tile.data = file.read()
        return tile

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



class LinesTileStore(TileStore):
    """Generates all tile coordinates matching the specified layout from lines"""

    def __init__(self, tile_layout, lines=None):
        self.tile_layout = tile_layout
        self.lines = lines

    def list(self):
        # FIXME warn that this consumes lines
        filename_re = re.compile(self.tile_layout.pattern)
        for line in self.lines:
            match = filename_re.search(line)
            if match:
                yield Tile(self.tile_layout.tilecoord(match.group()), line=line)



class MaskTileStore(TileStore):
    """A black and white image representing present and absent tiles"""

    def __init__(self, z, slices, file=None):
        self.z = z
        self.xbounds, self.ybounds = slices
        self.width = self.xbounds.stop - self.xbounds.start
        self.height = self.ybounds.stop - self.ybounds.start
        if file:
            self.image = PIL.Image.open(file)
            assert self.image.mode == '1'
            assert self.image.size == (self.width, self.height)
        else:
            self.image = PIL.Image.new('1', (self.width, self.height))
        self.pixels = self.image.load()

    def delete_one(self, tile):
        if tile.tilecoord.z == self.z:
            x = tile.tilecoord.x - self.xbounds.start
            y = self.ybounds.stop - tile.tilecoord.y - 1
            if 0 <= x < self.width and 0 <= y < self.height:
                self.pixels[x, y] = 0
        return tile

    def list(self):
        for x in xrange(0, self.width):
            for y in xrange(0, self.height):
                if self.pixels[x, y]:
                    yield Tile(TileCoord(self.z, self.xbounds.start + x, self.ybounds.stop - y - 1))

    def put_one(self, tile):
        x = tile.tilecoord.x - self.xbounds.start
        y = self.ybounds.stop - tile.tilecoord.y - 1
        if 0 <= x < self.width and 0 <= y < self.height:
            self.pixels[x, y] = 1
        return tile

    def save(self, file, format, **kwargs):
        self.image.save(file, format, **kwargs)



class S3Bucket(object):
    """Provides a more robust wrapper around braindead boto's boto.s3.Bucket"""

    def __init__(self, name, bucket=None, s3connection=None, s3connection_factory=boto.s3.connection.S3Connection):
        self.name = name
        self.s3connection_factory = s3connection_factory
        self.bucket = bucket
        self.s3connection = s3connection

    def boto_is_braindead(self):
        """Keeps yielding buckets until one doesn't raise an SSLError"""
        while True:
            try:
                if not self.bucket:
                    if not self.s3connection:
                        assert callable(self.s3connection_factory)
                        self.s3connection = self.s3connection_factory()
                    assert self.name
                    self.bucket = self.s3connection.get_bucket(self.name)
                yield self.bucket
                break
            except SSLError as exc:
                logger.warning(exc)
                if callable(self.s3connection_factory) and self.name:
                    self.s3connection = None
                    self.bucket = None
                else:
                    raise



class S3TileStore(TileStore):
    """Tiles stored in Amazon S3"""

    def __init__(self, bucket_name, tile_layout, bucket=None, dry_run=False, s3connection=None, s3connection_factory=boto.s3.connection.S3Connection):
        self.dry_run = dry_run
        self.s3bucket = S3Bucket(bucket_name, bucket=bucket, s3connection=s3connection, s3connection_factory=s3connection_factory)
        self.tile_layout = tile_layout

    def delete_one(self, tile):
        key_name = self.tile_layout.filename(tile.tilecoord)
        for bucket in self.s3bucket.boto_is_braindead():
            if not self.dry_run:
                bucket.delete_key(key_name)
            return tile

    def get_one(self, tile):
        key_name = self.tile_layout.filename(tile.tilecoord)
        for bucket in self.s3bucket.boto_is_braindead():
            s3key = bucket.new_key(key_name)
            return Tile(tile.tilecoord, data=s3key.read(), s3key=s3key)

    def list(self):
        prefix = getattr(self.tile_layout, 'prefix', '')
        marker = ''
        while True:
            for bucket in self.s3bucket.boto_is_braindead():
                s3keys = bucket.get_all_keys(prefix=prefix, marker=marker)
                break
            for s3key in s3keys:
                yield Tile(self.tile_layout.tilecoord(s3key.name), s3key=s3key)
            if s3keys.is_truncated:
                marker = s3key.name
            else:
                break

    def put_one(self, tile):
        key_name = self.tile_layout.filename(tile.tilecoord)
        for bucket in self.s3bucket.boto_is_braindead():
            s3key = bucket.new_key(key_name)
            headers = {}
            if hasattr(tile, 'content_encoding'):
                headers['Content-Encoding'] = tile.content_encoding
            if hasattr(tile, 'content_type'):
                headers['Content-Type'] = tile.content_type
            if hasattr(tile, 'data'):
                if not self.dry_run:
                    s3key.set_contents_from_string(tile.data, headers)
            else:
                assert False
            return tile



class ContentTypeAdder(object):
    """A class that adds a content type to a tile"""

    def __init__(self, content_type):
        self.content_type = content_type

    def __call__(self, tile):
        tile.content_type = self.content_type
        return tile



class GzipCompressor(object):
    """A class that compresses a tile with gzip"""

    def __init__(self, compresslevel=9):
        self.compresslevel = compresslevel

    def __call__(self, tile):
        assert hasattr(tile, 'data')
        string_io = StringIO()
        gzip_file = GzipFile(compresslevel=self.compresslevel, fileobj=string_io, mode='w')
        gzip_file.write(tile.data)
        gzip_file.close()
        return Tile(tile.tilecoord, data=string_io.getvalue(), content_encoding='gzip')



class ImageFormatConverter(object):
    """A class that converts a tile into the desired format"""

    def __init__(self, content_type, **kwargs):
        self.content_type = content_type
        self.kwargs = kwargs
        if self.content_type == 'image/jpeg':
            self.format = 'JPEG'
        elif content_type == 'image/png':
            self.format = 'PNG'
        else:
            assert False

    def __call__(self, tile):
        assert hasattr(tile, 'data')
        string_io = StringIO()
        PIL.Image.open(StringIO(tile.data)).save(string_io, self.format, **self.kwargs)
        return Tile(tile.tilecoord, data=string_io.getvalue(), content_type=self.content_type)



class Logger(object):

    def __init__(self, logger, level, msgformat, *args, **kwargs):
        self.logger = logger
        self.level = level
        self.msgformat = msgformat
        self.args = args
        self.kwargs = kwargs

    def __call__(self, tile):
        variables = dict()
        variables.update(tile.__dict__)
        variables.update(tile.tilecoord.__dict__)
        logger.log(self.level, self.msgformat % variables, *self.args, **self.kwargs)
        return tile
