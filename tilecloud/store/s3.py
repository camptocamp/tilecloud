import logging
from ssl import SSLError

import boto.s3.connection
import boto.exception

from tilecloud import Tile, TileStore



logger = logging.getLogger(__name__)



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
            try:
                return Tile(tile.tilecoord, data=s3key.read(), s3key=s3key)
            except boto.exception.S3ResponseError as exc:
                if exc.status == 404:
                    return None
                else:
                    raise

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

