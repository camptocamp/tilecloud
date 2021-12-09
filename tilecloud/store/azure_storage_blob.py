import logging
import os
from typing import Any, Iterator, Optional

from azure.core.exceptions import ResourceNotFoundError
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient, ContentSettings

from tilecloud import Tile, TileLayout, TileStore

LOGGER = logging.getLogger(__name__)


class AzureStorageBlobTileStore(TileStore):
    """
    Tiles stored in Azure storage blob.
    """

    def __init__(
        self,
        container: str,
        tilelayout: TileLayout,
        dry_run: bool = False,
        cache_control: Optional[str] = None,
        client: Optional[BlobServiceClient] = None,
        **kwargs: Any,
    ):
        if client is None:
            if "AZURE_STORAGE_CONNECTION_STRING" in os.environ:
                client = BlobServiceClient.from_connection_string(
                    os.environ.get("AZURE_STORAGE_CONNECTION_STRING")
                )
            else:
                client = BlobServiceClient(
                    account_url=os.environ["AZURE_STORAGE_ACCOUNT_URL"],
                    credential=DefaultAzureCredential(),
                )

        self.container_client = client.get_container_client(container=container)
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
                blob = self.container_client.get_blob_client(blob=key_name)
                blob.delete_blob()
        except Exception as exc:
            tile.error = exc
        return tile

    def get_one(self, tile: Tile) -> Optional[Tile]:
        key_name = self.tilelayout.filename(tile.tilecoord, tile.metadata)
        try:
            blob = self.container_client.get_blob_client(blob=key_name)
            tile.data = blob.download_blob().readall()
            properties = blob.get_blob_properties()
            tile.content_encoding = properties.content_settings.content_encoding
            tile.content_type = properties.content_settings.content_type
        except ResourceNotFoundError:
            return None
        except Exception as exc:
            LOGGER.exception(exc)
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
                blob = self.container_client.get_blob_client(blob=key_name)
                blob.upload_blob(
                    tile.data,
                    overwrite=True,
                    content_settings=ContentSettings(
                        content_type=tile.content_type,
                        content_encoding=tile.content_encoding,
                        cache_control=self.cache_control,
                    ),
                )
            except Exception as exc:
                tile.error = exc

        return tile
