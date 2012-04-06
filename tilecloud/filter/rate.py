import time


class RateLimit(object):

    def __init__(self, rate):
        self.rate = rate
        self.count = 0
        self.start = None

    def __call__(self, tile):
        if tile:
            if self.start is None:
                self.start = time.time()
            else:
                self.count += 1
                seconds = self.start + self.count / self.rate - time.time()
                if seconds > 0:
                    time.sleep(seconds)
        return tile
