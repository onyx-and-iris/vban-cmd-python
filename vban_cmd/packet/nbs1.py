import struct
from dataclasses import dataclass
from functools import cached_property
from typing import NamedTuple

from vban_cmd.enums import NBS
from vban_cmd.kinds import KindMapClass

from .headers import VbanRTPacket

VMPARAMSTRIP_SIZE = 174


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

    _mode: bytes
    _dblevel: bytes
    _audibility: bytes
    _pos3D_x: bytes
    _pos3D_y: bytes
    _posColor_x: bytes
    _posColor_y: bytes
    _EQgain1: bytes
    _EQgain2: bytes
    _EQgain3: bytes

    # First channel parametric EQ
    _PEQ_eqOn: bytes
    _PEQ_eqtype: bytes
    _PEQ_eqgain: bytes
    _PEQ_eqfreq: bytes
    _PEQ_eqq: bytes

    _audibility_c: bytes
    _audibility_g: bytes
    _audibility_d: bytes
    _posMod_x: bytes
    _posMod_y: bytes
    _send_reverb: bytes
    _send_delay: bytes
    _send_fx1: bytes
    _send_fx2: bytes
    _dblimit: bytes
    _nKaraoke: bytes

    _COMP_gain_in: bytes
    _COMP_attack_ms: bytes
    _COMP_release_ms: bytes
    _COMP_n_knee: bytes
    _COMP_comprate: bytes
    _COMP_threshold: bytes
    _COMP_c_enabled: bytes
    _COMP_c_auto: bytes
    _COMP_gain_out: bytes

    _GATE_dBThreshold_in: bytes
    _GATE_dBDamping_max: bytes
    _GATE_BP_Sidechain: bytes
    _GATE_attack_ms: bytes
    _GATE_hold_ms: bytes
    _GATE_release_ms: bytes

    _DenoiserThreshold: bytes
    _PitchEnabled: bytes
    _Pitch_DryWet: bytes
    _Pitch_Value: bytes
    _Pitch_formant_lo: bytes
    _Pitch_formant_med: bytes
    _Pitch_formant_high: bytes

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

    @cached_property
    def mode(self) -> int:
        return int.from_bytes(self._mode, 'little')

    @cached_property
    def karaoke(self) -> int:
        return int.from_bytes(self._nKaraoke, 'little')

    @cached_property
    def audibility(self) -> Audibility:
        return Audibility(
            round(int.from_bytes(self._audibility, 'little', signed=True) * 0.01, 2),
            round(int.from_bytes(self._audibility_c, 'little', signed=True) * 0.01, 2),
            round(int.from_bytes(self._audibility_g, 'little', signed=True) * 0.01, 2),
            round(int.from_bytes(self._audibility_d, 'little', signed=True) * 0.01, 2),
        )

    @cached_property
    def positions(self) -> Positions:
        return Positions(
            round(int.from_bytes(self._pos3D_x, 'little', signed=True) * 0.01, 2),
            round(int.from_bytes(self._pos3D_y, 'little', signed=True) * 0.01, 2),
            round(int.from_bytes(self._posColor_x, 'little', signed=True) * 0.01, 2),
            round(int.from_bytes(self._posColor_y, 'little', signed=True) * 0.01, 2),
            round(int.from_bytes(self._posMod_x, 'little', signed=True) * 0.01, 2),
            round(int.from_bytes(self._posMod_y, 'little', signed=True) * 0.01, 2),
        )

    @cached_property
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

    @cached_property
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

    @cached_property
    def sends(self) -> Sends:
        return Sends(
            round(int.from_bytes(self._send_reverb, 'little', signed=True) * 0.01, 2),
            round(int.from_bytes(self._send_delay, 'little', signed=True) * 0.01, 2),
            round(int.from_bytes(self._send_fx1, 'little', signed=True) * 0.01, 2),
            round(int.from_bytes(self._send_fx2, 'little', signed=True) * 0.01, 2),
        )

    @cached_property
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

    @cached_property
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

    @cached_property
    def denoiser(self) -> DenoiserSettings:
        return DenoiserSettings(
            threshold=round(
                int.from_bytes(self._DenoiserThreshold, 'little', signed=True) * 0.01, 2
            )
        )

    @cached_property
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
class VbanRTPacketNBS1(VbanRTPacket):
    """Represents the body of a VBAN RTPacket with ident:1"""

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
