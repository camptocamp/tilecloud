import boto3
import botocore.config
import botocore.exceptions
import logging

from tilecloud import Tile, TileStore

logger = logging.getLogger(__name__)
CLIENT_TIMEOUT = 60


class S3TileStore(TileStore):
    """Tiles stored in Amazon S3"""

    def __init__(self, bucket, tilelayout, dry_run=False, s3_host=None, **kwargs):
        self.client = get_client(s3_host)
        self.bucket = bucket
        self.tilelayout = tilelayout
        self.dry_run = dry_run
        TileStore.__init__(self, **kwargs)

    def __contains__(self, tile):
        if not tile:
            return False
        key_name = self.tilelayout.filename(tile.tilecoord)
        try:
            self.client.head_object(Bucket=self.bucket, Key=key_name)
            return True
        except botocore.exceptions.ClientError as exc:
            if _get_status(exc) == 404:
                return False
            else:
                raise

    def delete_one(self, tile):
        try:
            key_name = self.tilelayout.filename(tile.tilecoord)
            if not self.dry_run:
                self.client.delete_object(Bucket=self.bucket, Key=key_name)
        except botocore.exceptions.ClientError as exc:
            tile.error = exc
        return tile

    def get_one(self, tile):
        key_name = self.tilelayout.filename(tile.tilecoord)
        try:
            response = self.client.get_object(Bucket=self.bucket, Key=key_name)
            tile.data = response['Body'].read()
            tile.content_encoding = response.get('ContentEncoding')
            tile.content_type = response.get('ContentType')
        except botocore.exceptions.ClientError as exc:
            if _get_status(exc) == 404:
                return None
            else:
                tile.error = exc
        return tile

    def list(self):
        prefix = getattr(self.tilelayout, 'prefix', '')
        for s3_key in self.client.list_objects(Bucket=self.bucket, Prefix=prefix):
            try:
                tilecoord = self.tilelayout.tilecoord(s3_key['Key'])
            except ValueError:
                continue
            yield Tile(tilecoord)

    def put_one(self, tile):
        assert tile.data is not None
        key_name = self.tilelayout.filename(tile.tilecoord)
        args = {}
        if tile.content_encoding is not None:
            args['ContentEncoding'] = tile.content_encoding
        if tile.content_type is not None:
            args['ContentType'] = tile.content_type
        if not self.dry_run:
            try:
                self.client.put_object(ACL='public-read', Body=tile.data, Key=key_name, Bucket=self.bucket,
                                       **args)
            except botocore.exceptions.ClientError as exc:
                tile.error = exc
        return tile


def _get_status(s3_client_exception):
    return int(s3_client_exception.response['Error']['Code'])


def get_client(s3_host):
    config = botocore.config.Config(connect_timeout=CLIENT_TIMEOUT, read_timeout=CLIENT_TIMEOUT)
    session = boto3.session.Session()
    return session.client('s3', endpoint_url=('https://%s/' % s3_host) if s3_host is not None else None,
                          config=config)
