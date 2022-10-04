import logging
import socket
import time
from abc import ABCMeta, abstractmethod
from typing import Iterable, Optional, Union

from .event import Event
from .packet import RequestHeader
from .subject import Subject
from .util import Socket, script
from .worker import Subscriber, Updater


class VbanCmd(metaclass=ABCMeta):
    """Base class responsible for communicating with the VBAN RT Packet Service"""

    DELAY = 0.001
    # fmt: off
    BPS_OPTS = [
        0, 110, 150, 300, 600, 1200, 2400, 4800, 9600, 14400, 19200, 31250,
        38400, 57600, 115200, 128000, 230400, 250000, 256000, 460800, 921600,
        1000000, 1500000, 2000000, 3000000,
    ]
    # fmt: on
    logger = logging.getLogger("vbancmd.vbancmd")

    def __init__(self, **kwargs):
        for attr, val in kwargs.items():
            setattr(self, attr, val)

        self.packet_request = RequestHeader(
            name=self.streamname,
            bps_index=self.BPS_OPTS.index(self.bps),
            channel=self.channel,
        )
        self.socks = tuple(
            socket.socket(socket.AF_INET, socket.SOCK_DGRAM) for _ in Socket
        )
        self.subject = Subject()
        self.cache = {}
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
        self.event.info()

        self.subscriber = Subscriber(self)
        self.subscriber.start()

        self.updater = Updater(self)
        self.updater.start()

        self.logger.info(f"{type(self).__name__}: Successfully logged into {self}")

    def _set_rt(
        self,
        id_: str,
        param: Optional[str] = None,
        val: Optional[Union[int, float]] = None,
    ):
        """Sends a string request command over a network."""
        cmd = id_ if not param else f"{id_}.{param}={val}"
        self.socks[Socket.request].sendto(
            self.packet_request.header + cmd.encode(),
            (socket.gethostbyname(self.ip), self.port),
        )
        count = int.from_bytes(self.packet_request.framecounter, "little") + 1
        self.packet_request.framecounter = count.to_bytes(4, "little")
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
        return "{0}.{1}.{2}.{3}".format(*self.public_packet.voicemeeterversion)

    @property
    def pdirty(self):
        """True iff a parameter has changed"""
        return self._pdirty

    @property
    def ldirty(self):
        """True iff a level value has changed."""
        return self._ldirty

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
            packet.inputlevels,
            packet.outputlevels,
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
            self.logger.info(f"Profile '{name}' applied!")
        except KeyError as e:
            self.logger.error(("\n").join(error_msg))

    def logout(self):
        self.running = False
        time.sleep(0.2)
        [sock.close() for sock in self.socks]
        self.logger.info(f"{type(self).__name__}: Successfully logged out of {self}")

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.logout()