#!/usr/bin/env python

import collections
from itertools import ifilter, imap, islice
import logging
from operator import attrgetter
import os.path
import pyproj
import re


logger = logging.getLogger(__name__)


SPHERICAL_MERCATOR = pyproj.Proj(init='epsg:3857')
SPHERICAL_MERCATOR_ORIGIN = 20037508.34
WGS84 = pyproj.Proj(init='epsg:4326')


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
            return '%s(%r, %r)' % (self.__class__.__name__,
                                   self.start, self.stop)

    def add(self, value):
        if self.start is None:
            self.start = value
            self.stop = value + 1
        else:
            self.start = min(self.start, value)
            self.stop = max(self.stop, value + 1)
        return self

    def update(self, other):
        if self.start is None:
            self.start = other.start
            self.stop = other.stop
        else:
            self.start = min(self.start, other.start)
            self.stop = max(self.stop, other.stop)
        return self

    def union(self, other):
        if self and other:
            return Bounds(min(self.start, other.start),
                          max(self.start, other.start))
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
        return sum(len(xbounds) * len(ybounds)
                   for xbounds, ybounds in self.bounds.itervalues())

    def add(self, tilecoord):
        if tilecoord.z in self.bounds:
            xbounds, ybounds = self.bounds[tilecoord.z]
            xbounds.add(tilecoord.x)
            ybounds.add(tilecoord.y)
        else:
            self.bounds[tilecoord.z] = (Bounds(tilecoord.x),
                                        Bounds(tilecoord.y))
        return self

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

    def zget(self, z):
        return self.bounds[z]

    def ziter(self, z):
        if z in self.bounds:
            xbounds, ybounds = self.bounds[z]
            for x in xbounds:
                for y in ybounds:
                    yield TileCoord(z, x, y)

    def zs(self):
        return self.bounds.keys()

    @classmethod
    def from_wgs84(cls, zmin, zmax, lonmin, lonmax, latmin, latmax):
        bounds = {}
        for z in xrange(zmin, zmax + 1):
            tilecoords = [TileCoord.from_wgs84(z, lon, lat)
                          for lon in (lonmin, lonmax)
                          for lat in (latmin, latmax)]
            xs = [tilecoord.x for tilecoord in tilecoords]
            ys = [tilecoord.y for tilecoord in tilecoords]
            bounds[z] = (Bounds(min(xs), max(x + 1 for x in xs)),
                         Bounds(min(ys), max(y + 1 for y in ys)))
        return cls(bounds)

    @classmethod
    def from_string(cls, s):
        match = re.match(
                r'(?P<z1>\d+)/(?P<x1>\d+)/(?P<y1>\d+):' +
                r'(?:(?P<plusz>\+)?(?P<z2>\d+)/)?' +
                r'(?P<plusx>\+)?(?P<x2>\d+)/(?P<plusy>\+)?(?P<y2>\d+)\Z', s)
        if not match:
            raise ValueError('invalid literal for %s.from_string(): %r' %
                             (cls.__name__, s))
        z1 = int(match.group('z1'))
        x1, x2 = int(match.group('x1')), int(match.group('x2'))
        xbounds = Bounds(x1, x1 + x2 if match.group('plusx') else x2)
        y1, y2 = int(match.group('y1')), int(match.group('y2'))
        ybounds = Bounds(y1, y1 + y2 if match.group('plusy') else y2)
        result = cls({z1: (xbounds, ybounds)})
        if match.group('z2'):
            z2 = int(match.group('z2'))
            if match.group('plusz'):
                z2 += z1
            if z1 < z2:
                result.filldown(z2)
            elif z1 > z2:
                result.fillup(z2)
        return result

    @classmethod
    def full(cls, zmin=None, zmax=None):
        assert zmax is not None
        zs = (zmax,) if zmin is None else xrange(zmin, zmax + 1)
        return cls(dict((z, (Bounds(0, 1 << z), Bounds(0, 1 << z)))
                        for z in zs))


class TileCoord(object):
    """A tile coordinate"""

    def __init__(self, z, x, y):
        self.z = z
        self.x = x
        self.y = y

    def __hash__(self):
        return (self.x << self.z) ^ self.y

    def __repr__(self):
        return '%s(%r, %r, %r)' % (self.__class__.__name__,
                                   self.z, self.x, self.y)

    def __str__(self):
        return '%d/%d/%d' % (self.z, self.x, self.y)

    def normalize(self):
        return (float(self.x) / (1 << self.z), float(self.y) / (1 << self.z))

    def tuple(self):
        return (self.z, self.x, self.y)

    @classmethod
    def from_normalized_coord(cls, z, xy):
        return cls(z, int(xy[0] * (1 << z)), int(xy[1] * (1 << z)))

    @classmethod
    def from_string(cls, s):
        return cls(*map(int, s.split('/')))

    @classmethod
    def from_tuple(cls, tpl):
        return cls(*tpl)

    @classmethod
    def from_wgs84(cls, z, lon, lat):
        if z == 0:
            return cls(0, 0, 0)
        x, y = pyproj.transform(WGS84, SPHERICAL_MERCATOR, lon, lat)
        d = (1 << z - 1) / SPHERICAL_MERCATOR_ORIGIN
        return cls(z,
                   int(d * (x + SPHERICAL_MERCATOR_ORIGIN)),
                   int(d * (SPHERICAL_MERCATOR_ORIGIN - y)))


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
            raise ValueError('invalid literal for %s.tilecoord(): %r' %
                             (self.__class__.__name__, filename))
        return self._tilecoord(match)

    def _tilecoord(self, match):
        raise NotImplementedError


class Tile(object):
    """An actual tile with optional metadata"""

    def __init__(self, tilecoord, content_encoding=None, content_type=None,
                 data=None, **kwargs):
        self.tilecoord = tilecoord
        self.content_encoding = content_encoding
        self.content_type = content_type
        self.data = data
        for key, value in kwargs.items():
            setattr(self, key, value)


class TileStore(object):
    """A tile store"""

    def __init__(self, bounding_pyramid=None, content_type=None, **kwargs):
        self.bounding_pyramid = bounding_pyramid
        self.content_type = content_type
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __contains__(self, tile):
        if self.bounding_pyramid is None:
            return True
        else:
            return tile.tilecoord in self.bounding_pyramid

    def count(self):
        """Returns the total number of tiles in the store"""
        return reduce(lambda x, _: x + 1, ifilter(None, self.list()), 0)

    def delete(self, tiles):
        """A generator that has the side effect of deleting the specified tiles
           from the store"""
        return imap(self.delete_one, ifilter(None, tiles))

    def delete_one(self, tile):
        """A function that deletes tile from the store and returns the tile"""
        raise NotImplementedError

    def get(self, tiles):
        """A generator that returns the specified tiles and their data from the
           store"""
        return imap(self.get_one, ifilter(None, tiles))

    def get_all(self):
        """A generator that returns all the tiles in the store with their
           data"""
        return imap(self.get_one, ifilter(None, self.list()))

    def get_bounding_pyramid(self):
        """Returns the bounding pyramid that encloses all tiles in the store"""
        return reduce(BoundingPyramid.add,
                      imap(attrgetter('tilecoord'),
                           ifilter(None, self.list())),
                      BoundingPyramid())

    def get_cheap_bounding_pyramid(self):
        """Returns a bounding pyramid that is cheap to calculate, or None if it
           is not possible to calculate a bounding pyramid cheaply"""
        return None

    def get_one(self, tile):
        """A function that gets the specified tile and its data from the
           store"""
        raise NotImplementedError

    def list(self):
        """A generator that returns the tiles in the store without necessarily
           retrieving their data"""
        raise NotImplementedError

    def put(self, tiles):
        """A generator that has the side effect of putting the specified tiles
           in the store"""
        return imap(self.put_one, ifilter(None, tiles))

    def put_one(self, tile):
        """A function that puts tile in the store and returns the tile"""
        raise NotImplementedError

    @classmethod
    def load(cls, name):
        root, ext = os.path.splitext(name)
        if ext == '.bsddb':
            import bsddb
            from tilecloud.store.bsddb import BSDDBTileStore
            return BSDDBTileStore(bsddb.hashopen(name))
        if ext == '.mbtiles':
            import sqlite3
            from tilecloud.store.mbtiles import MBTilesTileStore
            return MBTilesTileStore(sqlite3.connect(name))
        if ext == '.zip':
            import zipfile
            from tilecloud.store.zip import ZipTileStore
            return ZipTileStore(zipfile.ZipFile(name, 'a'))
        module = __import__(name)
        components = name.split('.')
        module = reduce(lambda module, attr: getattr(module, attr),
                        components[1:],
                        module)
        return getattr(module, 'tile_store')
