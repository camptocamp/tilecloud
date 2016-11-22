import re
import socket


class MemcachedError(RuntimeError):
    pass


class MemcachedClient(object):

    VALUE_RE = re.compile(r'VALUE\s+(?P<key>\S+)\s+(?P<flags>\d+)\s+(?P<bytes>\d+)(?:\s+(?P<cas>\d+))?\Z')

    def __init__(self, host='localhost', port=11211):
        self.socket = socket.create_connection((host, port))
        self.buffer = ''

    def delete(self, key):
        self.writeline('delete {0!s}'.format(key))
        line = self.readline()
        if line == 'DELETED':
            return True
        elif line == 'NOT_FOUND':
            return False
        else:
            raise MemcachedError(line)

    def get(self, key):
        self.writeline('get {0!s}'.format(key))
        line = self.readline()
        if line == 'END':
            return None, None, None
        m = self.VALUE_RE.match(line)
        if not m:
            raise MemcachedError(line)
        assert m.group('key') == key
        flags = int(m.group('flags'))
        value = self.readvalue(int(m.group('bytes')))
        cas = None if m.group('cas') is None else int(m.group('cas'))
        line = self.readline()
        if line != 'END':
            raise MemcachedError(line)
        return flags, value, cas

    def set(self, key, flags, exptime, value):
        self.writeline('set {0!s} {1:d} {2:d} {3:d}'.format(key, flags, exptime, len(value)))
        self.writeline(value)
        line = self.readline()
        if line != 'STORED':
            raise MemcachedError(line)

    def readvalue(self, n):
        while len(self.buffer) < n + 2:
            self.buffer += self.socket.recv(n + 2 - len(self.buffer))
        if self.buffer[n:n + 2] != '\r\n':
            raise MemcachedError
        result = self.buffer[:n]
        self.buffer = self.buffer[n + 2:]
        return result

    def readline(self):
        while True:
            index = self.buffer.find('\r\n')
            if index == -1:
                self.buffer += self.socket.recv(1024)
            else:
                line = self.buffer[:index]
                self.buffer = self.buffer[index + 2:]
                return line

    def writeline(self, line):
        self.socket.send(line + '\r\n')
