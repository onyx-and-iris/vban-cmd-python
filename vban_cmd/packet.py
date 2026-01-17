from dataclasses import dataclass

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
    def stripgainlayer1(self) -> tuple:
        return tuple(
            int.from_bytes(self._stripGaindB100Layer1[i : i + 2], 'little')
            for i in range(0, 16, 2)
        )

    @property
    def stripgainlayer2(self) -> tuple:
        return tuple(
            int.from_bytes(self._stripGaindB100Layer2[i : i + 2], 'little')
            for i in range(0, 16, 2)
        )

    @property
    def stripgainlayer3(self) -> tuple:
        return tuple(
            int.from_bytes(self._stripGaindB100Layer3[i : i + 2], 'little')
            for i in range(0, 16, 2)
        )

    @property
    def stripgainlayer4(self) -> tuple:
        return tuple(
            int.from_bytes(self._stripGaindB100Layer4[i : i + 2], 'little')
            for i in range(0, 16, 2)
        )

    @property
    def stripgainlayer5(self) -> tuple:
        return tuple(
            int.from_bytes(self._stripGaindB100Layer5[i : i + 2], 'little')
            for i in range(0, 16, 2)
        )

    @property
    def stripgainlayer6(self) -> tuple:
        return tuple(
            int.from_bytes(self._stripGaindB100Layer6[i : i + 2], 'little')
            for i in range(0, 16, 2)
        )

    @property
    def stripgainlayer7(self) -> tuple:
        return tuple(
            int.from_bytes(self._stripGaindB100Layer7[i : i + 2], 'little')
            for i in range(0, 16, 2)
        )

    @property
    def stripgainlayer8(self) -> tuple:
        return tuple(
            int.from_bytes(self._stripGaindB100Layer8[i : i + 2], 'little')
            for i in range(0, 16, 2)
        )

    @property
    def busgain(self) -> tuple:
        """returns tuple of bus gains"""
        return tuple(
            int.from_bytes(self._busGaindB100[i : i + 2], 'little')
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
    def eqgains(self) -> tuple[float, float, float]:
        return tuple(
            round(
                int.from_bytes(getattr(self, f'_EQgain{i}'), 'little', signed=True)
                * 0.01,
                2,
            )
            for i in range(1, 4)
        )

    @property
    def karaoke(self) -> int:
        return int.from_bytes(self._nKaraoke, 'little')


@dataclass
class VbanRtPacketNBS1(VbanRtPacket):
    """Represents the body of a VBAN RT data packet with NBS 1"""

    strips: tuple[VbanVMParamStrip, ...]


@dataclass
class SubscribeHeader:
    """Represents the header of an RT subscription packet"""

    ident: NBS = NBS.zero
    name = 'Register-RTP'
    timeout = 15
    vban: bytes = 'VBAN'.encode()
    format_sr: bytes = (VBAN_PROTOCOL_SERVICE).to_bytes(1, 'little')
    format_nbs: bytes = (ident.value & 0xFF).to_bytes(1, 'little')
    format_nbc: bytes = (VBAN_SERVICE_RTPACKETREGISTER).to_bytes(1, 'little')
    format_bit: bytes = (timeout & 0xFF).to_bytes(1, 'little')  # timeout
    streamname: bytes = name.encode('ascii') + bytes(16 - len(name))

    @classmethod
    def to_bytes(cls, nbs: NBS, framecounter: int) -> bytes:
        header = cls(ident=nbs)
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
    vban: bytes = 'VBAN'.encode()
    format_sr: bytes = (VBAN_PROTOCOL_SERVICE).to_bytes(1, 'little')
    format_nbs: bytes = (0).to_bytes(1, 'little')
    format_nbc: bytes = (VBAN_SERVICE_RTPACKET).to_bytes(1, 'little')
    format_bit: bytes = (0).to_bytes(1, 'little')
    streamname: bytes = name.encode('ascii') + bytes(16 - len(name))

    @classmethod
    def from_bytes(cls, data: bytes):
        if len(data) < HEADER_SIZE:
            raise ValueError('Data is too short to be a valid VbanRTPPacketHeader')
        vban = data[0:4]
        format_sr = data[4]
        format_nbs = data[5]
        format_nbc = data[6]
        format_bit = data[7]
        name = data[8:24].rstrip(b'\x00').decode('utf-8')
        return cls(
            name=name,
            vban=vban,
            format_sr=format_sr & VBAN_SERVICE_MASK,
            format_nbs=format_nbs,
            format_nbc=format_nbc,
            format_bit=format_bit,
        )


@dataclass
class RequestHeader:
    """Represents the header of an RT request packet"""

    name: str
    bps_index: int
    channel: int
    vban: bytes = 'VBAN'.encode()
    nbs: bytes = (0).to_bytes(1, 'little')
    bit: bytes = (0x10).to_bytes(1, 'little')
    framecounter: bytes = (0).to_bytes(4, 'little')

    @property
    def sr(self):
        return (VBAN_PROTOCOL_TXT + self.bps_index).to_bytes(1, 'little')

    @property
    def nbc(self):
        return (self.channel).to_bytes(1, 'little')

    @property
    def streamname(self):
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
