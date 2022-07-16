from dataclasses import dataclass
from typing import Generator

VBAN_SERVICE_RTPACKETREGISTER = 32
VBAN_SERVICE_RTPACKET = 33
MAX_PACKET_SIZE = 1436
HEADER_SIZE = 4 + 1 + 1 + 1 + 1 + 16 + 4


@dataclass
class VBAN_VMRT_Packet_Data:
    """Represents the structure of a VMRT data packet"""

    _voicemeeterType: bytes
    _reserved: bytes
    _buffersize: bytes
    _voicemeeterVersion: bytes
    _optionBits: bytes
    _samplerate: bytes
    _inputLeveldB100: bytes
    _outputLeveldB100: bytes
    _TransportBit: bytes
    _stripState: bytes
    _busState: bytes
    _stripGaindB100Layer1: bytes
    _stripGaindB100Layer2: bytes
    _stripGaindB100Layer3: bytes
    _stripGaindB100Layer4: bytes
    _stripGaindB100Layer5: bytes
    _stripGaindB100Layer6: bytes
    _stripGaindB100Layer7: bytes
    _stripGaindB100Layer8: bytes
    _busGaindB100: bytes
    _stripLabelUTF8c60: bytes
    _busLabelUTF8c60: bytes

    def pdirty(self, other):
        """True iff any defined parameter has changed"""

        return not (
            self._stripState == other._stripState
            and self._busState == other._busState
            and self._stripLabelUTF8c60 == other._stripLabelUTF8c60
            and self._busLabelUTF8c60 == other._busLabelUTF8c60
            and self._stripGaindB100Layer1 == other._stripGaindB100Layer1
            and self._stripGaindB100Layer2 == other._stripGaindB100Layer2
            and self._stripGaindB100Layer3 == other._stripGaindB100Layer3
            and self._stripGaindB100Layer4 == other._stripGaindB100Layer4
            and self._stripGaindB100Layer5 == other._stripGaindB100Layer5
            and self._stripGaindB100Layer6 == other._stripGaindB100Layer6
            and self._stripGaindB100Layer7 == other._stripGaindB100Layer7
            and self._stripGaindB100Layer8 == other._stripGaindB100Layer8
            and self._busGaindB100 == other._busGaindB100
        )

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
    def inputlevels(self) -> Generator[float, None, None]:
        """returns the entire level array across all inputs"""
        for i in range(0, 68, 2):
            val = ((1 << 16) - 1) - int.from_bytes(
                self._inputLeveldB100[i : i + 2], "little"
            )
            if val != ((1 << 16) - 1):
                yield val

    @property
    def outputlevels(self) -> Generator[float, None, None]:
        """returns the entire level array across all outputs"""
        for i in range(0, 128, 2):
            val = ((1 << 16) - 1) - int.from_bytes(
                self._outputLeveldB100[i : i + 2], "little"
            )
            if val != ((1 << 16) - 1):
                yield val

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
            ((1 << 16) - 1)
            - int.from_bytes(self._stripGaindB100Layer1[i : i + 2], "little")
            for i in range(0, 16, 2)
        )

    @property
    def stripgainlayer2(self) -> tuple:
        return tuple(
            ((1 << 16) - 1)
            - int.from_bytes(self._stripGaindB100Layer2[i : i + 2], "little")
            for i in range(0, 16, 2)
        )

    @property
    def stripgainlayer3(self) -> tuple:
        return tuple(
            ((1 << 16) - 1)
            - int.from_bytes(self._stripGaindB100Layer3[i : i + 2], "little")
            for i in range(0, 16, 2)
        )

    @property
    def stripgainlayer4(self) -> tuple:
        return tuple(
            ((1 << 16) - 1)
            - int.from_bytes(self._stripGaindB100Layer4[i : i + 2], "little")
            for i in range(0, 16, 2)
        )

    @property
    def stripgainlayer5(self) -> tuple:
        return tuple(
            ((1 << 16) - 1)
            - int.from_bytes(self._stripGaindB100Layer5[i : i + 2], "little")
            for i in range(0, 16, 2)
        )

    @property
    def stripgainlayer6(self) -> tuple:
        return tuple(
            ((1 << 16) - 1)
            - int.from_bytes(self._stripGaindB100Layer6[i : i + 2], "little")
            for i in range(0, 16, 2)
        )

    @property
    def stripgainlayer7(self) -> tuple:
        return tuple(
            ((1 << 16) - 1)
            - int.from_bytes(self._stripGaindB100Layer7[i : i + 2], "little")
            for i in range(0, 16, 2)
        )

    @property
    def stripgainlayer8(self) -> tuple:
        return tuple(
            ((1 << 16) - 1)
            - int.from_bytes(self._stripGaindB100Layer8[i : i + 2], "little")
            for i in range(0, 16, 2)
        )

    @property
    def busgain(self) -> tuple:
        """returns tuple of bus gains"""
        return tuple(
            ((1 << 16) - 1) - int.from_bytes(self._busGaindB100[i : i + 2], "little")
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
class VBAN_VMRT_Packet_Header:
    """Represents a RESPONSE RT PACKET header"""

    name = "Voicemeeter-RTP"
    vban: bytes = "VBAN".encode()
    format_sr: bytes = (0x60).to_bytes(1, "little")
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
        assert len(header) == HEADER_SIZE - 4, f"Header expected {HEADER_SIZE-4} bytes"
        return header


@dataclass
class TextRequestHeader:
    """Represents a REQUEST RT PACKET header"""

    name: str
    bps_index: int
    channel: int
    vban: bytes = "VBAN".encode()
    nbs: bytes = (0).to_bytes(1, "little")
    bit: bytes = (0x10).to_bytes(1, "little")
    framecounter: bytes = (0).to_bytes(4, "little")

    @property
    def sr(self):
        return (0x40 + self.bps_index).to_bytes(1, "little")

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
        assert len(header) == HEADER_SIZE, f"Header expected {HEADER_SIZE} bytes"
        return header


@dataclass
class RegisterRTHeader:
    """Represents a REGISTER RT PACKET header"""

    name = "Register RTP"
    timeout = 15
    vban: bytes = "VBAN".encode()
    format_sr: bytes = (0x60).to_bytes(1, "little")
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
        assert len(header) == HEADER_SIZE, f"Header expected {HEADER_SIZE} bytes"
        return header
