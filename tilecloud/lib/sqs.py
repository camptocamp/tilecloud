from tilecloud import Tile, TileCoord


def raise_IndexError():
    raise IndexError


class SQSDeque(object):
    """Provides a deque-like interface to an Amazon SQS queue of tiles"""

    def __init__(self, queue, on_empty=raise_IndexError, visibility_timeout=None):
        self.queue = queue
        self.on_empty = on_empty
        self.visibility_timeout = visibility_timeout

    def append(self, tile):
        sqs_message = self.queue.new_message()
        sqs_message['z'] = tile.tilecoord.z
        sqs_message['x'] = tile.tilecoord.x
        sqs_message['y'] = tile.tilecoord.y
        self.queue.write(sqs_message)

    def popleft(self):
        sqs_message = self.queue.read(self.visibility_timeout)
        if sqs_message is None:
            return self.on_empty()
        z = sqs_message.get('z')
        x = sqs_message.get('x')
        y = sqs_message.get('y')
        return Tile(TileCoord(z, x, y), sqs_message=sqs_message)
