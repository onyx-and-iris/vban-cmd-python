import time
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass


@dataclass
class Modes:
    """Channel Modes"""

    _mute: hex = 0x00000001
    _solo: hex = 0x00000002
    _mono: hex = 0x00000004
    _mc: hex = 0x00000008

    _amix: hex = 0x00000010
    _repeat: hex = 0x00000020
    _bmix: hex = 0x00000030
    _composite: hex = 0x00000040
    _tvmix: hex = 0x00000050
    _upmix21: hex = 0x00000060
    _upmix41: hex = 0x00000070
    _upmix61: hex = 0x00000080
    _centeronly: hex = 0x00000090
    _lfeonly: hex = 0x000000A0
    _rearonly: hex = 0x000000B0

    _mask: hex = 0x000000F0

    _eq_on: hex = 0x00000100
    _cross: hex = 0x00000200
    _eq_ab: hex = 0x00000800

    _busa: hex = 0x00001000
    _busa1: hex = 0x00001000
    _busa2: hex = 0x00002000
    _busa3: hex = 0x00004000
    _busa4: hex = 0x00008000
    _busa5: hex = 0x00080000

    _busb: hex = 0x00010000
    _busb1: hex = 0x00010000
    _busb2: hex = 0x00020000
    _busb3: hex = 0x00040000

    _pan0: hex = 0x00000000
    _pancolor: hex = 0x00100000
    _panmod: hex = 0x00200000
    _panmask: hex = 0x00F00000

    _postfx_r: hex = 0x01000000
    _postfx_d: hex = 0x02000000
    _postfx1: hex = 0x04000000
    _postfx2: hex = 0x08000000

    _sel: hex = 0x10000000
    _monitor: hex = 0x20000000

    @property
    def modevals(self):
        return (
            val
            for val in [
                self._amix,
                self._repeat,
                self._bmix,
                self._composite,
                self._tvmix,
                self._upmix21,
                self._upmix41,
                self._upmix61,
                self._centeronly,
                self._lfeonly,
                self._rearonly,
            ]
        )


class IRemote(metaclass=ABCMeta):
    """
    Common interface between base class and extended (higher) classes

    Provides some default implementation
    """

    def __init__(self, remote, index=None):
        self._remote = remote
        self.index = index
        self._modes = Modes()

    def getter(self, param):
        cmd = f"{self.identifier}.{param}"
        if cmd in self._remote.cache:
            return self._remote.cache.pop(cmd)

    def setter(self, param, val):
        """Sends a string request RT packet."""
        self._remote._set_rt(f"{self.identifier}", param, val)

    @abstractmethod
    def identifier(self):
        pass

    @property
    def public_packet(self):
        """Returns an RT data packet."""
        return self._remote.public_packet

    def apply(self, data):
        """Sets all parameters of a dict for the channel."""
        script = ""
        for attr, val in data.items():
            if hasattr(self, attr):
                self._remote.cache[f"{self.identifier}[{self.index}].{attr}"] = val
                script += f"{self.identifier}[{self.index}].{attr}={val};"

        self._remote.sendtext(script)
        return self

    def then_wait(self):
        time.sleep(self._remote.DELAY)
