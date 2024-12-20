import logging
import os
from collections.abc import Iterator
from typing import Any, Optional

from azure.core.exceptions import ResourceNotFoundError
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient, ContainerClient, ContentSettings

from tilecloud import Tile, TileLayout, TileStore

_LOGGER = logging.getLogger(__name__)


class AzureStorageBlobTileStore(TileStore):
    """
    Tiles stored in Azure storage blob.
    """

    def __init__(
        self,
        tilelayout: TileLayout,
        container: Optional[str] = None,
        dry_run: bool = False,
        cache_control: Optional[str] = None,
        container_client: Optional[ContainerClient] = None,
        **kwargs: Any,
    ):
        if container_client is None:
            if "AZURE_STORAGE_CONNECTION_STRING" in os.environ:
                assert container is not None
                self.container_client = BlobServiceClient.from_connection_string(
                    os.environ["AZURE_STORAGE_CONNECTION_STRING"]
                ).get_container_client(container=container)
            elif "AZURE_STORAGE_BLOB_CONTAINER_URL" in os.environ:
                self.container_client = ContainerClient.from_container_url(
                    os.environ["AZURE_STORAGE_BLOB_CONTAINER_URL"]
                )
                if os.environ.get("AZURE_STORAGE_BLOB_VALIDATE_CONTAINER_NAME", "false").lower() == "true":
                    assert container == self.container_client.container_name
            else:
                assert container is not None
                self.container_client = BlobServiceClient(
                    account_url=os.environ["AZURE_STORAGE_ACCOUNT_URL"],
                    credential=DefaultAzureCredential(),
                ).get_container_client(container=container)
        else:
            self.container_client = container_client

        self.tilelayout = tilelayout
        self.dry_run = dry_run
        self.cache_control = cache_control
        TileStore.__init__(self, **kwargs)

    def __contains__(self, tile: Tile) -> bool:
        if not tile:
            return False
        key_name = self.tilelayout.filename(tile.tilecoord, tile.metadata)
        blob = self.container_client.get_blob_client(blob=key_name)
        return blob.exists()

    def delete_one(self, tile: Tile) -> Tile:
        try:
            key_name = self.tilelayout.filename(tile.tilecoord, tile.metadata)
            if not self.dry_run:
                blob = self.container_client.get_blob_client(blob=key_name)
                if blob.exists():
                    blob.delete_blob()
        except Exception as exc:  # pylint: disable=broad-except
            _LOGGER.warning("Failed to delete tile %s", tile.tilecoord, exc_info=exc)
            tile.error = exc
        return tile

    def get_one(self, tile: Tile) -> Optional[Tile]:
        key_name = self.tilelayout.filename(tile.tilecoord, tile.metadata)
        try:
            blob = self.container_client.get_blob_client(blob=key_name)
            if not blob.exists():
                return None
            data = blob.download_blob().readall()
            assert isinstance(data, bytes) or data is None
            tile.data = data
            properties = blob.get_blob_properties()
            tile.content_encoding = properties.content_settings.content_encoding
            tile.content_type = properties.content_settings.content_type
        except Exception as exc:  # pylint: disable=broad-except
            _LOGGER.warning("Failed to get tile %s", tile.tilecoord, exc_info=exc)
            tile.error = exc
        return tile

    def list(self) -> Iterator[Tile]:
        prefix = getattr(self.tilelayout, "prefix", "")

        for blob in self.container_client.list_blobs(name_starts_with=prefix):
            try:
                assert isinstance(blob.name, str)
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
                    content_settings=ContentSettings(  # type: ignore
                        content_type=tile.content_type,
                        content_encoding=tile.content_encoding,
                        cache_control=self.cache_control,
                    ),
                )
            except Exception as exc:  # pylint: disable=broad-except
                _LOGGER.warning("Failed to put tile %s", tile.tilecoord, exc_info=exc)
                tile.error = exc

        return tile
