from dataclasses import dataclass
from typing import NamedTuple

from vban_cmd.enums import NBS
from vban_cmd.kinds import KindMapClass
from vban_cmd.util import comp

from .enums import ChannelModes
from .headers import VbanPacket


class Levels(NamedTuple):
    strip: tuple[float, ...]
    bus: tuple[float, ...]


class ChannelState:
    """Represents the processed state of a single strip or bus channel"""

    def __init__(self, state_bytes: bytes):
        # Convert 4-byte state to integer once for efficient lookups
        self._state = int.from_bytes(state_bytes, 'little')

    def get_mode(self, mode_value: int) -> bool:
        """Get boolean state for a specific mode"""
        return (self._state & mode_value) != 0

    def get_mode_int(self, mode_value: int) -> int:
        """Get integer state for a specific mode"""
        return self._state & mode_value

    # Common boolean modes
    @property
    def mute(self) -> bool:
        return (self._state & ChannelModes.MUTE.value) != 0

    @property
    def solo(self) -> bool:
        return (self._state & ChannelModes.SOLO.value) != 0

    @property
    def mono(self) -> bool:
        return (self._state & ChannelModes.MONO.value) != 0

    @property
    def mc(self) -> bool:
        return (self._state & ChannelModes.MC.value) != 0

    # EQ modes
    @property
    def eq_on(self) -> bool:
        return (self._state & ChannelModes.ON.value) != 0

    @property
    def eq_ab(self) -> bool:
        return (self._state & ChannelModes.AB.value) != 0

    # Bus assignments (strip to bus routing)
    @property
    def busa1(self) -> bool:
        return (self._state & ChannelModes.BUSA1.value) != 0

    @property
    def busa2(self) -> bool:
        return (self._state & ChannelModes.BUSA2.value) != 0

    @property
    def busa3(self) -> bool:
        return (self._state & ChannelModes.BUSA3.value) != 0

    @property
    def busa4(self) -> bool:
        return (self._state & ChannelModes.BUSA4.value) != 0

    @property
    def busb1(self) -> bool:
        return (self._state & ChannelModes.BUSB1.value) != 0

    @property
    def busb2(self) -> bool:
        return (self._state & ChannelModes.BUSB2.value) != 0

    @property
    def busb3(self) -> bool:
        return (self._state & ChannelModes.BUSB3.value) != 0


class States(NamedTuple):
    strip: tuple[ChannelState, ...]
    bus: tuple[ChannelState, ...]


class Labels(NamedTuple):
    strip: tuple[str, ...]
    bus: tuple[str, ...]


@dataclass
class VbanPacketNBS0(VbanPacket):
    """Represents the body of a VBAN data packet with ident:0"""

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

    @classmethod
    def from_bytes(cls, nbs: NBS, kind: KindMapClass, data: bytes):
        return cls(
            nbs=nbs,
            _kind=kind,
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

    def pdirty(self, other) -> bool:
        """True iff any defined parameter has changed"""

        self_gains = (
            self._stripGaindB100Layer1
            + self._stripGaindB100Layer2
            + self._stripGaindB100Layer3
            + self._stripGaindB100Layer4
            + self._stripGaindB100Layer5
            + self._stripGaindB100Layer6
            + self._stripGaindB100Layer7
            + self._stripGaindB100Layer8
        )
        other_gains = (
            other._stripGaindB100Layer1
            + other._stripGaindB100Layer2
            + other._stripGaindB100Layer3
            + other._stripGaindB100Layer4
            + other._stripGaindB100Layer5
            + other._stripGaindB100Layer6
            + other._stripGaindB100Layer7
            + other._stripGaindB100Layer8
        )

        return (
            self._stripState != other._stripState
            or self._busState != other._busState
            or self_gains != other_gains
            or self._busGaindB100 != other._busGaindB100
            or self._stripLabelUTF8c60 != other._stripLabelUTF8c60
            or self._busLabelUTF8c60 != other._busLabelUTF8c60
        )

    def ldirty(self, strip_cache, bus_cache) -> bool:
        """True iff any level has changed, ignoring changes when levels are very quiet"""
        self._strip_comp, self._bus_comp = (
            tuple(not val for val in comp(strip_cache, self.strip_levels)),
            tuple(not val for val in comp(bus_cache, self.bus_levels)),
        )
        return any(self._strip_comp) or any(self._bus_comp)

    @property
    def strip_levels(self) -> tuple[float, ...]:
        """Returns strip levels in dB"""
        return tuple(
            round(
                int.from_bytes(self._inputLeveldB100[i : i + 2], 'little', signed=True)
                * 0.01,
                1,
            )
            for i in range(0, len(self._inputLeveldB100), 2)
        )[: self._kind.num_strip_levels]

    @property
    def bus_levels(self) -> tuple[float, ...]:
        """Returns bus levels in dB"""
        return tuple(
            round(
                int.from_bytes(self._outputLeveldB100[i : i + 2], 'little', signed=True)
                * 0.01,
                1,
            )
            for i in range(0, len(self._outputLeveldB100), 2)
        )[: self._kind.num_bus_levels]

    @property
    def levels(self) -> Levels:
        """Returns strip and bus levels as a namedtuple"""
        return Levels(strip=self.strip_levels, bus=self.bus_levels)

    @property
    def states(self) -> States:
        """returns States object with processed strip and bus channel states"""
        return States(
            strip=tuple(
                ChannelState(self._stripState[i : i + 4]) for i in range(0, 32, 4)
            ),
            bus=tuple(ChannelState(self._busState[i : i + 4]) for i in range(0, 32, 4)),
        )

    @property
    def gainlayers(self) -> tuple:
        """returns tuple of all strip gain layers as tuples"""
        return tuple(
            tuple(
                round(
                    int.from_bytes(
                        getattr(self, f'_stripGaindB100Layer{layer}')[i : i + 2],
                        'little',
                        signed=True,
                    )
                    * 0.01,
                    2,
                )
                for i in range(0, 16, 2)
            )
            for layer in range(1, 9)
        )

    @property
    def busgain(self) -> tuple:
        """returns tuple of bus gains"""
        return tuple(
            round(
                int.from_bytes(self._busGaindB100[i : i + 2], 'little', signed=True)
                * 0.01,
                2,
            )
            for i in range(0, 16, 2)
        )

    @property
    def labels(self) -> Labels:
        """returns Labels namedtuple of strip and bus labels"""

        def _extract_labels_from_bytes(label_bytes: bytes) -> tuple[str, ...]:
            """Extract null-terminated UTF-8 labels from 60-byte chunks"""
            labels = []
            for i in range(0, len(label_bytes), 60):
                chunk = label_bytes[i : i + 60]
                null_pos = chunk.find(b'\x00')
                if null_pos == -1:
                    try:
                        label = chunk.decode('utf-8', errors='replace').rstrip('\x00')
                    except UnicodeDecodeError:
                        label = ''
                else:
                    try:
                        label = (
                            chunk[:null_pos].decode('utf-8', errors='replace')
                            if null_pos > 0
                            else ''
                        )
                    except UnicodeDecodeError:
                        label = ''
                labels.append(label)
            return tuple(labels)

        return Labels(
            strip=_extract_labels_from_bytes(self._stripLabelUTF8c60),
            bus=_extract_labels_from_bytes(self._busLabelUTF8c60),
        )
