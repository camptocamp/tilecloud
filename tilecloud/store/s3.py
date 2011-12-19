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

    def delete_one(self, tile):
        key_name = self.tile_layout.filename(tile.tilecoord)
        if not self.dry_run:
            self.s3bucket.delete(key_name)
        return tile

    def get_one(self, tile):
        key_name = self.tile_layout.filename(tile.tilecoord)
        try:
            s3key = self.s3bucket.get(key_name)
            tile.data = s3key.body
            if 'Content-Encoding' in s3key:
                tile.content_encoding = s3key['Content-Encoding']
            else:
                tile.content_encoding = None
            if 'Content-Type' in s3key:
                tile.content_type = s3key['Content-Type']
            else:
                tile.content_type = None
            return tile
        except S3Error as exc:
            if exc.response.status == 404:
                return None
            else:
                raise

    def list(self):
        prefix = getattr(self.tile_layout, 'prefix', '')
        for s3key in self.s3bucket.list_objects(prefix=prefix):
            yield Tile(self.tile_layout.tilecoord(s3key.name), s3key=s3key)

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
            s3key.put()
        return tile
