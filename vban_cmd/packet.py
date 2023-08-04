from dataclasses import dataclass

from .kinds import KindMapClass
from .util import comp

VBAN_PROTOCOL_TXT = 0x40
VBAN_PROTOCOL_SERVICE = 0x60

VBAN_SERVICE_RTPACKETREGISTER = 32
VBAN_SERVICE_RTPACKET = 33

MAX_PACKET_SIZE = 1436
HEADER_SIZE = 4 + 1 + 1 + 1 + 1 + 16


@dataclass
class VbanRtPacket:
    """Represents the body of a VBAN RT data packet"""

    _kind: KindMapClass
    _voicemeeterType: bytes  # data[28:29]
    _reserved: bytes  # data[29:30]
    _buffersize: bytes  # data[30:32]
    _voicemeeterVersion: bytes  # data[32:36]
    _optionBits: bytes  # data[36:40]
    _samplerate: bytes  # data[40:44]
    _inputLeveldB100: bytes  # data[44:112]
    _outputLeveldB100: bytes  # data[112:240]
    _TransportBit: bytes  # data[240:244]
    _stripState: bytes  # data[244:276]
    _busState: bytes  # data[276:308]
    _stripGaindB100Layer1: bytes  # data[308:324]
    _stripGaindB100Layer2: bytes  # data[324:340]
    _stripGaindB100Layer3: bytes  # data[340:356]
    _stripGaindB100Layer4: bytes  # data[356:372]
    _stripGaindB100Layer5: bytes  # data[372:388]
    _stripGaindB100Layer6: bytes  # data[388:404]
    _stripGaindB100Layer7: bytes  # data[404:420]
    _stripGaindB100Layer8: bytes  # data[420:436]
    _busGaindB100: bytes  # data[436:452]
    _stripLabelUTF8c60: bytes  # data[452:932]
    _busLabelUTF8c60: bytes  # data[932:1412]

    def _generate_levels(self, levelarray) -> tuple:
        return tuple(
            int.from_bytes(levelarray[i : i + 2], "little")
            for i in range(0, len(levelarray), 2)
        )

    @property
    def strip_levels(self):
        return self._generate_levels(self._inputLeveldB100)

    @property
    def bus_levels(self):
        return self._generate_levels(self._outputLeveldB100)

    def pdirty(self, other) -> bool:
        """True iff any defined parameter has changed"""

        return not (
            self._stripState == other._stripState
            and self._busState == other._busState
            and self._stripGaindB100Layer1 == other._stripGaindB100Layer1
            and self._stripGaindB100Layer2 == other._stripGaindB100Layer2
            and self._stripGaindB100Layer3 == other._stripGaindB100Layer3
            and self._stripGaindB100Layer4 == other._stripGaindB100Layer4
            and self._stripGaindB100Layer5 == other._stripGaindB100Layer5
            and self._stripGaindB100Layer6 == other._stripGaindB100Layer6
            and self._stripGaindB100Layer7 == other._stripGaindB100Layer7
            and self._stripGaindB100Layer8 == other._stripGaindB100Layer8
            and self._busGaindB100 == other._busGaindB100
            and self._stripLabelUTF8c60 == other._stripLabelUTF8c60
            and self._busLabelUTF8c60 == other._busLabelUTF8c60
        )

    def ldirty(self, strip_cache, bus_cache) -> bool:
        self._strip_comp, self._bus_comp = (
            tuple(not val for val in comp(strip_cache, self.strip_levels)),
            tuple(not val for val in comp(bus_cache, self.bus_levels)),
        )
        return any(any(l) for l in (self._strip_comp, self._bus_comp))

    @property
    def voicemeetertype(self) -> str:
        """returns voicemeeter type as a string"""
        type_ = ("basic", "banana", "potato")
        return type_[int.from_bytes(self._voicemeeterType, "little") - 1]

    @property
    def voicemeeterversion(self) -> tuple:
        """returns voicemeeter version as a tuple"""
        return tuple(
            reversed(
                tuple(
                    int.from_bytes(self._voicemeeterVersion[i : i + 1], "little")
                    for i in range(4)
                )
            )
        )

    @property
    def samplerate(self) -> int:
        """returns samplerate as an int"""
        return int.from_bytes(self._samplerate, "little")

    @property
    def inputlevels(self) -> tuple:
        """returns the entire level array across all inputs for a kind"""
        return self.strip_levels[0 : self._kind.num_strip_levels]

    @property
    def outputlevels(self) -> tuple:
        """returns the entire level array across all outputs for a kind"""
        return self.bus_levels[0 : self._kind.num_bus_levels]

    @property
    def stripstate(self) -> tuple:
        """returns tuple of strip states accessable through bit modes"""
        return tuple(self._stripState[i : i + 4] for i in range(0, 32, 4))

    @property
    def busstate(self) -> tuple:
        """returns tuple of bus states accessable through bit modes"""
        return tuple(self._busState[i : i + 4] for i in range(0, 32, 4))

    """ 
    these functions return an array of gainlayers[i] across all strips 
    ie stripgainlayer1 = [strip[0].gainlayer[0], strip[1].gainlayer[0], strip[2].gainlayer[0]...]
    """

    @property
    def stripgainlayer1(self) -> tuple:
        return tuple(
            int.from_bytes(self._stripGaindB100Layer1[i : i + 2], "little")
            for i in range(0, 16, 2)
        )

    @property
    def stripgainlayer2(self) -> tuple:
        return tuple(
            int.from_bytes(self._stripGaindB100Layer2[i : i + 2], "little")
            for i in range(0, 16, 2)
        )

    @property
    def stripgainlayer3(self) -> tuple:
        return tuple(
            int.from_bytes(self._stripGaindB100Layer3[i : i + 2], "little")
            for i in range(0, 16, 2)
        )

    @property
    def stripgainlayer4(self) -> tuple:
        return tuple(
            int.from_bytes(self._stripGaindB100Layer4[i : i + 2], "little")
            for i in range(0, 16, 2)
        )

    @property
    def stripgainlayer5(self) -> tuple:
        return tuple(
            int.from_bytes(self._stripGaindB100Layer5[i : i + 2], "little")
            for i in range(0, 16, 2)
        )

    @property
    def stripgainlayer6(self) -> tuple:
        return tuple(
            int.from_bytes(self._stripGaindB100Layer6[i : i + 2], "little")
            for i in range(0, 16, 2)
        )

    @property
    def stripgainlayer7(self) -> tuple:
        return tuple(
            int.from_bytes(self._stripGaindB100Layer7[i : i + 2], "little")
            for i in range(0, 16, 2)
        )

    @property
    def stripgainlayer8(self) -> tuple:
        return tuple(
            int.from_bytes(self._stripGaindB100Layer8[i : i + 2], "little")
            for i in range(0, 16, 2)
        )

    @property
    def busgain(self) -> tuple:
        """returns tuple of bus gains"""
        return tuple(
            int.from_bytes(self._busGaindB100[i : i + 2], "little")
            for i in range(0, 16, 2)
        )

    @property
    def striplabels(self) -> tuple:
        """returns tuple of strip labels"""
        return tuple(
            self._stripLabelUTF8c60[i : i + 60].decode().split("\x00")[0]
            for i in range(0, 480, 60)
        )

    @property
    def buslabels(self) -> tuple:
        """returns tuple of bus labels"""
        return tuple(
            self._busLabelUTF8c60[i : i + 60].decode().split("\x00")[0]
            for i in range(0, 480, 60)
        )


@dataclass
class SubscribeHeader:
    """Represents the header an RT Packet Service subscription packet"""

    name = "Register RTP"
    timeout = 15
    vban: bytes = "VBAN".encode()
    format_sr: bytes = (VBAN_PROTOCOL_SERVICE).to_bytes(1, "little")
    format_nbs: bytes = (0).to_bytes(1, "little")
    format_nbc: bytes = (VBAN_SERVICE_RTPACKETREGISTER).to_bytes(1, "little")
    format_bit: bytes = (timeout & 0x000000FF).to_bytes(1, "little")  # timeout
    streamname: bytes = name.encode("ascii") + bytes(16 - len(name))
    framecounter: bytes = (0).to_bytes(4, "little")

    @property
    def header(self):
        header = self.vban
        header += self.format_sr
        header += self.format_nbs
        header += self.format_nbc
        header += self.format_bit
        header += self.streamname
        header += self.framecounter
        assert (
            len(header) == HEADER_SIZE + 4
        ), f"expected header size {HEADER_SIZE} bytes + 4 bytes framecounter ({HEADER_SIZE +4} bytes total)"
        return header


@dataclass
class VbanRtPacketHeader:
    """Represents the header of a VBAN RT response packet"""

    name = "Voicemeeter-RTP"
    vban: bytes = "VBAN".encode()
    format_sr: bytes = (VBAN_PROTOCOL_SERVICE).to_bytes(1, "little")
    format_nbs: bytes = (0).to_bytes(1, "little")
    format_nbc: bytes = (VBAN_SERVICE_RTPACKET).to_bytes(1, "little")
    format_bit: bytes = (0).to_bytes(1, "little")
    streamname: bytes = name.encode("ascii") + bytes(16 - len(name))

    @property
    def header(self):
        header = self.vban
        header += self.format_sr
        header += self.format_nbs
        header += self.format_nbc
        header += self.format_bit
        header += self.streamname
        assert len(header) == HEADER_SIZE, f"expected header size {HEADER_SIZE} bytes"
        return header


@dataclass
class RequestHeader:
    """Represents the header of an REQUEST RT PACKET"""

    name: str
    bps_index: int
    channel: int
    vban: bytes = "VBAN".encode()
    nbs: bytes = (0).to_bytes(1, "little")
    bit: bytes = (0x10).to_bytes(1, "little")
    framecounter: bytes = (0).to_bytes(4, "little")

    @property
    def sr(self):
        return (VBAN_PROTOCOL_TXT + self.bps_index).to_bytes(1, "little")

    @property
    def nbc(self):
        return (self.channel).to_bytes(1, "little")

    @property
    def streamname(self):
        return self.name.encode() + bytes(16 - len(self.name))

    @property
    def header(self):
        header = self.vban
        header += self.sr
        header += self.nbs
        header += self.nbc
        header += self.bit
        header += self.streamname
        header += self.framecounter
        assert (
            len(header) == HEADER_SIZE + 4
        ), f"expected header size {HEADER_SIZE} bytes + 4 bytes framecounter ({HEADER_SIZE +4} bytes total)"
        return header
