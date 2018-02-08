import base64
import json
import logging
import time

from tilecloud import Tile, TileCoord, TileStore


BATCH_SIZE = 10  # max Amazon allows
logger = logging.getLogger(__name__)


def maybe_stop(queue):
    attributes = queue.get_attributes()
    if int(attributes['ApproximateNumberOfMessages']) == 0:
        if int(attributes['ApproximateNumberOfMessagesNotVisible']) == 0:
            raise StopIteration
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
            sqs_messages = self.queue.receive_messages(MaxNumberOfMessages=BATCH_SIZE)
            if not sqs_messages:
                try:
                    self.on_empty(self.queue)
                except StopIteration:
                    break
            else:
                for sqs_message in sqs_messages:
                    try:
                        body = json.loads(base64.b64decode(sqs_message.body.encode('utf-8')).decode('utf-8'))
                        z = body.get('z')
                        x = body.get('x')
                        y = body.get('y')
                        n = body.get('n')
                        metadata = body.get('metadata', {})
                        # FIXME deserialize other attributes
                        tile = Tile(TileCoord(z, x, y, n), sqs_message=sqs_message, metadata=metadata)
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
        sqs_message = _create_message(tile)

        try:
            self.queue.send_message(MessageBody=sqs_message)
        except Exception as e:
            logger.warning('Failed sending SQS message', exc_info=True)
            tile.error = e
        return tile

    def put(self, tiles):
        buffered_tiles = []
        for tile in tiles:
            buffered_tiles.append(tile)
            if len(buffered_tiles) >= BATCH_SIZE:
                self._send_buffer(buffered_tiles)
                buffered_tiles = []
        if len(buffered_tiles) > 0:
            self._send_buffer(buffered_tiles)

    def _send_buffer(self, tiles):
        try:
            messages = [{
                'Id': str(i),
                'MessageBody': _create_message(tile)
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


def _create_message(tile):
    sqs_message = {
        'z': tile.tilecoord.z,
        'x': tile.tilecoord.x,
        'y': tile.tilecoord.y,
        'n': tile.tilecoord.n,
        'metadata': tile.metadata
    }
    if 'sqs_message' in sqs_message['metadata']:
        del sqs_message['metadata']['sqs_message']

    # FIXME serialize other attributes
    return base64.b64encode(json.dumps(sqs_message).encode('utf-8')).decode('utf-8')
