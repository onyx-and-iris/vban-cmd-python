import socket
import time
from typing import Iterator

from .error import VBANCMDConnectionError


def ratelimit(func):
    """ratelimit decorator for {VbanCmd}.sendtext, to prevent flooding the network with script requests."""

    def wrapper(*args, **kwargs):
        self, *rem = args
        if self.script_ratelimit > 0:
            now = time.time()
            elapsed = now - self._last_script_request_time
            if elapsed < self.script_ratelimit:
                time.sleep(self.script_ratelimit - elapsed)
            self._last_script_request_time = time.time()
        return func(*args, **kwargs)

    return wrapper


def pong_timeout(func):
    """pong_timeout decorator for {VbanCmd}._handle_pong, to handle timeout logic and socket management."""

    def wrapper(self, timeout: float = None):
        if timeout is None:
            timeout = min(self.timeout, 3.0)

        original_timeout = self.sock.gettimeout()
        self.sock.settimeout(0.5)

        try:
            start_time = time.time()
            response_count = 0

            while time.time() - start_time < timeout:
                try:
                    response_count += 1

                    if func(self):
                        return

                except socket.timeout:
                    continue

            self.logger.debug(
                f'PING timeout after {timeout}s, received {response_count} non-PONG packets'
            )
            raise VBANCMDConnectionError(
                f'PING timeout: No response from {self.host}:{self.port} after {timeout}s'
            )

        finally:
            self.sock.settimeout(original_timeout)

    return wrapper


def cache_bool(func, param):
    """Check cache for a bool prop"""

    def wrapper(*args, **kwargs):
        self, *rem = args
        if self._cmd(param) in self._remote.cache:
            return self._remote.cache.pop(self._cmd(param)) == 1
        if self._remote.sync:
            self._remote.clear_dirty()
        return func(*args, **kwargs)

    return wrapper


def cache_int(func, param):
    """Check cache for an int prop"""

    def wrapper(*args, **kwargs):
        self, *rem = args
        if self._cmd(param) in self._remote.cache:
            return self._remote.cache.pop(self._cmd(param))
        if self._remote.sync:
            self._remote.clear_dirty()
        return func(*args, **kwargs)

    return wrapper


def cache_string(func, param):
    """Check cache for a string prop"""

    def wrapper(*args, **kwargs):
        self, *rem = args
        if self._cmd(param) in self._remote.cache:
            return self._remote.cache.pop(self._cmd(param)).strip('"')
        if self._remote.sync:
            self._remote.clear_dirty()
        return func(*args, **kwargs)

    return wrapper


def cache_float(func, param):
    """Check cache for a float prop"""

    def wrapper(*args, **kwargs):
        self, *rem = args
        if self._cmd(param) in self._remote.cache:
            return round(self._remote.cache.pop(self._cmd(param)), 2)
        if self._remote.sync:
            self._remote.clear_dirty()
        return func(*args, **kwargs)

    return wrapper


def depth(d):
    if isinstance(d, dict):
        return 1 + (max(map(depth, d.values())) if d else 0)
    return 0


def comp(t0: tuple, t1: tuple) -> Iterator[bool]:
    """
    Generator function, accepts two tuples of dB values.

    Evaluates equality of each member in both tuples.
    Only ignores changes when levels are very quiet (below -72 dB).
    """

    for a, b in zip(t0, t1):
        # If both values are very quiet (below -72dB), ignore small changes
        if a <= -72.0 and b <= -72.0:
            yield a == b  # Both quiet, check if they're equal
        else:
            yield a != b  # At least one has significant level, detect changes


def deep_merge(dict1, dict2):
    """Generator function for deep merging two dicts"""
    for k in set(dict1) | set(dict2):
        if k in dict1 and k in dict2:
            if isinstance(dict1[k], dict) and isinstance(dict2[k], dict):
                yield k, dict(deep_merge(dict1[k], dict2[k]))
            else:
                yield k, dict2[k]
        elif k in dict1:
            yield k, dict1[k]
        else:
            yield k, dict2[k]


def bump_framecounter(framecounter: int) -> int:
    """Increment framecounter with rollover at 0xFFFFFFFF."""
    if framecounter > 0xFFFFFFFF:
        return 0
    else:
        return framecounter + 1
