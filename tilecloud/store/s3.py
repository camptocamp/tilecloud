import httplib
import logging

from tilecloud import Tile, TileStore
from tilecloud.lib.s3 import S3Connection, S3Error


logger = logging.getLogger(__name__)


class S3TileStore(TileStore):
    """Tiles stored in Amazon S3"""

    def __init__(self, bucket, tile_layout, dry_run=False, **kwargs):
        self.s3bucket = S3Connection().bucket(bucket)
        self.tile_layout = tile_layout
        self.dry_run = dry_run
        TileStore.__init__(self, **kwargs)

    def __contains__(self, tile):
        if not tile:
            return False
        key_name = self.tile_layout.filename(tile.tilecoord)
        try:
            self.s3bucket.get(key_name)  # FIXME should use head
            return True
        except S3Error as exc:
            if exc.response.status == httplib.NOT_FOUND:
                return False
            else:
                raise

    def delete_one(self, tile):
        try:
            key_name = self.tile_layout.filename(tile.tilecoord)
            if not self.dry_run:
                self.s3bucket.delete(key_name)
        except S3Error as exc:
            tile.error = exc
        return tile

    def get_one(self, tile):
        key_name = self.tile_layout.filename(tile.tilecoord)
        try:
            tile.s3key = self.s3bucket.get(key_name)
            tile.data = tile.s3key.body
            if 'Content-Encoding' in tile.s3key:
                tile.content_encoding = tile.s3key['Content-Encoding']
            else:
                tile.content_encoding = None
            if 'Content-Type' in tile.s3key:
                tile.content_type = tile.s3key['Content-Type']
            else:
                tile.content_type = None
        except S3Error as exc:
            if exc.response.status == httplib.NOT_FOUND:
                return None
            else:
                tile.error = exc
        return tile

    def list(self):
        prefix = getattr(self.tile_layout, 'prefix', '')
        for s3key in self.s3bucket.list_objects(prefix=prefix):
            try:
                tilecoord = self.tile_layout.tilecoord(s3key.name)
            except ValueError:
                continue
            yield Tile(tilecoord, s3key=s3key)

    def put_one(self, tile):
        assert tile.data is not None
        key_name = self.tile_layout.filename(tile.tilecoord)
        s3key = self.s3bucket.key(key_name)
        s3key.body = tile.data
        if tile.content_encoding is not None:
            s3key['Content-Encoding'] = tile.content_encoding
        if tile.content_type is not None:
            s3key['Content-Type'] = tile.content_type
        if not self.dry_run:
            try:
                s3key.put()
            except S3Error as exc:
                tile.error = exc
        return tile
