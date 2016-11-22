import math
import socket
import time


class Statistics(object):

    def __init__(self, format='%f'):
        self.format = format
        self.n = 0
        self.sum = 0.0
        self.sum_of_squares = 0.0
        self.minimum = None
        self.maximum = None

    def add(self, x):
        self.n += 1
        self.sum += x
        self.sum_of_squares += x * x
        self.minimum = x if self.minimum is None else min(self.minimum, x)
        self.maximum = x if self.maximum is None else max(self.maximum, x)

    def __str__(self):
        result = []
        if self.n:
            result.append('/'.join(self.format % value for value in (self.minimum, self.mean, self.maximum)))
        result.append('(n={0:d})'.format(self.n))
        return ' '.join(result)

    @property
    def mean(self):
        return self.sum / self.n if self.n else None

    @property
    def variance(self):
        return self.sum_of_squares / self.n - (self.sum / self.n) ** 2

    @property
    def standard_deviation(self):
        return math.sqrt(self.variance)


class Statsd(object):

    def __init__(self, prefix='tilecloud.', host='127.0.0.1', port=8125):
        self.prefix = prefix
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def send(self, message):
        self.socket.sendto(self.prefix + message, (self.host, self.port))


class Benchmark(object):

    def __init__(self, attr='benchmark', statsd=None):
        self.attr = attr
        self.statsd = statsd
        self.statisticss = {}

    def sample(self, key=None):
        if key:
            if key in self.statisticss:
                statistics = self.statisticss[key]
            else:
                statistics = Statistics('%.3fs')
                self.statisticss[key] = statistics
        else:
            statistics = None

        def callback(tile):
            if tile:
                if hasattr(tile, self.attr):
                    times = getattr(tile, self.attr)
                    times.append(time.time())
                    delta_t = times[-1] - times[-2]
                    if statistics:
                        statistics.add(delta_t)
                    if self.statsd:
                        self.statsd.send('{0!s}:{1:.3f}|ms'.format(key, delta_t))
                else:
                    setattr(tile, self.attr, [time.time()])
            return tile
        return callback


class StatsdCountTiles(object):

    def __init__(self, statsd):
        self.statsd = statsd

    def __call__(self, tile):
        if tile:
            self.statsd.send('tiles:1|c')
        return tile


class StatsdCountErrors(object):

    def __init__(self, statsd):
        self.statsd = statsd

    def __call__(self, tile):
        if tile and tile.error:
            self.statsd.send('errors:1|c')
        return tile
