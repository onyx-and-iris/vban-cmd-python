import socket
import time
from abc import ABCMeta, abstractmethod
from typing import Iterable, NoReturn, Optional, Union

from .misc import Event
from .packet import TextRequestHeader
from .subject import Subject
from .util import Socket, comp, script
from .worker import Subscriber, Updater


class VbanCmd(metaclass=ABCMeta):
    """Base class responsible for communicating over VBAN RT Service"""

    DELAY = 0.001
    # fmt: off
    BPS_OPTS = [
        0, 110, 150, 300, 600, 1200, 2400, 4800, 9600, 14400, 19200, 31250,
        38400, 57600, 115200, 128000, 230400, 250000, 256000, 460800, 921600,
        1000000, 1500000, 2000000, 3000000,
    ]
    # fmt: on

    def __init__(self, **kwargs):
        for attr, val in kwargs.items():
            setattr(self, attr, val)

        self.text_header = TextRequestHeader(
            name=self.streamname,
            bps_index=self.BPS_OPTS.index(self.bps),
            channel=self.channel,
        )
        self.socks = tuple(
            socket.socket(socket.AF_INET, socket.SOCK_DGRAM) for _ in Socket
        )
        self.subject = Subject()
        self.cache = dict()
        self.event = Event(self.subs)

    @abstractmethod
    def __str__(self):
        """Ensure subclasses override str magic method"""
        pass

    def __enter__(self):
        self.login()
        return self

    def login(self):
        """Starts the subscriber and updater threads"""
        self.running = True

        self.subscriber = Subscriber(self)
        self.subscriber.start()

        self.updater = Updater(self)
        self.updater.start()

    def _set_rt(
        self,
        id_: str,
        param: Optional[str] = None,
        val: Optional[Union[int, float]] = None,
    ):
        """Sends a string request command over a network."""
        cmd = id_ if not param else f"{id_}.{param}={val}"
        self.socks[Socket.request].sendto(
            self.text_header.header + cmd.encode(),
            (socket.gethostbyname(self.ip), self.port),
        )
        count = int.from_bytes(self.text_header.framecounter, "little") + 1
        self.text_header.framecounter = count.to_bytes(4, "little")
        if param:
            self.cache[f"{id_}.{param}"] = val
        if self.sync:
            time.sleep(0.02)

    @script
    def sendtext(self, cmd):
        """Sends a multiple parameter string over a network."""
        self._set_rt(cmd)
        time.sleep(self.DELAY)

    @property
    def type(self) -> str:
        """Returns the type of Voicemeeter installation."""
        return self.public_packet.voicemeetertype

    @property
    def version(self) -> str:
        """Returns Voicemeeter's version as a string"""
        v1, v2, v3, v4 = self.public_packet.voicemeeterversion
        return f"{v1}.{v2}.{v3}.{v4}"

    @property
    def pdirty(self):
        """True iff a parameter has changed"""
        return self._pdirty

    @property
    def ldirty(self):
        """True iff a level value has changed."""
        self._strip_comp, self._bus_comp = (
            tuple(not x for x in comp(self.cache["strip_level"], self._strip_buf)),
            tuple(not x for x in comp(self.cache["bus_level"], self._bus_buf)),
        )
        return any(any(l) for l in (self._strip_comp, self._bus_comp))

    @property
    def public_packet(self):
        return self._public_packet

    def clear_dirty(self):
        while self.pdirty:
            pass

    def _get_levels(self, packet) -> Iterable:
        """
        returns both level arrays (strip_levels, bus_levels) BEFORE math conversion

        strip levels in PREFADER mode.
        """
        return (
            tuple(val for val in packet.inputlevels),
            tuple(val for val in packet.outputlevels),
        )

    def apply(self, data: dict):
        """
        Sets all parameters of a dict

        minor delay between each recursion
        """

        def param(key):
            obj, m2, *rem = key.split("-")
            index = int(m2) if m2.isnumeric() else int(*rem)
            if obj in ("strip", "bus"):
                return getattr(self, obj)[index]
            else:
                raise ValueError(obj)

        [param(key).apply(datum).then_wait() for key, datum in data.items()]

    def apply_config(self, name):
        """applies a config from memory"""
        error_msg = (
            f"No config with name '{name}' is loaded into memory",
            f"Known configs: {list(self.configs.keys())}",
        )
        try:
            self.apply(self.configs[name])
            print(f"Profile '{name}' applied!")
        except KeyError as e:
            print(("\n").join(error_msg))

    def logout(self):
        self.running = False
        time.sleep(0.2)
        [sock.close() for sock in self.socks]

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.logout()
