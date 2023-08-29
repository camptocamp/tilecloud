import re
import socket
from typing import Optional


class MemcachedError(RuntimeError):
    pass


class MemcachedClient:
    VALUE_RE = re.compile(rb"VALUE\s+(?P<key>\S+)\s+(?P<flags>\d+)\s+(?P<bytes>\d+)(?:\s+(?P<cas>\d+))?\Z")

    def __init__(self, host: str = "localhost", port: int = 11211):
        self.socket = socket.create_connection((host, port))
        self.buffer = b""

    def delete(self, key: str) -> bool:
        self.writeline(f"delete {key}".encode())
        line = self.readline()
        if line == b"DELETED":
            return True
        if line == b"NOT_FOUND":
            return False
        raise MemcachedError(line)

    def get(self, key: str) -> tuple[Optional[int], Optional[bytes], Optional[int]]:
        self.writeline(f"get {key}".encode())
        line = self.readline()
        if line == b"END":
            return None, None, None
        match = self.VALUE_RE.match(line)
        if not match:
            raise MemcachedError(line)
        assert match.group("key") == key.encode()
        flags = int(match.group("flags"))
        value = self.readvalue(int(match.group("bytes")))
        cas = None if match.group("cas") is None else int(match.group("cas"))
        line = self.readline()
        if line != b"END":
            raise MemcachedError(line)
        return flags, value, cas

    def set(self, key: str, flags: int, exptime: int, value: bytes) -> None:
        self.writeline(f"set {key} {flags} {exptime} {len(value)}".encode())
        self.writeline(value)
        line = self.readline()
        if line != b"STORED":
            raise MemcachedError(line)

    def readvalue(self, n: int) -> bytes:  # pylint: disable=invalid-name
        while len(self.buffer) < n + 2:
            self.buffer += self.socket.recv(n + 2 - len(self.buffer))
        if self.buffer[n : n + 2] != b"\r\n":
            raise MemcachedError
        result = self.buffer[:n]
        self.buffer = self.buffer[n + 2 :]
        return result

    def readline(self) -> bytes:
        while True:
            index = self.buffer.find(b"\r\n")
            if index == -1:
                self.buffer += self.socket.recv(1024)
            else:
                line = self.buffer[:index]
                self.buffer = self.buffer[index + 2 :]
                return line

    def writeline(self, line: bytes) -> None:
        self.socket.send(line + b"\r\n")
