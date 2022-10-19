from enum import IntEnum
from typing import Iterator


def cache_bool(func, param):
    """Check cache for a bool prop"""

    def wrapper(*args, **kwargs):
        self, *rem = args
        cmd = f"{self.identifier}.{param}"
        if cmd in self._remote.cache:
            return self._remote.cache.pop(cmd) == 1
        if self._remote.sync:
            self._remote.clear_dirty()
        return func(*args, **kwargs)

    return wrapper


def cache_string(func, param):
    """Check cache for a string prop"""

    def wrapper(*args, **kwargs):
        self, *rem = args
        cmd = f"{self.identifier}.{param}"
        if cmd in self._remote.cache:
            return self._remote.cache.pop(cmd)
        if self._remote.sync:
            self._remote.clear_dirty()
        return func(*args, **kwargs)

    return wrapper


def depth(d):
    if isinstance(d, dict):
        return 1 + (max(map(depth, d.values())) if d else 0)
    return 0


def script(func):
    """Convert dictionary to script"""

    def wrapper(*args):
        remote, script = args
        if isinstance(script, dict):
            params = ""
            for key, val in script.items():
                obj, m2, *rem = key.split("-")
                index = int(m2) if m2.isnumeric() else int(*rem)
                params += ";".join(
                    f"{obj}{f'.{m2}stream' if not m2.isnumeric() else ''}[{index}].{k}={int(v) if isinstance(v, bool) else v}"
                    for k, v in val.items()
                )
                params += ";"
            script = params
        return func(remote, script)

    return wrapper


def comp(t0: tuple, t1: tuple) -> Iterator[bool]:
    """
    Generator function, accepts two tuples.

    Evaluates equality of each member in both tuples.
    """

    for a, b in zip(t0, t1):
        if ((1 << 16) - 1) - b <= 7200:
            yield a == b
        else:
            yield True


Socket = IntEnum("Socket", "register request response", start=0)
