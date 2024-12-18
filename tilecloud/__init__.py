#!/usr/bin/env python
# pylint: disable=import-outside-toplevel

import builtins
import collections
import logging
import os.path
import re
from builtins import filter as ifilter
from collections.abc import Iterable, Iterator
from functools import reduce
from itertools import islice
from operator import attrgetter
from typing import Any, Optional, Union, cast

logger = logging.getLogger(__name__)


class NotSupportedOperation(Exception):
    pass


def cmp(a: Any, b: Any) -> int:  # pylint: disable=invalid-name
    return cast(bool, a > b) - cast(bool, a < b)


def consume(
    iterator: Iterator[Optional["Tile"]], n: Optional[int] = None  # pylint: disable=invalid-name
) -> None:  # pragma: no cover
    """
    Advance the iterator n-steps ahead.

    If n is none, consume entirely.
    """
    # Use functions that consume iterators at C speed.
    if n is None:
        # feed the entire iterator into a zero-length deque
        collections.deque(iterator, maxlen=0)
    else:
        # advance to the empty slice starting at position n
        next(islice(iterator, n, n), None)


class Bounds:
    """
    Uni-dimensional integer bounds.
    """

    def __init__(self, start: Optional[int] = None, stop: Optional[int] = None) -> None:
        """
        Construct a :class:`Bounds` object.

        Arguments:

            start: Start
            stop: Stop
        """
        self.start = start
        if stop is None:
            self.stop = start + 1 if start is not None else None
        else:
            self.stop = stop

    def __cmp__(self, other: "Bounds") -> int:
        return cmp(self.start, other.start) or cmp(self.stop, other.stop)

    def __lt__(self, other: "Bounds") -> bool:
        return [self.start, self.stop] < [other.start, other.stop]

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Bounds):
            return False
        return [self.start, self.stop] == [other.start, other.stop]

    def __contains__(self, key: int) -> bool:
        """
        Return ``True`` if ``self`` contains ``key``.

        Arguments:

            key: Key
        """
        if self.start is None:
            return False
        assert self.stop is not None
        return self.start <= key < self.stop

    def __len__(self) -> int:
        """
        Return the number of unique elements.
        """
        if self.start is None:
            return 0
        assert self.stop is not None
        return self.stop - self.start

    def __iter__(self) -> Iterator[int]:
        if self.start is not None:
            assert self.stop is not None
            yield from range(self.start, self.stop)

    def __repr__(self) -> str:  # pragma: no cover
        if self.start is None:
            return f"{self.__class__.__name__}(None)"
        return f"{self.__class__.__name__}({self.start}, {self.stop})"

    def add(self, value: int) -> "Bounds":
        """
        Extends self to include value.
        """
        if self.start is None:
            self.start = value
            self.stop = value + 1
        else:
            assert self.stop is not None
            self.start = min(self.start, value)
            self.stop = max(self.stop, value + 1)
        return self

    def update(self, other: "Bounds") -> "Bounds":
        """
        Merges other into self.
        """
        if self.start is None:
            self.start = other.start
            self.stop = other.stop
        else:
            assert self.start is not None
            assert self.stop is not None
            assert other.start is not None
            assert other.stop is not None
            self.start = min(self.start, other.start)
            self.stop = max(self.stop, other.stop)
        return self

    def union(self, other: "Bounds") -> "Bounds":
        """
        Returns a new Bounds which is the union of self and other.
        """
        if self and other:
            assert self.start is not None
            assert self.stop is not None
            assert other.start is not None
            assert other.stop is not None
            return Bounds(min(self.start, other.start), max(self.stop, other.stop))
        if self:
            return Bounds(self.start, self.stop)
        if other:
            return Bounds(other.start, other.stop)
        return Bounds()


class BoundingPyramid:
    def __init__(
        self, bounds: Optional[dict[int, tuple[Bounds, Bounds]]] = None, tilegrid: Optional[Any] = None
    ) -> None:
        self.bounds = bounds or {}
        self.tilegrid = tilegrid
        if self.tilegrid is None:
            from tilecloud.grid.google import GoogleTileGrid

            self.tilegrid = GoogleTileGrid

    def __contains__(self, tilecoord: "TileCoord") -> bool:
        """
        Returns True if tilecoord is in self.
        """
        if tilecoord.z not in self.bounds:
            return False
        xbounds, ybounds = self.bounds[tilecoord.z]
        return tilecoord.x in xbounds and tilecoord.y in ybounds

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, BoundingPyramid):
            return False
        return self.tilegrid == other.tilegrid and self.bounds == other.bounds

    def __iter__(self) -> Iterator["TileCoord"]:
        """
        Generates every TileCoord in self, in increasing z, x, and y order.
        """
        return self.itertopdown()

    def __len__(self) -> int:
        """
        Returns the total number of TileCoords in self.
        """
        return sum(len(xbounds) * len(ybounds) for xbounds, ybounds in self.bounds.values())

    def add(self, tilecoord: "TileCoord") -> "BoundingPyramid":
        """
        Extends self to include tilecoord.
        """
        if tilecoord.z in self.bounds:
            xbounds, ybounds = self.bounds[tilecoord.z]
            xbounds.add(tilecoord.x)
            ybounds.add(tilecoord.y)
        else:
            self.bounds[tilecoord.z] = (Bounds(tilecoord.x), Bounds(tilecoord.y))
        return self

    def add_bounds(self, z: int, bounds: tuple[Bounds, Bounds]) -> None:  # pylint: disable=invalid-name
        if z in self.bounds:
            self.bounds[z][0].update(bounds[0])
            self.bounds[z][1].update(bounds[1])
        else:
            self.bounds[z] = bounds

    def fill(
        self,
        zs: Optional[Iterable[int]] = None,  # pylint: disable=invalid-name
        extent: Optional[tuple[float, float, float, float]] = None,
    ) -> None:
        if zs is None:
            assert self.tilegrid is not None
            zs = self.tilegrid.zs()
        assert self.tilegrid is not None
        if extent is None:
            extent = self.tilegrid.max_extent
        minx, miny, maxx, maxy = extent
        for z in zs:  # pylint: disable=invalid-name
            self.add(self.tilegrid.tilecoord(z, minx, miny))
            self.add(self.tilegrid.tilecoord(z, maxx, maxy))

    def fill_down(self, bottom: int, start: Optional[Any] = None) -> None:
        if start is None:
            start = max(self.bounds)
        assert self.tilegrid is not None
        for z in range(start, bottom):  # pylint: disable=invalid-name
            self.add_bounds(z + 1, self.tilegrid.fill_down(z, self.bounds[z]))

    def fill_up(self, top: int = 0) -> None:
        assert self.tilegrid is not None
        for z in range(max(self.bounds), top, -1):  # pylint: disable=invalid-name
            self.add_bounds(z - 1, self.tilegrid.fill_up(z, self.bounds[z]))

    def iterbottomup(self) -> Iterator["TileCoord"]:
        for z in reversed(sorted(self.bounds.keys())):  # pylint: disable=invalid-name
            yield from self.ziter(z)

    def itertopdown(self) -> Iterator["TileCoord"]:
        for z in sorted(self.bounds.keys()):  # pylint: disable=invalid-name
            yield from self.ziter(z)

    def metatilecoords(self, n: int = 8) -> Iterator["TileCoord"]:  # pylint: disable=invalid-name
        for z in sorted(self.bounds.keys()):  # pylint: disable=invalid-name
            xbounds, ybounds = self.bounds[z]
            assert xbounds.start is not None
            assert xbounds.stop is not None
            assert ybounds.start is not None
            assert ybounds.stop is not None
            metatilecoord = TileCoord(z, xbounds.start, ybounds.start).metatilecoord(n)
            x = metatilecoord.x  # pylint: disable=invalid-name
            while x < xbounds.stop:
                y = metatilecoord.y  # pylint: disable=invalid-name
                while y < ybounds.stop:
                    yield TileCoord(z, x, y, n)
                    y += n  # pylint: disable=invalid-name
                x += n  # pylint: disable=invalid-name

    def zget(self, z: int) -> tuple[Bounds, Bounds]:  # pylint: disable=invalid-name
        """
        Return the tuple (xbounds, ybounds) at level z.
        """
        return self.bounds[z]

    def ziter(self, z: int) -> Iterator["TileCoord"]:  # pylint: disable=invalid-name
        """
        Generates every TileCoord in self at level z.
        """
        if z in self.bounds:
            xbounds, ybounds = self.bounds[z]
            for x in xbounds:  # pylint: disable=invalid-name
                for y in ybounds:  # pylint: disable=invalid-name
                    yield TileCoord(z, x, y)

    def zs(self) -> Iterable[int]:  # pylint: disable=invalid-name
        return self.bounds.keys()

    @classmethod
    def from_string(cls, s: str) -> "BoundingPyramid":  # pylint: disable=invalid-name
        match = re.match(
            r"(?P<z1>\d+)/(?P<x1>\d+)/(?P<y1>\d+):"
            + r"(?:(?P<plusz>\+)?(?P<z2>\d+)/)?"
            + r"(?:(?P<plusx>\+)?(?P<x2>\d+)|(?P<starx>\*))/"
            + r"(?:(?P<plusy>\+)?(?P<y2>\d+)|(?P<stary>\*))\Z",
            s,
        )
        if not match:
            raise ValueError(f"invalid literal for {cls.__name__}.from_string(): {s}")
        z1 = int(match.group("z1"))  # pylint: disable=invalid-name
        x1 = int(match.group("x1"))  # pylint: disable=invalid-name
        if match.group("starx"):
            x2 = 1 << z1  # pylint: disable=invalid-name
        elif match.group("plusx"):
            x2 = x1 + int(match.group("x2"))  # pylint: disable=invalid-name
        else:
            x2 = int(match.group("x2"))  # pylint: disable=invalid-name
        y1 = int(match.group("y1"))  # pylint: disable=invalid-name
        if match.group("stary"):
            y2 = 1 << z1  # pylint: disable=invalid-name
        elif match.group("plusy"):
            y2 = y1 + int(match.group("y2"))  # pylint: disable=invalid-name
        else:
            y2 = int(match.group("y2"))  # pylint: disable=invalid-name
        result = cls({z1: (Bounds(x1, x2), Bounds(y1, y2))})
        if match.group("z2"):
            z2 = int(match.group("z2"))  # pylint: disable=invalid-name
            if match.group("plusz"):
                z2 += z1  # pylint: disable=invalid-name
            if z1 < z2:
                result.fill_down(z2)
            elif z1 > z2:
                result.fill_up(z2)
        return result

    @classmethod
    def full(cls, zmin: Optional[int] = None, zmax: Optional[int] = None) -> "BoundingPyramid":
        assert zmax is not None
        zs = (zmax,) if zmin is None else range(zmin, zmax + 1)  # pylint: disable=invalid-name
        return cls({z: (Bounds(0, 1 << z), Bounds(0, 1 << z)) for z in zs})


class Tile:
    """
    An actual tile with optional metadata.
    """

    def __init__(
        self,
        tilecoord: "TileCoord",
        content_encoding: Optional[Any] = None,
        content_type: Optional[str] = None,
        data: Optional[bytes] = None,
        metadata: Optional[dict[str, str]] = None,
        **kwargs: Any,
    ) -> None:
        """
        Construct a :class:`Tile`.

        Arguments:

            tilecoord: Tile coordinate
            content_encoding: Content encoding
            content_type: Content type
            data: Data
            kwargs: The metadata attributes
        """
        self.tilecoord = tilecoord
        self.content_encoding = content_encoding
        self.content_type = content_type
        self.data = data
        self.error: Optional[Union[Exception, str]] = None
        self.metadata = metadata if metadata is not None else {}
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __cmp__(self, other: "Tile") -> int:
        """
        Compare ``self`` to ``other``.

        Tile comparison is done by comparing their coordinates.
        """
        return cmp(self.tilecoord, other.tilecoord)

    def __lt__(self, other: "Tile") -> bool:
        return self.tilecoord < other.tilecoord

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Tile):
            return False
        return self.tilecoord == other.tilecoord

    def __repr__(self) -> str:  # pragma: no cover
        """
        Return a string representation for debugging.
        """
        keys = sorted(self.__dict__.keys())
        attrs = "".join(f" {key}={self.__dict__[key]}" for key in keys)
        return f"<Tile{attrs}>"

    @property
    def formated_metadata(self) -> str:
        return " ".join([f"{k}={self.metadata[k]}" for k in sorted(self.metadata.keys())])

    @property
    def __dict2__(self) -> dict[str, Any]:
        result = {}
        result.update(self.__dict__)
        result["formated_metadata"] = self.formated_metadata
        return result


class TileCoord:
    """
    A tile coordinate.
    """

    def __init__(self, z: int, x: int, y: int, n: int = 1) -> None:  # pylint: disable=invalid-name
        """
        Construct a TileCoord.

        Attributes:

            z: Zoom level
            x: X coordinate
            y: Y coordinate
            n: Tile size
        """
        self.z = z  # pylint: disable=invalid-name
        self.x = x  # pylint: disable=invalid-name
        self.y = y  # pylint: disable=invalid-name
        self.n = n  # pylint: disable=invalid-name

    def __cmp__(self, other: "TileCoord") -> int:
        """
        Compare ``self`` to ``other``.

        :class:`TileCoord`s are compared in order of their size and ``z``, ``x`` and
        ``y`` coordinates.
        """
        return cmp(self.n, other.n) or cmp(self.z, other.z) or cmp(self.x, other.x) or cmp(self.y, other.y)

    def __lt__(self, other: "TileCoord") -> bool:
        return [self.n, self.z, self.x, self.y] < [other.n, other.z, other.x, other.y]

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TileCoord):
            return False
        return [self.n, self.z, self.x, self.y] == [other.n, other.z, other.x, other.y]

    def __hash__(self) -> int:
        """
        Return a hash value.

        The hash values are unique for all tiles at a given zoom level, but
        tiles from different zoom levels may have equal hash values.
        """
        return ((self.x // self.n) << self.z) ^ (self.y // self.n)

    def __iter__(self) -> Iterator["TileCoord"]:
        """
        Yield each TileCoord.
        """
        for i in range(0, self.n):
            for j in range(0, self.n):
                yield TileCoord(self.z, self.x + i, self.y + j)

    def __repr__(self) -> str:  # pragma: no cover
        """
        Return a string representation for debugging.
        """
        if self.n == 1:
            return f"{self.__class__.__name__}({self.z}, {self.x}, {self.y})"
        return f"{self.__class__.__name__}({self.z}, {self.x}, {self.y}, {self.n})"

    def __str__(self) -> str:
        """
        Return a string representation.
        """
        if self.n == 1:
            return f"{self.z}/{self.x}/{self.y}"
        return f"{self.z}/{self.x}/{self.y}:+{self.n}/+{self.n}"

    def metatilecoord(self, n: int = 8) -> "TileCoord":  # pylint: disable=invalid-name
        return TileCoord(self.z, n * (self.x // n), n * (self.y // n), n)

    def tuple(self) -> tuple[int, int, int, int]:
        return (self.z, self.x, self.y, self.n)

    @classmethod
    def from_string(cls, s: str) -> "TileCoord":  # pylint: disable=invalid-name
        match = re.match(r"(\d+)/(\d+)/(\d+)(?::\+(\d+)/\+\4)?\Z", s)
        if not match:
            raise ValueError(f"invalid literal for {cls.__name__}.from_string: {s}")
        x, y, z, n = match.groups()  # pylint: disable=invalid-name
        return cls(int(x), int(y), int(z), int(n) if n else 1)

    @classmethod
    def from_tuple(cls, tpl: builtins.tuple[int, int, int]) -> "TileCoord":
        return cls(*tpl)


class TileGrid:
    """
    Lays out tiles at multiple zoom levels.
    """

    def __init__(
        self,
        max_extent: Optional[tuple[float, float, float, float]] = None,
        tile_size: Optional[float] = None,
        flip_y: bool = False,
    ) -> None:
        self.max_extent = max_extent or (0.0, 0.0, 1.0, 1.0)
        self.tile_size = tile_size or 256
        self.flip_y = flip_y

    def children(self, tilecoord: TileCoord) -> Iterator[TileCoord]:
        """
        Generates all the children of tilecoord.
        """
        raise NotImplementedError

    def extent(self, tilecoord: TileCoord, border: float = 0) -> tuple[float, float, float, float]:
        """
        Returns the extent of the tile at tilecoord.
        """
        raise NotImplementedError

    def fill_down(
        self, z: int, bounds: tuple[Bounds, Bounds]  # pylint: disable=invalid-name
    ) -> tuple[Bounds, Bounds]:
        raise NotImplementedError

    def fill_up(
        self, z: int, bounds: tuple[Bounds, Bounds]  # pylint: disable=invalid-name
    ) -> tuple[Bounds, Bounds]:
        raise NotImplementedError

    def parent(self, tilecoord: TileCoord) -> Optional[TileCoord]:
        """
        Returns the parent of tilecoord.
        """
        raise NotImplementedError

    def roots(self) -> Iterator[TileCoord]:
        """
        Generates all the root tiles.
        """
        raise NotImplementedError

    def tilecoord(self, z: int, x: float, y: float) -> TileCoord:  # pylint: disable=invalid-name
        """
        Returns the TileCoord for location (x, y) at level z.
        """
        raise NotImplementedError

    def zs(self) -> Iterable[int]:  # pylint: disable=invalid-name
        """
        Generates all zs.
        """
        raise NotImplementedError


class TileLayout:
    """
    Maps tile coordinates to filenames and vice versa.
    """

    def filename(self, tilecoord: TileCoord, metadata: Optional[Any] = None) -> str:
        """
        Return the filename for the given tile coordinate.

        Attributes:

            tilecoord: Tile coordinate
        """
        raise NotImplementedError

    def tilecoord(self, filename: str) -> TileCoord:
        """
        Return the tile coordinate for the given filename.

        Attributes:

            filename: Filename
        """
        raise NotImplementedError


class TileStore:
    """
    A tile store.
    """

    def __init__(
        self,
        bounding_pyramid: Optional[BoundingPyramid] = None,
        content_type: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """
        Construct a :class:`TileStore`.

        Attributes:

            bounding_pyramid: Bounding pyramid
            content_type: Default content type for tiles in this store
            kwargs: Extra attributes
        """
        self.bounding_pyramid = bounding_pyramid
        self.content_type = content_type
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __contains__(self, tile: Tile) -> bool:
        """
        Return true if this store contains ``tile``.

        Attributes:

            tile: Tile
        """
        if tile and self.bounding_pyramid:
            return tile.tilecoord in self.bounding_pyramid
        return False

    def __len__(self) -> int:
        """
        Returns the total number of tiles in the store.
        """
        return reduce(lambda x, _: x + 1, ifilter(None, self.list()), 0)

    def delete(self, tiles: Iterable[Tile]) -> Iterator[Tile]:
        """
        Delete ``tiles`` from the store.

        Attributes:

            tiles: Input tilestream
        """
        return map(self.delete_one, ifilter(None, tiles))

    def delete_one(self, tile: Tile) -> Tile:
        """
        Delete ``tile`` and return ``tile``.

        Attributes:

            tile: Tile
        """
        raise NotImplementedError

    def get(self, tiles: Iterable[Optional[Tile]]) -> Iterator[Optional[Tile]]:
        """
        Add data to each of ``tiles``.

        Attributes:

            tiles: Tilestream
        """
        return map(self.get_one, ifilter(None, tiles))

    def get_all(self) -> Iterator[Optional[Tile]]:
        """
        Generate all the tiles in the store with their data.
        """
        return map(self.get_one, ifilter(None, self.list()))

    def get_bounding_pyramid(self) -> BoundingPyramid:
        """
        Returns the bounding pyramid that encloses all tiles in the store.
        """
        return reduce(
            BoundingPyramid.add, map(attrgetter("tilecoord"), ifilter(None, self.list())), BoundingPyramid()
        )

    def get_cheap_bounding_pyramid(self) -> Optional[BoundingPyramid]:
        """
        Returns a bounding pyramid that is cheap to calculate, or ``None`` if it is not possible to calculate
        a bounding pyramid cheaply.
        """
        return None

    def get_one(self, tile: Tile) -> Optional[Tile]:
        """
        Add data to ``tile``, or return ``None`` if ``tile`` is not in the store.

        Attributes:

            tile: Tile
        """
        raise NotImplementedError

    def list(self) -> Iterable[Tile]:
        """
        Generate all the tiles in the store, but without their data.
        """
        if self.bounding_pyramid is not None:
            for tilecoord in self.bounding_pyramid:
                yield Tile(tilecoord)

    def put(self, tiles: Iterable[Tile]) -> Iterator[Tile]:
        """
        Store ``tiles`` in the store.

        Attributes:

            tiles: Tilestream
        """
        return map(self.put_one, ifilter(None, tiles))

    def put_one(self, tile: Tile) -> Tile:
        """
        Store ``tile`` in the store.

        Attributes:

            tile: Tile
        """
        raise NotImplementedError

    @staticmethod
    def load(name: str, allows_no_contenttype: bool = False) -> "TileStore":  # pragma: no cover
        """
        Construct a :class:`TileStore` from a name.

        Attributes:

            name: Name

        The following shortcuts are available:

        bounds://<bounding-pyramid>

        file://<template>

        http://<template> and https://<template>

        memcached://<server>:<port>/<template>

        s3://<bucket>/<template>

        sqs://<region>/<queue>

        <filename>.bsddb

        <filename>.mbtiles

        <filename>.zip

        <module>
        """
        if name == "null://":
            from tilecloud.store.null import NullTileStore

            return NullTileStore()
        if name.startswith("bounds://"):
            from tilecloud.store.boundingpyramid import BoundingPyramidTileStore

            return BoundingPyramidTileStore(BoundingPyramid.from_string(name[9:]))
        if name.startswith("file://"):
            from tilecloud.layout.template import TemplateTileLayout
            from tilecloud.store.filesystem import FilesystemTileStore

            return FilesystemTileStore(
                TemplateTileLayout(name[7:]),
            )
        if name.startswith("http://") or name.startswith("https://"):
            from tilecloud.layout.template import TemplateTileLayout
            from tilecloud.store.url import URLTileStore

            return URLTileStore((TemplateTileLayout(name),), allows_no_contenttype=allows_no_contenttype)
        if name.startswith("memcached://"):
            from tilecloud.layout.template import TemplateTileLayout
            from tilecloud.lib.memcached import MemcachedClient
            from tilecloud.store.memcached import MemcachedTileStore

            server, template = name[12:].split("/", 1)
            host, port = server.split(":", 1)
            client = MemcachedClient(host, int(port))
            return MemcachedTileStore(client, TemplateTileLayout(template))
        if name.startswith("s3://"):
            from tilecloud.layout.template import TemplateTileLayout
            from tilecloud.store.s3 import S3TileStore

            bucket, template = name[5:].split("/", 1)
            return S3TileStore(bucket, TemplateTileLayout(template))
        if name.startswith("sqs://"):
            import boto.sqs  # pylint: disable=import-error
            from boto.sqs.jsonmessage import JSONMessage  # pylint: disable=import-error

            from tilecloud.store.sqs import SQSTileStore

            region_name, queue_name = name[6:].split("/", 1)
            connection = boto.sqs.connect_to_region(region_name)
            queue = connection.create_queue(queue_name)
            queue.set_message_class(JSONMessage)
            return SQSTileStore(queue)
        if name.startswith("redis://"):
            from tilecloud.store.redis import RedisTileStore

            return RedisTileStore(name)
        _, ext = os.path.splitext(name)
        if ext == ".bsddb":
            import bsddb

            from tilecloud.store.bsddb import BSDDBTileStore

            return BSDDBTileStore(bsddb.hashopen(name))
        if ext == ".mbtiles":
            import sqlite3

            from tilecloud.store.mbtiles import MBTilesTileStore

            return MBTilesTileStore(sqlite3.connect(name))
        if ext == ".zip":
            import zipfile

            from tilecloud.store.zip import ZipTileStore

            return ZipTileStore(zipfile.ZipFile(name, "a"))
        module = __import__(name)
        components = name.split(".")
        module = reduce(getattr, components[1:], module)
        return cast(TileStore, getattr(module, "tilestore"))
