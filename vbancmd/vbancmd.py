import abc
import select
import socket
from time import sleep
from threading import Thread
from typing import NamedTuple, NoReturn, Optional, Union

from .errors import VMCMDErrors
from . import kinds
from . import profiles
from .dataclass import (
    HEADER_SIZE,
    VBAN_VMRT_Packet_Data,
    VBAN_VMRT_Packet_Header,
    RegisterRTHeader,
    TextRequestHeader,
)
from .strip import InputStrip
from .bus import OutputBus
from .command import Command


class VbanCmd(abc.ABC):
    def __init__(self, **kwargs):
        self._ip = kwargs["ip"]
        self._port = kwargs["port"]
        self._streamname = kwargs["streamname"]
        self._bps = kwargs["bps"]
        self._channel = kwargs["channel"]
        self._delay = kwargs["delay"]
        self._ratelimiter = kwargs["ratelimiter"]
        self._sync = kwargs["sync"]
        # fmt: off
        self._bps_opts = [
            0, 110, 150, 300, 600, 1200, 2400, 4800, 9600, 14400, 19200, 31250,
            38400, 57600, 115200, 128000, 230400, 250000, 256000, 460800, 921600,
            1000000, 1500000, 2000000, 3000000,
        ]
        # fmt: on
        if self._channel not in range(256):
            raise VMCMDErrors("Channel must be in range 0 to 255")
        self._text_header = TextRequestHeader(
            name=self._streamname,
            bps_index=self._bps_opts.index(self._bps),
            channel=self._channel,
        )
        self._register_rt_header = RegisterRTHeader()
        self.expected_packet = VBAN_VMRT_Packet_Header()

        self._rt_register_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._rt_packet_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._sendrequest_string_socket = socket.socket(
            socket.AF_INET, socket.SOCK_DGRAM
        )

        is_readable = []
        is_writable = [
            self._rt_register_socket,
            self._rt_packet_socket,
            self._sendrequest_string_socket,
        ]
        is_error = []
        self.ready_to_read, self.ready_to_write, in_error = select.select(
            is_readable, is_writable, is_error, 60
        )
        self._public_packet = None
        self.running = True
        self._pdirty = False
        self.cache = {}

    def __enter__(self):
        self.login()
        return self

    def login(self):
        """
        Start listening for RT Packets

        Start background threads:

        Register to RT service
        Keep public packet updated.
        """
        self._rt_packet_socket.bind(
            (socket.gethostbyname(socket.gethostname()), self._port)
        )
        worker = Thread(target=self._send_register_rt, daemon=True)
        worker.start()
        self._public_packet = self._get_rt()
        worker2 = Thread(target=self._keepupdated, daemon=True)
        worker2.start()

    def _send_register_rt(self):
        """
        Continuously register to the RT Packet Service

        This function to be run in its own thread.
        """
        while self.running:
            if self._rt_register_socket in self.ready_to_write:
                self._rt_register_socket.sendto(
                    self._register_rt_header.header,
                    (socket.gethostbyname(self._ip), self._port),
                )
                count = (
                    int.from_bytes(self._register_rt_header.framecounter, "little") + 1
                )
                self._register_rt_header.framecounter = count.to_bytes(4, "little")
                sleep(10)

    def _fetch_rt_packet(self) -> Optional[VBAN_VMRT_Packet_Data]:
        """Returns a valid RT Data Packet or None"""
        if self._rt_packet_socket in self.ready_to_write:
            data, _ = self._rt_packet_socket.recvfrom(1024 * 2)
            # check for packet data
            if len(data) > HEADER_SIZE:
                # check if packet is of type rt service
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

    @property
    def pdirty(self):
        """True iff a parameter has changed"""
        return self._pdirty

    @property
    def public_packet(self):
        return self._public_packet

    @public_packet.setter
    def public_packet(self, val):
        self._public_packet = val

    def _keepupdated(self) -> NoReturn:
        """
        Continously update public packet in background.

        Set parameter dirty flag.

        Update public packet only if new private packet is found.

        This function to be run in its own thread.
        """
        while self.running:
            private_packet = self._get_rt()
            self._pdirty = private_packet.isdirty(self.public_packet)
            if not private_packet.__eq__(self.public_packet):
                self.public_packet = private_packet

    def _get_rt(self) -> VBAN_VMRT_Packet_Data:
        """Attempt to fetch data packet until a valid one found"""

        def fget():
            data = False
            while not data:
                data = self._fetch_rt_packet()
            return data

        return fget()

    def set_rt(
        self,
        id_: str,
        param: Optional[str] = None,
        val: Optional[Union[int, float]] = None,
    ):
        """Sends a string request command over a network."""
        cmd = id_ if not param and val else f"{id_}.{param}={val}"
        if self._sendrequest_string_socket in self.ready_to_write:
            self._sendrequest_string_socket.sendto(
                self._text_header.header + cmd.encode(),
                (socket.gethostbyname(self._ip), self._port),
            )
            count = int.from_bytes(self._text_header.framecounter, "little") + 1
            self._text_header.framecounter = count.to_bytes(4, "little")
            self.cache[f"{id_}.{param}"] = [val, True]
            if self._sync:
                sleep(self._ratelimiter)

    def sendtext(self, cmd):
        """Sends a multiple parameter string over a network."""
        self.set_rt(cmd)
        sleep(self._delay)

    @property
    def type(self):
        """Returns the type of Voicemeeter installation."""
        return self.public_packet.voicemeetertype

    @property
    def version(self):
        """Returns Voicemeeter's version as a tuple"""
        return self.public_packet.voicemeeterversion

    def show(self) -> NoReturn:
        """Shows Voicemeeter if it's hidden."""
        self.command.show()

    def hide(self) -> NoReturn:
        """Hides Voicemeeter if it's shown."""
        self.command.hide()

    def shutdown(self) -> NoReturn:
        """Closes Voicemeeter."""
        self.command.shutdown()

    def restart(self) -> NoReturn:
        """Restarts Voicemeeter's audio engine."""
        self.command.restart()

    def apply(self, mapping: dict):
        """Sets all parameters of a di"""
        for key, submapping in mapping.items():
            obj, index = key.split("-")

            if obj in ("strip"):
                target = self.strip[int(index)]
            elif obj in ("bus"):
                target = self.bus[int(index)]
            else:
                raise ValueError(obj)
            target.apply(submapping)

    def apply_profile(self, name: str):
        self._sync = True
        try:
            profile = self.profiles[name]
            if "extends" in profile:
                base = self.profiles[profile["extends"]]
                del profile["extends"]
                for key in profile.keys():
                    if key in base:
                        base[key] |= profile[key]
                    else:
                        base[key] = profile[key]
                profile = base
            self.apply(profile)
        except KeyError:
            raise VMCMDErrors(f"Unknown profile: {self.kind.id}/{name}")
        self._sync = False

    def reset(self) -> NoReturn:
        self.apply_profile("base")

    @property
    def strip_levels(self):
        """Returns the full level array for strips, PREFADER mode, before math conversion"""
        return self.public_packet.inputlevels

    @property
    def bus_levels(self):
        """Returns the full level array for buses, before math conversion"""
        return self.public_packet.outputlevels

    def logout(self):
        """sets thread flag, closes sockets"""
        self.running = False
        sleep(0.2)
        self._rt_register_socket.close()
        self._sendrequest_string_socket.close()
        self._rt_packet_socket.close()

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.logout()


def _make_remote(kind: NamedTuple) -> VbanCmd:
    """
    Creates a new remote class and sets its number of inputs
    and outputs for a VM kind.

    The returned class will subclass VbanCmd.
    """

    def init(self, **kwargs):
        defaultkwargs = {
            "ip": None,
            "port": 6990,
            "streamname": "Command1",
            "bps": 0,
            "channel": 0,
            "delay": 0.001,
            "ratelimiter": 0.018,
            "sync": False,
        }
        kwargs = defaultkwargs | kwargs
        VbanCmd.__init__(self, **kwargs)
        self.kind = kind
        self.phys_in, self.virt_in = kind.ins
        self.phys_out, self.virt_out = kind.outs
        self.strip = tuple(
            InputStrip.make((i < self.phys_in), self, i)
            for i in range(self.phys_in + self.virt_in)
        )
        self.bus = tuple(
            OutputBus.make((i < self.phys_out), self, i)
            for i in range(self.phys_out + self.virt_out)
        )
        self.command = Command.make(self)

    def get_profiles(self):
        return profiles.profiles[kind.id]

    return type(
        f"VbanCmd{kind.name}",
        (VbanCmd,),
        {"__init__": init, "profiles": property(get_profiles)},
    )


_remotes = {kind.id: _make_remote(kind) for kind in kinds.all}


def connect(kind_id: str, **kwargs):
    """Connect to Voicemeeter and sets its strip layout."""
    try:
        VBANCMD_cls = _remotes[kind_id]
        return VBANCMD_cls(**kwargs)
    except KeyError as err:
        raise VMCMDErrors(f"Invalid Voicemeeter kind: {kind_id}")
