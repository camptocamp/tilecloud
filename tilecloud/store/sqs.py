import botocore.exceptions
import logging
import time

from tilecloud import TileStore
from tilecloud.store.queue import encode_message, decode_message

BATCH_SIZE = 10  # max Amazon allows
logger = logging.getLogger(__name__)


def maybe_stop(queue):
    try:
        queue.load()
    except botocore.exceptions.EndpointConnectionError:
        logger.warning("Error fetching SQS attributes", exc_info=True)
        raise StopIteration()

    attributes = queue.attributes
    if int(attributes['ApproximateNumberOfMessages']) == 0:
        if int(attributes['ApproximateNumberOfMessagesNotVisible']) == 0:
            raise StopIteration()
        else:
            time.sleep(int(attributes['VisibilityTimeout']) / 4.0)


class SQSTileStore(TileStore):

    def __init__(self, queue, on_empty=maybe_stop, **kwargs):
        TileStore.__init__(self, **kwargs)
        self.queue = queue
        self.on_empty = on_empty

    def __contains__(self, tile):
        return False

    @staticmethod
    def get_one(tile):
        return tile

    def list(self):
        while True:
            try:
                sqs_messages = self.queue.receive_messages(MaxNumberOfMessages=BATCH_SIZE)
            except botocore.exceptions.EndpointConnectionError:
                logger.warning("Error fetching SQS messages", exc_info=True)
                sqs_messages = []

            if not sqs_messages:
                try:
                    self.on_empty(self.queue)
                except StopIteration:
                    break
            else:
                for sqs_message in sqs_messages:
                    try:
                        tile = decode_message(sqs_message.body.encode('utf-8'), sqs_message=sqs_message)
                        yield tile
                    except Exception:
                        logger.warning('Failed decoding the SQS message', exc_info=True)
                        sqs_message.delete()

    @staticmethod
    def delete_one(tile):
        assert hasattr(tile, 'sqs_message')
        tile.sqs_message.delete()
        delattr(tile, 'sqs_message')
        return tile

    def put_one(self, tile):
        sqs_message = encode_message(tile)

        try:
            self.queue.send_message(MessageBody=sqs_message)
        except Exception as e:
            logger.warning('Failed sending SQS message', exc_info=True)
            tile.error = e
        return tile

    def put(self, tiles):
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

    def _send_buffer(self, tiles):
        try:
            messages = [{
                'Id': str(i),
                'MessageBody': encode_message(tile)
            } for i, tile in enumerate(tiles)]
            response = self.queue.send_messages(Entries=messages)
            for failed in response.get('Failed', []):
                logger.warning('Failed sending SQS message: %s', failed['Message'])
                pos = int(failed['Id'])
                tiles[pos].error = failed['Message']
        except Exception as e:
            logger.warning('Failed sending SQS messages', exc_info=True)
            for tile in tiles:
                tile.error = e
