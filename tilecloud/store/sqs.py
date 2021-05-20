import logging
import time
from typing import Any, Callable, Dict, Iterable, Iterator, List

import botocore.client
import botocore.exceptions

from tilecloud import Tile, TileStore
from tilecloud.store.queue import decode_message, encode_message

BATCH_SIZE = 10  # max Amazon allows
logger = logging.getLogger(__name__)


def maybe_stop(queue: "botocore.client.SQS") -> bool:
    try:
        queue.load()
    except botocore.exceptions.EndpointConnectionError:
        logger.warning("Error fetching SQS attributes", exc_info=True)
        return True

    attributes = queue.attributes
    if int(attributes["ApproximateNumberOfMessages"]) == 0:
        if int(attributes["ApproximateNumberOfMessagesNotVisible"]) == 0:
            return True
        else:
            time.sleep(int(attributes["VisibilityTimeout"]) / 4.0)
    return False


class SQSTileStore(TileStore):
    def __init__(
        self,
        queue: "botocore.client.SQS",
        on_empty: Callable[["botocore.client.SQS"], bool] = maybe_stop,
        **kwargs: Any,
    ):
        TileStore.__init__(self, **kwargs)
        self.queue = queue
        self.on_empty = on_empty

    def __contains__(self, tile: Tile) -> bool:
        return False

    @staticmethod
    def get_one(tile: Tile) -> Tile:
        return tile

    def list(self) -> Iterator[Tile]:
        while True:
            try:
                sqs_messages = self.queue.receive_messages(MaxNumberOfMessages=BATCH_SIZE)
            except botocore.exceptions.EndpointConnectionError:
                logger.warning("Error fetching SQS messages", exc_info=True)
                sqs_messages = []

            if not sqs_messages:
                if self.on_empty(self.queue):
                    break
            else:
                for sqs_message in sqs_messages:
                    try:
                        tile = decode_message(sqs_message.body.encode("utf-8"), sqs_message=sqs_message)
                        yield tile
                    except Exception:
                        logger.warning("Failed decoding the SQS message", exc_info=True)
                        sqs_message.delete()

    def delete_one(self, tile: Tile) -> Tile:
        assert hasattr(tile, "sqs_message")
        tile.sqs_message.delete()  # type: ignore
        delattr(tile, "sqs_message")
        return tile

    def put_one(self, tile: Tile) -> Tile:
        sqs_message = encode_message(tile)

        try:
            self.queue.send_message(MessageBody=sqs_message)
        except Exception as e:
            logger.warning("Failed sending SQS message", exc_info=True)
            tile.error = e
        return tile

    def put(self, tiles: Iterable[Tile]) -> Iterator[Tile]:
        buffered_tiles = []
        try:
            for tile in tiles:
                buffered_tiles.append(tile)
                if len(buffered_tiles) >= BATCH_SIZE:
                    self._send_buffer(buffered_tiles)
                    buffered_tiles = []
                yield tile
        finally:
            if len(buffered_tiles) > 0:
                self._send_buffer(buffered_tiles)

    def _send_buffer(self, tiles: List[Tile]) -> None:
        try:
            messages: List[Dict[str, Any]] = [
                {"Id": str(i), "MessageBody": encode_message(tile)} for i, tile in enumerate(tiles)
            ]
            response = self.queue.send_messages(Entries=messages)
            for failed in response.get("Failed", []):
                logger.warning("Failed sending SQS message: %s", failed["Message"])
                pos = int(failed["Id"])
                tiles[pos].error = failed["Message"]
        except Exception as e:
            logger.warning("Failed sending SQS messages", exc_info=True)
            for tile in tiles:
                tile.error = e

    def get_status(self) -> Dict[str, str]:
        """
        Returns a map of stats
        """
        self.queue.load()
        attributes = dict(self.queue.attributes)
        return {
            "Approximate number of tiles to generate": attributes["ApproximateNumberOfMessages"],
            "Approximate number of generating tiles": attributes["ApproximateNumberOfMessagesNotVisible"],
            "Delay in seconds": attributes["DelaySeconds"],
            "Receive message wait time in seconds": attributes["ReceiveMessageWaitTimeSeconds"],
            "Visibility timeout in seconds": attributes["VisibilityTimeout"],
            "Queue creation date": time.ctime(int(attributes["CreatedTimestamp"])),
            "Last modification in tile queue": time.ctime(int(attributes["LastModifiedTimestamp"])),
        }
