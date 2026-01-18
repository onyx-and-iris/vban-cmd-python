import struct
from dataclasses import dataclass
from typing import NamedTuple

from .enums import NBS
from .kinds import KindMapClass
from .util import comp

VBAN_PROTOCOL_TXT = 0x40
VBAN_PROTOCOL_SERVICE = 0x60

VBAN_SERVICE_RTPACKETREGISTER = 32
VBAN_SERVICE_RTPACKET = 33
VBAN_SERVICE_MASK = 0xE0

MAX_PACKET_SIZE = 1436
HEADER_SIZE = 4 + 1 + 1 + 1 + 1 + 16
VMPARAMSTRIP_SIZE = 174


@dataclass
class VbanRtPacket:
    """Represents the body of a VBAN RT data packet"""

    nbs: NBS
    _kind: KindMapClass
    _voicemeeterType: bytes  # data[28:29]
    _reserved: bytes  # data[29:30]
    _buffersize: bytes  # data[30:32]
    _voicemeeterVersion: bytes  # data[32:36]
    _optionBits: bytes  # data[36:40]
    _samplerate: bytes  # data[40:44]


@dataclass
class VbanRtPacketNBS0(VbanRtPacket):
    """Represents the body of a VBAN RT data packet with NBS 0"""

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

    def _generate_levels(self, levelarray) -> tuple:
        return tuple(
            int.from_bytes(levelarray[i : i + 2], 'little')
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
        return any(any(li) for li in (self._strip_comp, self._bus_comp))

    @property
    def voicemeetertype(self) -> str:
        """returns voicemeeter type as a string"""
        type_ = ('basic', 'banana', 'potato')
        return type_[int.from_bytes(self._voicemeeterType, 'little') - 1]

    @property
    def voicemeeterversion(self) -> tuple:
        """returns voicemeeter version as a tuple"""
        return tuple(
            reversed(
                tuple(
                    int.from_bytes(self._voicemeeterVersion[i : i + 1], 'little')
                    for i in range(4)
                )
            )
        )

    @property
    def samplerate(self) -> int:
        """returns samplerate as an int"""
        return int.from_bytes(self._samplerate, 'little')

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
    def striplabels(self) -> tuple:
        """returns tuple of strip labels"""
        return tuple(
            self._stripLabelUTF8c60[i : i + 60].decode().split('\x00')[0]
            for i in range(0, 480, 60)
        )

    @property
    def buslabels(self) -> tuple:
        """returns tuple of bus labels"""
        return tuple(
            self._busLabelUTF8c60[i : i + 60].decode().split('\x00')[0]
            for i in range(0, 480, 60)
        )


class Audibility(NamedTuple):
    knob: float
    comp: float
    gate: float
    denoiser: float


class Positions(NamedTuple):
    pan_x: float
    pan_y: float
    color_x: float
    color_y: float
    fx1: float
    fx2: float


class EqGains(NamedTuple):
    bass: float
    mid: float
    treble: float


class ParametricEQSettings(NamedTuple):
    on: bool
    type: int
    gain: float
    freq: float
    q: float


class Sends(NamedTuple):
    reverb: float
    delay: float
    fx1: float
    fx2: float


class CompressorSettings(NamedTuple):
    gain_in: float
    attack_ms: float
    release_ms: float
    n_knee: float
    ratio: float
    threshold: float
    c_enabled: bool
    makeup: bool
    gain_out: float


class GateSettings(NamedTuple):
    threshold_in: float
    damping_max: float
    bp_sidechain: bool
    attack_ms: float
    hold_ms: float
    release_ms: float


class DenoiserSettings(NamedTuple):
    threshold: float


class PitchSettings(NamedTuple):
    enabled: bool
    dry_wet: float
    value: float
    formant_lo: float
    formant_med: float
    formant_high: float


@dataclass
class VbanVMParamStrip:
    """Represents the VBAN_VMPARAMSTRIP_PACKET structure"""

    _mode: bytes  # long = 4 bytes data[0:4]
    _dblevel: bytes  # float = 4 bytes data[4:8]
    _audibility: bytes  # short = 2 bytes data[8:10]
    _pos3D_x: bytes  # short = 2 bytes data[10:12]
    _pos3D_y: bytes  # short = 2 bytes data[12:14]
    _posColor_x: bytes  # short = 2 bytes data[14:16]
    _posColor_y: bytes  # short = 2 bytes data[16:18]
    _EQgain1: bytes  # short = 2 bytes data[18:20]
    _EQgain2: bytes  # short = 2 bytes data[20:22]
    _EQgain3: bytes  # short = 2 bytes data[22:24]

    # First channel parametric EQ
    _PEQ_eqOn: bytes  # 6 * char = 6 bytes data[24:30]
    _PEQ_eqtype: bytes  # 6 * char = 6 bytes data[30:36]
    _PEQ_eqgain: bytes  # 6 * float = 24 bytes data[36:60]
    _PEQ_eqfreq: bytes  # 6 * float = 24 bytes data[60:84]
    _PEQ_eqq: bytes  # 6 * float = 24 bytes data[84:108]

    _audibility_c: bytes  # short = 2 bytes data[108:110]
    _audibility_g: bytes  # short = 2 bytes data[110:112]
    _audibility_d: bytes  # short = 2 bytes data[112:114]
    _posMod_x: bytes  # short = 2 bytes data[114:116]
    _posMod_y: bytes  # short = 2 bytes data[116:118]
    _send_reverb: bytes  # short = 2 bytes data[118:120]
    _send_delay: bytes  # short = 2 bytes data[120:122]
    _send_fx1: bytes  # short = 2 bytes data[122:124]
    _send_fx2: bytes  # short = 2 bytes data[124:126]
    _dblimit: bytes  # short = 2 bytes data[126:128]
    _nKaraoke: bytes  # short = 2 bytes data[128:130]

    _COMP_gain_in: bytes  # short = 2 bytes data[130:132]
    _COMP_attack_ms: bytes  # short = 2 bytes data[132:134]
    _COMP_release_ms: bytes  # short = 2 bytes data[134:136]
    _COMP_n_knee: bytes  # short = 2 bytes data[136:138]
    _COMP_comprate: bytes  # short = 2 bytes data[138:140]
    _COMP_threshold: bytes  # short = 2 bytes data[140:142]
    _COMP_c_enabled: bytes  # short = 2 bytes data[142:144]
    _COMP_c_auto: bytes  # short = 2 bytes data[144:146]
    _COMP_gain_out: bytes  # short = 2 bytes data[146:148]

    _GATE_dBThreshold_in: bytes  # short = 2 bytes data[148:150]
    _GATE_dBDamping_max: bytes  # short = 2 bytes data[150:152]
    _GATE_BP_Sidechain: bytes  # short = 2 bytes data[152:154]
    _GATE_attack_ms: bytes  # short = 2 bytes data[154:156]
    _GATE_hold_ms: bytes  # short = 2 bytes data[156:158]
    _GATE_release_ms: bytes  # short = 2 bytes data[158:160]

    _DenoiserThreshold: bytes  # short = 2 bytes data[160:162]
    _PitchEnabled: bytes  # short = 2 bytes data[162:164]
    _Pitch_DryWet: bytes  # short = 2 bytes data[164:166]
    _Pitch_Value: bytes  # short = 2 bytes data[166:168]
    _Pitch_formant_lo: bytes  # short = 2 bytes data[168:170]
    _Pitch_formant_med: bytes  # short = 2 bytes data[170:172]
    _Pitch_formant_high: bytes  # short = 2 bytes data[172:174]

    @classmethod
    def from_bytes(cls, data: bytes):
        return cls(
            _mode=data[0:4],
            _dblevel=data[4:8],
            _audibility=data[8:10],
            _pos3D_x=data[10:12],
            _pos3D_y=data[12:14],
            _posColor_x=data[14:16],
            _posColor_y=data[16:18],
            _EQgain1=data[18:20],
            _EQgain2=data[20:22],
            _EQgain3=data[22:24],
            _PEQ_eqOn=data[24:30],
            _PEQ_eqtype=data[30:36],
            _PEQ_eqgain=data[36:60],
            _PEQ_eqfreq=data[60:84],
            _PEQ_eqq=data[84:108],
            _audibility_c=data[108:110],
            _audibility_g=data[110:112],
            _audibility_d=data[112:114],
            _posMod_x=data[114:116],
            _posMod_y=data[116:118],
            _send_reverb=data[118:120],
            _send_delay=data[120:122],
            _send_fx1=data[122:124],
            _send_fx2=data[124:126],
            _dblimit=data[126:128],
            _nKaraoke=data[128:130],
            _COMP_gain_in=data[130:132],
            _COMP_attack_ms=data[132:134],
            _COMP_release_ms=data[134:136],
            _COMP_n_knee=data[136:138],
            _COMP_comprate=data[138:140],
            _COMP_threshold=data[140:142],
            _COMP_c_enabled=data[142:144],
            _COMP_c_auto=data[144:146],
            _COMP_gain_out=data[146:148],
            _GATE_dBThreshold_in=data[148:150],
            _GATE_dBDamping_max=data[150:152],
            _GATE_BP_Sidechain=data[152:154],
            _GATE_attack_ms=data[154:156],
            _GATE_hold_ms=data[156:158],
            _GATE_release_ms=data[158:160],
            _DenoiserThreshold=data[160:162],
            _PitchEnabled=data[162:164],
            _Pitch_DryWet=data[164:166],
            _Pitch_Value=data[166:168],
            _Pitch_formant_lo=data[168:170],
            _Pitch_formant_med=data[170:172],
            _Pitch_formant_high=data[172:174],
        )

    @property
    def mode(self) -> int:
        return int.from_bytes(self._mode, 'little')

    @property
    def audibility(self) -> Audibility:
        return Audibility(
            round(int.from_bytes(self._audibility, 'little', signed=True) * 0.01, 2),
            round(int.from_bytes(self._audibility_c, 'little', signed=True) * 0.01, 2),
            round(int.from_bytes(self._audibility_g, 'little', signed=True) * 0.01, 2),
            round(int.from_bytes(self._audibility_d, 'little', signed=True) * 0.01, 2),
        )

    @property
    def positions(self) -> Positions:
        return Positions(
            round(int.from_bytes(self._pos3D_x, 'little', signed=True) * 0.01, 2),
            round(int.from_bytes(self._pos3D_y, 'little', signed=True) * 0.01, 2),
            round(int.from_bytes(self._posColor_x, 'little', signed=True) * 0.01, 2),
            round(int.from_bytes(self._posColor_y, 'little', signed=True) * 0.01, 2),
            round(int.from_bytes(self._posMod_x, 'little', signed=True) * 0.01, 2),
            round(int.from_bytes(self._posMod_y, 'little', signed=True) * 0.01, 2),
        )

    @property
    def eqgains(self) -> EqGains:
        return EqGains(
            *[
                round(
                    int.from_bytes(getattr(self, f'_EQgain{i}'), 'little', signed=True)
                    * 0.01,
                    2,
                )
                for i in range(1, 4)
            ]
        )

    @property
    def parametric_eq(self) -> tuple[ParametricEQSettings, ...]:
        return tuple(
            ParametricEQSettings(
                on=bool(int.from_bytes(self._PEQ_eqOn[i : i + 1], 'little')),
                type=int.from_bytes(self._PEQ_eqtype[i : i + 1], 'little'),
                freq=struct.unpack('<f', self._PEQ_eqfreq[i * 4 : (i + 1) * 4])[0],
                gain=struct.unpack('<f', self._PEQ_eqgain[i * 4 : (i + 1) * 4])[0],
                q=struct.unpack('<f', self._PEQ_eqq[i * 4 : (i + 1) * 4])[0],
            )
            for i in range(6)
        )

    @property
    def sends(self) -> Sends:
        return Sends(
            round(int.from_bytes(self._send_reverb, 'little', signed=True) * 0.01, 2),
            round(int.from_bytes(self._send_delay, 'little', signed=True) * 0.01, 2),
            round(int.from_bytes(self._send_fx1, 'little', signed=True) * 0.01, 2),
            round(int.from_bytes(self._send_fx2, 'little', signed=True) * 0.01, 2),
        )

    @property
    def karaoke(self) -> int:
        return int.from_bytes(self._nKaraoke, 'little')

    @property
    def compressor(self) -> CompressorSettings:
        return CompressorSettings(
            gain_in=round(
                int.from_bytes(self._COMP_gain_in, 'little', signed=True) * 0.01, 2
            ),
            attack_ms=round(int.from_bytes(self._COMP_attack_ms, 'little') * 0.1, 2),
            release_ms=round(int.from_bytes(self._COMP_release_ms, 'little') * 0.1, 2),
            n_knee=round(int.from_bytes(self._COMP_n_knee, 'little') * 0.01, 2),
            ratio=round(int.from_bytes(self._COMP_comprate, 'little') * 0.01, 2),
            threshold=round(
                int.from_bytes(self._COMP_threshold, 'little', signed=True) * 0.01, 2
            ),
            c_enabled=bool(int.from_bytes(self._COMP_c_enabled, 'little')),
            makeup=bool(int.from_bytes(self._COMP_c_auto, 'little')),
            gain_out=round(
                int.from_bytes(self._COMP_gain_out, 'little', signed=True) * 0.01, 2
            ),
        )

    @property
    def gate(self) -> GateSettings:
        return GateSettings(
            threshold_in=round(
                int.from_bytes(self._GATE_dBThreshold_in, 'little', signed=True) * 0.01,
                2,
            ),
            damping_max=round(
                int.from_bytes(self._GATE_dBDamping_max, 'little', signed=True) * 0.01,
                2,
            ),
            bp_sidechain=round(
                int.from_bytes(self._GATE_BP_Sidechain, 'little') * 0.1, 2
            ),
            attack_ms=round(int.from_bytes(self._GATE_attack_ms, 'little') * 0.1, 2),
            hold_ms=round(int.from_bytes(self._GATE_hold_ms, 'little') * 0.1, 2),
            release_ms=round(int.from_bytes(self._GATE_release_ms, 'little') * 0.1, 2),
        )

    @property
    def denoiser(self) -> DenoiserSettings:
        return DenoiserSettings(
            threshold=round(
                int.from_bytes(self._DenoiserThreshold, 'little', signed=True) * 0.01, 2
            )
        )

    @property
    def pitch(self) -> PitchSettings:
        return PitchSettings(
            enabled=bool(int.from_bytes(self._PitchEnabled, 'little')),
            dry_wet=round(
                int.from_bytes(self._Pitch_DryWet, 'little', signed=True) * 0.01, 2
            ),
            value=round(
                int.from_bytes(self._Pitch_Value, 'little', signed=True) * 0.01, 2
            ),
            formant_lo=round(
                int.from_bytes(self._Pitch_formant_lo, 'little', signed=True) * 0.01, 2
            ),
            formant_med=round(
                int.from_bytes(self._Pitch_formant_med, 'little', signed=True) * 0.01, 2
            ),
            formant_high=round(
                int.from_bytes(self._Pitch_formant_high, 'little', signed=True) * 0.01,
                2,
            ),
        )


@dataclass
class VbanRtPacketNBS1(VbanRtPacket):
    """Represents the body of a VBAN RT data packet with NBS 1"""

    strips: tuple[VbanVMParamStrip, ...]

    @classmethod
    def from_bytes(
        cls,
        nbs: NBS,
        kind: KindMapClass,
        data: bytes,
    ):
        return cls(
            nbs=nbs,
            _kind=kind,
            _voicemeeterType=data[28:29],
            _reserved=data[29:30],
            _buffersize=data[30:32],
            _voicemeeterVersion=data[32:36],
            _optionBits=data[36:40],
            _samplerate=data[40:44],
            strips=tuple(
                VbanVMParamStrip.from_bytes(
                    data[44 + i * VMPARAMSTRIP_SIZE : 44 + (i + 1) * VMPARAMSTRIP_SIZE]
                )
                for i in range(16)
            ),
        )


@dataclass
class SubscribeHeader:
    """Represents the header of an RT subscription packet"""

    nbs: NBS = NBS.zero
    name: str = 'Register-RTP'
    timeout: int = 15

    @property
    def vban(self) -> bytes:
        return b'VBAN'

    @property
    def format_sr(self) -> bytes:
        return VBAN_PROTOCOL_SERVICE.to_bytes(1, 'little')

    @property
    def format_nbs(self) -> bytes:
        return (self.nbs.value & 0xFF).to_bytes(1, 'little')

    @property
    def format_nbc(self) -> bytes:
        return VBAN_SERVICE_RTPACKETREGISTER.to_bytes(1, 'little')

    @property
    def format_bit(self) -> bytes:
        return (self.timeout & 0xFF).to_bytes(1, 'little')

    @property
    def streamname(self) -> bytes:
        return self.name.encode('ascii') + bytes(16 - len(self.name))

    @classmethod
    def to_bytes(cls, nbs: NBS, framecounter: int) -> bytes:
        header = cls(nbs=nbs)

        data = bytearray()
        data.extend(header.vban)
        data.extend(header.format_sr)
        data.extend(header.format_nbs)
        data.extend(header.format_nbc)
        data.extend(header.format_bit)
        data.extend(header.streamname)
        data.extend(framecounter.to_bytes(4, 'little'))
        return bytes(data)


@dataclass
class VbanRtPacketHeader:
    """Represents the header of an RT response packet"""

    name: str = 'Voicemeeter-RTP'
    format_sr: int = VBAN_PROTOCOL_SERVICE
    format_nbs: int = 0
    format_nbc: int = VBAN_SERVICE_RTPACKET
    format_bit: int = 0

    @property
    def vban(self) -> bytes:
        return b'VBAN'

    @property
    def streamname(self) -> bytes:
        return self.name.encode('ascii') + bytes(16 - len(self.name))

    @classmethod
    def from_bytes(cls, data: bytes):
        if len(data) < HEADER_SIZE:
            raise ValueError('Data is too short to be a valid VbanRTPPacketHeader')

        name = data[8:24].rstrip(b'\x00').decode('utf-8')
        return cls(
            name=name,
            format_sr=data[4] & VBAN_SERVICE_MASK,
            format_nbs=data[5],
            format_nbc=data[6],
            format_bit=data[7],
        )


@dataclass
class RequestHeader:
    """Represents the header of an RT request packet"""

    name: str
    bps_index: int
    channel: int
    framecounter: int = 0

    @property
    def vban(self) -> bytes:
        return b'VBAN'

    @property
    def sr(self) -> bytes:
        return (VBAN_PROTOCOL_TXT + self.bps_index).to_bytes(1, 'little')

    @property
    def nbs(self) -> bytes:
        return (0).to_bytes(1, 'little')

    @property
    def nbc(self) -> bytes:
        return (self.channel).to_bytes(1, 'little')

    @property
    def bit(self) -> bytes:
        return (0x10).to_bytes(1, 'little')

    @property
    def streamname(self) -> bytes:
        return self.name.encode() + bytes(16 - len(self.name))

    @classmethod
    def to_bytes(
        cls, name: str, bps_index: int, channel: int, framecounter: int
    ) -> bytes:
        header = cls(
            name=name, bps_index=bps_index, channel=channel, framecounter=framecounter
        )

        data = bytearray()
        data.extend(header.vban)
        data.extend(header.sr)
        data.extend(header.nbs)
        data.extend(header.nbc)
        data.extend(header.bit)
        data.extend(header.streamname)
        data.extend(header.framecounter.to_bytes(4, 'little'))
        return bytes(data)
