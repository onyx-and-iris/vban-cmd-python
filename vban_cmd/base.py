import socket
import time
from abc import ABCMeta, abstractmethod
from enum import IntEnum
from threading import Thread
from typing import Iterable, NoReturn, Optional, Union

from .misc import Event
from .packet import (
    HEADER_SIZE,
    RegisterRTHeader,
    TextRequestHeader,
    VBAN_VMRT_Packet_Data,
    VBAN_VMRT_Packet_Header,
)
from .subject import Subject
from .util import comp, script

Socket = IntEnum("Socket", "register request response", start=0)


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
        self.register_header = RegisterRTHeader()
        self.expected_packet = VBAN_VMRT_Packet_Header()

        self.socks = tuple(
            socket.socket(socket.AF_INET, socket.SOCK_DGRAM) for _ in Socket
        )
        self.running = True
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
        """Start listening for RT Packets"""

        self.socks[Socket.response.value].bind(
            (socket.gethostbyname(socket.gethostname()), self.port)
        )
        worker = Thread(target=self._send_register_rt, daemon=True)
        worker.start()
        self._public_packet = self._get_rt()
        worker2 = Thread(target=self._updates, daemon=True)
        worker2.start()
        time.sleep(0.1)

    def _send_register_rt(self):
        """Fires a subscription packet every 10 seconds"""

        while self.running:
            self.socks[Socket.register.value].sendto(
                self.register_header.header,
                (socket.gethostbyname(self.ip), self.port),
            )
            count = int.from_bytes(self.register_header.framecounter, "little") + 1
            self.register_header.framecounter = count.to_bytes(4, "little")
            time.sleep(10)

    def _fetch_rt_packet(self) -> Optional[VBAN_VMRT_Packet_Data]:
        """Returns a valid RT Data Packet or None"""
        data, _ = self.socks[Socket.response.value].recvfrom(2048)
        # check for packet data
        if len(data) > HEADER_SIZE:
            # check if packet is of type VBAN
            if self.expected_packet.header == data[: HEADER_SIZE - 4]:
                return VBAN_VMRT_Packet_Data(
                    _voicemeeterType=data[28:29],
                    _reserved=data[29:30],
                    _buffersize=data[30:32],
                    _voicemeeterVersion=data[32:36],
                    _optionBits=data[36:40],
                    _samplerate=data[40:44],
                    _inputLeveldB100=data[44:112],
                    _outputLeveldB100=data[112:240],
                    _TransportBit=data[240:244],
                    _stripState=data[244:276],
                    _busState=data[276:308],
                    _stripGaindB100Layer1=data[308:324],
                    _stripGaindB100Layer2=data[324:340],
                    _stripGaindB100Layer3=data[340:356],
                    _stripGaindB100Layer4=data[356:372],
                    _stripGaindB100Layer5=data[372:388],
                    _stripGaindB100Layer6=data[388:404],
                    _stripGaindB100Layer7=data[404:420],
                    _stripGaindB100Layer8=data[420:436],
                    _busGaindB100=data[436:452],
                    _stripLabelUTF8c60=data[452:932],
                    _busLabelUTF8c60=data[932:1412],
                )

    def _get_rt(self) -> VBAN_VMRT_Packet_Data:
        """Attempt to fetch data packet until a valid one found"""

        def fget():
            data = False
            while not data:
                data = self._fetch_rt_packet()
                time.sleep(self.DELAY)
            return data

        return fget()

    def _set_rt(
        self,
        id_: str,
        param: Optional[str] = None,
        val: Optional[Union[int, float]] = None,
    ):
        """Sends a string request command over a network."""
        cmd = id_ if not param else f"{id_}.{param}={val}"
        self.socks[Socket.request.value].sendto(
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

    def _updates(self) -> NoReturn:
        print(f"Listening for {', '.join(self.event.get())} events")
        self.cache["strip_level"], self.cache["bus_level"] = self._get_levels(
            self.public_packet
        )

        while self.running:
            start = time.time()
            self._pp = self._get_rt()
            self._strip_buf, self._bus_buf = self._get_levels(self._pp)
            self._pdirty = self._pp.pdirty(self.public_packet)

            if self.event.ldirty and self.ldirty:
                self.cache["strip_level"] = self._strip_buf
                self.cache["bus_level"] = self._bus_buf
                self.subject.notify("ldirty")
            if self.public_packet != self._pp:
                self._public_packet = self._pp
            if self.event.pdirty and self.pdirty:
                self.subject.notify("pdirty")
            elapsed = time.time() - start
            if self.ratelimit - elapsed > 0:
                time.sleep(self.ratelimit - elapsed)

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
