import logging
import os
from typing import Any, Iterator, Optional

from azure.storage.blob import BlobServiceClient

from tilecloud import Tile, TileLayout, TileStore

LOGGER = logging.getLogger(__name__)


class AzureStorageBlobTileStore(TileStore):
    """Tiles stored in Azure storge blob"""

    def __init__(
        self,
        container: str,
        tilelayout: TileLayout,
        dry_run: bool = False,
        cache_control: Optional[str] = None,
        **kwargs: Any,
    ):
        self.client = BlobServiceClient.from_connection_string(os.getenv("AZURE_STORAGE_CONNECTION_STRING"))
        self.container_name = container
        try:
            self.container_client = self.client.create_container(container)
        except Exception as e:
            LOGGER.info(e)
        self.tilelayout = tilelayout
        self.dry_run = dry_run
        self.cache_control = cache_control
        TileStore.__init__(self, **kwargs)

    def __contains__(self, tile: Tile) -> bool:
        if not tile:
            return False
        key_name = self.tilelayout.filename(tile.tilecoord, tile.metadata)
        return len(self.container_client.list_blobs(name_starts_with=key_name)) > 0

    def delete_one(self, tile: Tile) -> Tile:
        try:
            key_name = self.tilelayout.filename(tile.tilecoord, tile.metadata)
            if not self.dry_run:
                blob = self.client.get_blob_client(container=self.container_name, blob=key_name)
                blob.delete_blob()
        except Exception as exc:
            tile.error = exc
        return tile

    def get_one(self, tile: Tile) -> Optional[Tile]:
        key_name = self.tilelayout.filename(tile.tilecoord, tile.metadata)
        try:
            blob = self.client.get_blob_client(container=self.container_name, blob=key_name)
            tile.data = blob.download_blob().readall()
            tile.content_encoding = blob.Metadata.FirstOrDefault("ContentEncoding", None)
            tile.content_type = blob.Metadata.FirstOrDefault("ContentType", None)
        except Exception as exc:
            tile.error = exc
        return tile

    def list(self) -> Iterator[Tile]:
        prefix = getattr(self.tilelayout, "prefix", "")

        for blob in self.container_client.list_blobs(name_starts_with=prefix):
            try:
                tilecoord = self.tilelayout.tilecoord(blob.name)
            except ValueError:
                continue
            yield Tile(tilecoord)

    def put_one(self, tile: Tile) -> Tile:
        assert tile.data is not None
        key_name = self.tilelayout.filename(tile.tilecoord, tile.metadata)
        if not self.dry_run:
            try:
                blob = self.client.get_blob_client(container=self.container_name, blob=key_name)
                blob.upload_blob(tile.data)
                if tile.content_encoding is not None:
                    blob.Metadata.Add("ContentEncoding", tile.content_encoding)
                if tile.content_type is not None:
                    blob.Metadata.Add("ContentType", tile.content_type)
                if self.cache_control is not None:
                    blob.Metadata.Add("CacheControl", tile.cache_control)  # type: ignore
            except Exception as exc:
                tile.error = exc

        return tile
