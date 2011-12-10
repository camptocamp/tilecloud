#!/usr/bin/env python

# FIXME handle S3 403/404
# TODO generate tilecoords from coordinate systems (pyproj)
# TODO read tiles from database
# TODO write tiles to database
# TODO extend BinaryMaskTileStore to support multiple zs

from cStringIO import StringIO
import collections
from itertools import islice, repeat, starmap
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


def repeatfunc(func, times=None, *args):
    """Repeat calls to func with specified arguments.

    Example:  repeatfunc(random.random)
    """
    if times is None:
        return starmap(func, repeat(args))
    return starmap(func, repeat(args, times))


class TileCoord(object):
    """A tile coordinate"""

    def __init__(self, z, x, y):
        self.z = z
        self.x = x
        self.y = y

    def quadcode(self):
        x, y = self.x, self.y
        result = ''
        for i in xrange(0, self.z):
            result += '0123'[(x & 1) + ((y & 1) << 1)]
            x >>= 1
            y >>= 1
        return result[::-1]

    def __repr__(self):
        return '%s(%r, %r, %r)' % (self.__class__.__name__, self.z, self.x, self.y)

    def __str__(self):
        return '%d/%d/%d' % (self.z, self.x, self.y)

    @classmethod
    def from_quadcode(cls, quadcode):
        z, x, y = len(quadcode), 0, 0
        for i, c in enumerate(quadcode):
            mask = 1 << (z - i - 1)
            if c == '1' or c == '3':
                x |= mask
            if c == '2' or c == '3':
                y |= mask
        return cls(z, x, y)


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
        return '/'.join(re.findall(r'[0-3]{1,2}', tilecoord.quadcode()))

    def _tilecoord(self, match):
        return TileCoord.from_quadcode(re.sub(r'/', '', match.group()))


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
        raise NotImplementedError

    def get(self, tiles):
        raise NotImplementedError

    def list(self):
        raise NotImplementedError

    def put(self, tiles):
        raise NotImplementedError


class BoundingBoxTileStore(TileStore):
    """All tile coordinates in a bounding box"""

    def __init__(self, bounds=None):
        self.bounds = bounds or {}

    def get(self):
        for z in sorted(self.bounds.keys()):
            xslice, yslice = self.bounds[z]
            for x in xrange(xslice.start, xslice.stop):
                for y in xrange(yslice.start, yslice.stop):
                    yield Tile(TileCoord(z, x, y))

    list = get

    def put(self, tiles):
        for tile in tiles:
            tilecoord = tile.tilecoord
            if tilecoord.z in self.bounds:
                xslice, yslice = self.bounds[tilecoord.z]
                contains_x = xslice.start <= tilecoord.x < xslice.stop
                contains_y = yslice.start <= tilecoord.y < yslice.stop
                if contains_x and contains_y:
                    continue
                if not contains_x:
                    xslice = slice(min(xslice.start, tilecoord.x), max(xslice.stop, tilecoord.x + 1))
                if not contains_y:
                    yslice = slice(min(yslice.start, tilecoord.y), max(yslice.stop, tilecoord.y + 1))
                self.bounds[tilecoord.z] = (xslice, yslice)
            else:
                xslice = slice(tilecoord.x, tilecoord.x + 1)
                yslice = slice(tilecoord.y, tilecoord.y + 1)
                self.bounds[tilecoord.z] = (xslice, yslice)
            yield tile


class FilesystemTileStore(TileStore):

    def __init__(self, tile_layout):
        self.tile_layout = tile_layout

    def delete(self, tiles, remove_empty_directories=True):
        dirnames = set()
        for tile in tiles:
            filename = self.tile_layout.filename(tile.tilecoord)
            if os.path.exists(filename):
                os.remove(filename)
                if remove_empty_directories:
                    dirnames.add(os.path.dirname(filename))
                yield tile
        for dirname in reversed(sorted(dirnames, key=len)):
            try:
                os.rmdir(dirname)
            except OSError:
                pass

    def put(self, tiles):
        for tile in tiles:
            filename = self.tile_layout.filename(tile.tilecoord)
            dirname = os.path.dirname(filename)
            if not os.path.exists(dirname):
                os.makedirs(dirname)
            with open(filename, 'w') as file:
                if hasattr(tile, 'contents'):
                    file.write(tile.contents)
                else:
                    assert False
            yield tile


class LinesTileStore(TileStore):
    """Generates all tile coordinates matching the specified layout from lines"""

    def __init__(self, tile_layout, lines=None):
        self.tile_layout = tile_layout
        self.lines = lines

    def get(self):
        # FIXME warn that this consumes lines
        filename_re = re.compile(self.tile_layout.pattern)
        for line in self.lines:
            match = filename_re.search(line)
            if match:
                yield Tile(self.tile_layout.tilecoord(match.group()), line=line)

    list = get

    def put(self, tiles):
        for tile in tiles:
            logger.info(self.tile_layout.filename(tile.tilecoord))
            yield tile


class BinaryMaskTileStore(TileStore):

    def __init__(self, z, slices, file=None):
        self.z = z
        self.xslice, self.yslice = slices
        self.width = self.xslice.stop - self.xslice.start
        self.height = self.yslice.stop - self.yslice.start
        if file:
            self.image = PIL.Image.open(file)
            assert self.image.mode == '1'
            assert self.image.size == (self.width, self.height)
        else:
            self.image = PIL.Image.new('1', (self.width, self.height))
        self.pixels = self.image.load()

    def delete(self, tiles):
        for tile in tiles:
            if tile.tilecoord.z == self.z:
                x = tile.tilecoord.x - self.xslice.start
                y = self.yslice.stop - tile.tilecoord.y - 1
                if 0 <= x < self.width and 0 <= y < self.height:
                    self.pixels[x, y] = 0
            yield tile

    def get(self):
        for x in xrange(0, self.width):
            for y in xrange(0, self.height):
                if self.pixels[x, y]:
                    yield Tile(TileCoord(self, self.xslice.start + x, self.yslice.start + y))

    list = get

    def put(self, tiles):
        for tile in tiles:
            x = tile.tilecoord.x - self.xslice.start
            y = self.yslice.stop - tile.tilecoord.y - 1
            if 0 <= x < self.width and 0 <= y < self.height:
                self.pixels[x, y] = 1
            yield tile

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

    def __init__(self, bucket_name, tile_layout, bucket=None, dry_run=False, s3connection=None, s3connection_factory=boto.s3.connection.S3Connection):
        TileStore.__init__(self)
        self.dry_run = dry_run
        self.s3bucket = S3Bucket(bucket_name, bucket=bucket, s3connection=s3connection, s3connection_factory=s3connection_factory)
        self.tile_layout = tile_layout

    def delete(self, tiles):
        for tile in tiles:
            key_name = self.tile_layout.filename(tile.tilecoord)
            for bucket in self.s3bucket.boto_is_braindead():
                if not self.dry_run:
                    bucket.delete_key(key_name)
                yield tile

    def get(self, tiles):
        for tile in tiles:
            key_name = self.tile_layout.filename(tile.tilecoord)
            for bucket in self.s3bucket.boto_is_braindead():
                s3key = bucket.new_key(key_name)
                yield Tile(tile.tilecoord, contents=s3key.read(), s3key=s3key)

    def list(self):
        prefix = getattr(self.tile_layout, 'prefix', '')
        marker = ''
        while True:
            for bucket in self.s3bucket.boto_is_braindead():
                s3keys = bucket.get_all_keys(prefix=prefix, marker=marker)
            for s3key in s3keys:
                yield Tile(self.tile_layout.tilecoord(s3key.name), s3key=s3key)
            if s3keys.is_truncated:
                marker = s3key.name
            else:
                break

    def put(self, tiles):
        for tile in tiles:
            key_name = self.tile_layout.filename(tile.tilecoord)
            for bucket in self.s3bucket.boto_is_braindead():
                s3key = bucket.new_key(key_name)
                headers = {}
                if hasattr(tile, 'content_type'):
                    headers['Content-Type'] = tile.content_type
                if hasattr(tile, 'contents'):
                    if not self.dry_run:
                        s3key.set_contents_from_string(tile.contents, headers)
                else:
                    assert False
                yield tile


def convert_format(content_type, **kwargs):
    """Returns a function that converts a tile converted into the desired format"""
    def converter(tile):
        assert hasattr(tile, 'contents')
        if content_type == 'image/jpeg':
            format = 'JPEG'
        elif content_type == 'image/png':
            format = 'PNG'
        else:
            assert False
        string_io = StringIO()
        PIL.Image.open(StringIO(tile.contents)).save(string_io, format, **kwargs)
        return Tile(tile.tilecoord, content_type=content_type, contents=string_io.getvalue())
    return converter
