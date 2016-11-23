import logging
import time

from boto.exception import SQSDecodeError, SQSError

from tilecloud import Tile, TileCoord, TileStore


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
        self.on_empty = maybe_stop

    def __contains__(self, tile):
        return False

    @staticmethod
    def get_one(tile):
        return tile

    def list(self):
        while True:
            try:
                sqs_message = self.queue.read()
                if sqs_message is None:
                    try:
                        self.on_empty(self.queue)
                    except StopIteration:
                        break
                else:
                    z = sqs_message.get('z')
                    x = sqs_message.get('x')
                    y = sqs_message.get('y')
                    n = sqs_message.get('n')
                    # FIXME deserialize other attributes
                    tile = Tile(TileCoord(z, x, y, n), sqs_message=sqs_message)
                    yield tile
            except SQSDecodeError as e:
                logger.warning(str(e))
                sqs_message.delete()

    @staticmethod
    def delete_one(tile):
        assert hasattr(tile, 'sqs_message')
        tile.sqs_message.delete()
        delattr(tile, 'sqs_message')
        return tile

    def put_one(self, tile):
        sqs_message = self.queue.new_message()
        sqs_message['z'] = tile.tilecoord.z
        sqs_message['x'] = tile.tilecoord.x
        sqs_message['y'] = tile.tilecoord.y
        sqs_message['n'] = tile.tilecoord.n
        # FIXME serialize other attributes
        try:
            self.queue.write(sqs_message)
            tile.sqs_message = sqs_message
        except SQSError as e:
            tile.error = e
        return tile
