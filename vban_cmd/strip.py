import time
from abc import abstractmethod
from typing import Union

from . import kinds
from .enums import NBS
from .iremote import IRemote
from .meta import (
    channel_bool_prop,
    channel_label_prop,
    send_prop,
    strip_output_prop,
    xy_prop,
)


class Strip(IRemote):
    """
    Implements the common interface

    Defines concrete implementation for strip
    """

    @abstractmethod
    def __str__(self):
        pass

    @property
    def identifier(self) -> str:
        return f'strip[{self.index}]'

    @property
    def limit(self) -> int:
        return

    @limit.setter
    def limit(self, val: int):
        self.setter('limit', val)

    @property
    def gain(self) -> float:
        val = self.getter('gain')
        if val is None:
            val = max(layer.gain for layer in self.gainlayer)
        return round(val, 1)

    @gain.setter
    def gain(self, val: float):
        self.setter('gain', val)

    def fadeto(self, target: float, time_: int):
        self.setter('FadeTo', f'({target}, {time_})')
        time.sleep(self._remote.DELAY)

    def fadeby(self, change: float, time_: int):
        self.setter('FadeBy', f'({change}, {time_})')
        time.sleep(self._remote.DELAY)


class PhysicalStrip(Strip):
    @classmethod
    def make(cls, remote, index, is_phys):
        EFFECTS_cls = _make_effects_mixins(is_phys)[remote.kind.name]
        return type(
            f'PhysicalStrip{remote.kind}',
            (cls, EFFECTS_cls),
            {
                'comp': StripComp(remote, index),
                'gate': StripGate(remote, index),
                'denoiser': StripDenoiser(remote, index),
                'eq': StripEQ.make(remote, index),
            },
        )

    def __str__(self):
        return f'{type(self).__name__}{self.index}'

    @property
    def audibility(self) -> float:
        if self.public_packets[NBS.one] is None:
            return 0.0
        return self.public_packets[NBS.one].strips[self.index].audibility.knob

    @audibility.setter
    def audibility(self, val: float):
        self.setter('audibility', val)


class StripComp(IRemote):
    @property
    def identifier(self) -> str:
        return f'strip[{self.index}].comp'

    @property
    def knob(self) -> float:
        if self.public_packets[NBS.one] is None:
            return 0.0
        return self.public_packets[NBS.one].strips[self.index].audibility.comp

    @knob.setter
    def knob(self, val: float):
        self.setter('', val)

    @property
    def gainin(self) -> float:
        if self.public_packets[NBS.one] is None:
            return 0.0
        return self.public_packets[NBS.one].strips[self.index].compressor.gain_in

    @gainin.setter
    def gainin(self, val: float):
        self.setter('GainIn', val)

    @property
    def ratio(self) -> float:
        if self.public_packets[NBS.one] is None:
            return 0.0
        return self.public_packets[NBS.one].strips[self.index].compressor.ratio

    @ratio.setter
    def ratio(self, val: float):
        self.setter('Ratio', val)

    @property
    def threshold(self) -> float:
        if self.public_packets[NBS.one] is None:
            return 0.0
        return self.public_packets[NBS.one].strips[self.index].compressor.threshold

    @threshold.setter
    def threshold(self, val: float):
        self.setter('Threshold', val)

    @property
    def attack(self) -> float:
        if self.public_packets[NBS.one] is None:
            return 0.0
        return self.public_packets[NBS.one].strips[self.index].compressor.attack_ms

    @attack.setter
    def attack(self, val: float):
        self.setter('Attack', val)

    @property
    def release(self) -> float:
        if self.public_packets[NBS.one] is None:
            return 0.0
        return self.public_packets[NBS.one].strips[self.index].compressor.release_ms

    @release.setter
    def release(self, val: float):
        self.setter('Release', val)

    @property
    def knee(self) -> float:
        if self.public_packets[NBS.one] is None:
            return 0.0
        return self.public_packets[NBS.one].strips[self.index].compressor.n_knee

    @knee.setter
    def knee(self, val: float):
        self.setter('Knee', val)

    @property
    def gainout(self) -> float:
        if self.public_packets[NBS.one] is None:
            return 0.0
        return self.public_packets[NBS.one].strips[self.index].compressor.gain_out

    @gainout.setter
    def gainout(self, val: float):
        self.setter('GainOut', val)

    @property
    def makeup(self) -> bool:
        if self.public_packets[NBS.one] is None:
            return False
        return bool(self.public_packets[NBS.one].strips[self.index].compressor.makeup)

    @makeup.setter
    def makeup(self, val: bool):
        self.setter('makeup', 1 if val else 0)


class StripGate(IRemote):
    @property
    def identifier(self) -> str:
        return f'strip[{self.index}].gate'

    @property
    def knob(self) -> float:
        if self.public_packets[NBS.one] is None:
            return 0.0
        return self.public_packets[NBS.one].strips[self.index].audibility.gate

    @knob.setter
    def knob(self, val: float):
        self.setter('', val)

    @property
    def threshold(self) -> float:
        if self.public_packets[NBS.one] is None:
            return 0.0
        return self.public_packets[NBS.one].strips[self.index].gate.threshold_in

    @threshold.setter
    def threshold(self, val: float):
        self.setter('Threshold', val)

    @property
    def damping(self) -> float:
        if self.public_packets[NBS.one] is None:
            return 0.0
        return self.public_packets[NBS.one].strips[self.index].gate.damping_max

    @damping.setter
    def damping(self, val: float):
        self.setter('Damping', val)

    @property
    def bpsidechain(self) -> int:
        if self.public_packets[NBS.one] is None:
            return 0
        return self.public_packets[NBS.one].strips[self.index].gate.bp_sidechain

    @bpsidechain.setter
    def bpsidechain(self, val: int):
        self.setter('BPSidechain', val)

    @property
    def attack(self) -> float:
        if self.public_packets[NBS.one] is None:
            return 0.0
        return self.public_packets[NBS.one].strips[self.index].gate.attack_ms

    @attack.setter
    def attack(self, val: float):
        self.setter('Attack', val)

    @property
    def hold(self) -> float:
        if self.public_packets[NBS.one] is None:
            return 0.0
        return self.public_packets[NBS.one].strips[self.index].gate.hold_ms

    @hold.setter
    def hold(self, val: float):
        self.setter('Hold', val)

    @property
    def release(self) -> float:
        if self.public_packets[NBS.one] is None:
            return 0.0
        return self.public_packets[NBS.one].strips[self.index].gate.release_ms

    @release.setter
    def release(self, val: float):
        self.setter('Release', val)


class StripDenoiser(IRemote):
    @property
    def identifier(self) -> str:
        return f'strip[{self.index}].denoiser'

    @property
    def knob(self) -> float:
        if self.public_packets[NBS.one] is None:
            return 0.0
        return self.public_packets[NBS.one].strips[self.index].audibility.denoiser

    @knob.setter
    def knob(self, val: float):
        self.setter('', val)


class StripEQ(IRemote):
    @classmethod
    def make(cls, remote, i):
        """
        Factory method for Strip EQ.

        Returns a StripEQ class.
        """
        STRIPEQ_cls = type(
            'StripEQ',
            (cls,),
            {
                'channel': tuple(
                    StripEQCh.make(remote, i, j)
                    for j in range(remote.kind.strip_channels)
                )
            },
        )
        return STRIPEQ_cls(remote, i)

    @property
    def identifier(self) -> str:
        return f'strip[{self.index}].eq'

    @property
    def on(self):
        return

    @on.setter
    def on(self, val: bool):
        self.setter('on', 1 if val else 0)

    @property
    def ab(self):
        return

    @ab.setter
    def ab(self, val: bool):
        self.setter('ab', 1 if val else 0)


class StripEQCh(IRemote):
    @classmethod
    def make(cls, remote, i, j):
        """
        Factory method for Strip EQ channel.

        Returns a StripEQCh class.
        """
        StripEQCh_cls = type(
            'StripEQCh',
            (cls,),
            {
                'cell': tuple(
                    StripEQChCell(remote, i, j, k) for k in range(remote.kind.cells)
                )
            },
        )
        return StripEQCh_cls(remote, i, j)

    def __init__(self, remote, i, j):
        super().__init__(remote, i)
        self.channel_index = j

    @property
    def identifier(self) -> str:
        return f'Strip[{self.index}].eq.channel[{self.channel_index}]'


class StripEQChCell(IRemote):
    def __init__(self, remote, i, j, k):
        super().__init__(remote, i)
        self.channel_index = j
        self.cell_index = k

    @property
    def identifier(self) -> str:
        return f'Strip[{self.index}].eq.channel[{self.channel_index}].cell[{self.cell_index}]'

    @property
    def on(self) -> bool:
        if self.channel_index > 0:
            self.logger.warning(
                'Only channel 0 is supported over VBAN for Strip EQ cells'
            )
        if self.public_packets[NBS.one] is None:
            return False
        return (
            self.public_packets[NBS.one]
            .strips[self.index]
            .parametric_eq[self.cell_index]
            .on
        )

    @on.setter
    def on(self, val: bool):
        self.setter('on', 1 if val else 0)

    @property
    def type(self) -> int:
        if self.channel_index > 0:
            self.logger.warning(
                'Only channel 0 is supported over VBAN for Strip EQ cells'
            )
        if self.public_packets[NBS.one] is None:
            return 0
        return (
            self.public_packets[NBS.one]
            .strips[self.index]
            .parametric_eq[self.cell_index]
            .type
        )

    @type.setter
    def type(self, val: int):
        self.setter('type', val)

    @property
    def f(self) -> float:
        if self.channel_index > 0:
            self.logger.warning(
                'Only channel 0 is supported over VBAN for Strip EQ cells'
            )
        if self.public_packets[NBS.one] is None:
            return 0.0
        return (
            self.public_packets[NBS.one]
            .strips[self.index]
            .parametric_eq[self.cell_index]
            .freq
        )

    @f.setter
    def f(self, val: float):
        self.setter('f', val)

    @property
    def gain(self) -> float:
        if self.channel_index > 0:
            self.logger.warning(
                'Only channel 0 is supported over VBAN for Strip EQ cells'
            )
        if self.public_packets[NBS.one] is None:
            return 0.0
        return (
            self.public_packets[NBS.one]
            .strips[self.index]
            .parametric_eq[self.cell_index]
            .gain
        )

    @gain.setter
    def gain(self, val: float):
        self.setter('gain', val)

    @property
    def q(self) -> float:
        if self.channel_index > 0:
            self.logger.warning(
                'Only channel 0 is supported over VBAN for Strip EQ cells'
            )
        if self.public_packets[NBS.one] is None:
            return 0.0
        return (
            self.public_packets[NBS.one]
            .strips[self.index]
            .parametric_eq[self.cell_index]
            .q
        )

    @q.setter
    def q(self, val: float):
        self.setter('q', val)


class VirtualStrip(Strip):
    @classmethod
    def make(cls, remote, i, is_phys):
        """
        Factory method for VirtualStrip.

        Returns a VirtualStrip class.
        """
        EFFECTS_cls = _make_effects_mixins(is_phys)[remote.kind.name]
        return type(
            'VirtualStrip',
            (cls, EFFECTS_cls),
            {},
        )

    def __str__(self):
        return f'{type(self).__name__}{self.index}'

    mc = channel_bool_prop('mc')

    mono = mc

    @property
    def k(self) -> int:
        if self.public_packets[NBS.one] is None:
            return 0
        return self.public_packets[NBS.one].strips[self.index].karaoke

    @k.setter
    def k(self, val: int):
        self.setter('karaoke', val)

    @property
    def bass(self) -> float:
        if self.public_packets[NBS.one] is None:
            return 0.0
        return self.public_packets[NBS.one].strips[self.index].eqgains.bass

    @bass.setter
    def bass(self, val: float):
        self.setter('EQGain1', val)

    @property
    def mid(self) -> float:
        if self.public_packets[NBS.one] is None:
            return 0.0
        return self.public_packets[NBS.one].strips[self.index].eqgains.mid

    @mid.setter
    def mid(self, val: float):
        self.setter('EQGain2', val)

    med = mid

    @property
    def treble(self) -> float:
        if self.public_packets[NBS.one] is None:
            return 0.0
        return self.public_packets[NBS.one].strips[self.index].eqgains.treble

    @treble.setter
    def treble(self, val: float):
        self.setter('EQGain3', val)

    high = treble

    def appgain(self, name: str, gain: float):
        self.setter('AppGain', f'("{name}", {gain})')

    def appmute(self, name: str, mute: bool = None):
        self.setter('AppMute', f'("{name}", {1 if mute else 0})')


class StripLevel(IRemote):
    def __init__(self, remote, index):
        super().__init__(remote, index)
        phys_map = tuple((i, i + 2) for i in range(0, remote.kind.phys_in * 2, 2))
        virt_map = tuple(
            (i, i + 8)
            for i in range(
                remote.kind.phys_in * 2,
                remote.kind.phys_in * 2 + remote.kind.virt_in * 8,
                8,
            )
        )
        self.level_map = phys_map + virt_map
        self.range = self.level_map[self.index]

    def getter(self):
        """Returns a tuple of level values for the channel."""

        def fget(i):
            return round((((1 << 16) - 1) - i) * -0.01, 1)

        if not self._remote.stopped() and self._remote.event.ldirty:
            return tuple(
                fget(i)
                for i in self._remote.cache['strip_level'][
                    self.range[0] : self.range[-1]
                ]
            )
        return tuple(
            fget(i)
            for i in self._remote._get_levels(self.public_packets[NBS.zero])[0][
                self.range[0] : self.range[-1]
            ]
        )

    @property
    def identifier(self) -> str:
        return f'strip[{self.index}]'

    @property
    def prefader(self) -> tuple:
        return self.getter()

    @property
    def postfader(self) -> tuple:
        return

    @property
    def postmute(self) -> tuple:
        return

    @property
    def isdirty(self) -> bool:
        """
        Returns dirty status for this specific channel.

        Expected to be used in a callback only.
        """
        return any(self._remote._strip_comp[self.range[0] : self.range[-1]])

    is_updated = isdirty


class GainLayer(IRemote):
    def __init__(self, remote, index, i):
        super().__init__(remote, index)
        self._i = i

    @property
    def identifier(self) -> str:
        return f'strip[{self.index}]'

    @property
    def gain(self) -> float:
        val = self.getter(f'GainLayer[{self._i}]')
        if val:
            return round(val, 2)
        else:
            return self.public_packets[NBS.zero].gainlayers[self._i][self.index]

    @gain.setter
    def gain(self, val: float):
        self.setter(f'GainLayer[{self._i}]', val)


def _make_gainlayer_mixin(remote, index):
    """Creates a GainLayer mixin"""
    return type(
        'GainlayerMixin',
        (),
        {
            'gainlayer': tuple(
                GainLayer(remote, index, i) for i in range(remote.kind.num_bus)
            )
        },
    )


def _make_channelout_mixin(kind):
    """Creates a channel out property mixin"""
    return type(
        f'ChannelOutMixin{kind}',
        (),
        {
            **{
                f'A{i}': strip_output_prop(f'A{i}') for i in range(1, kind.phys_out + 1)
            },
            **{
                f'B{i}': strip_output_prop(f'B{i}') for i in range(1, kind.virt_out + 1)
            },
        },
    )


_make_channelout_mixins = {
    kind.name: _make_channelout_mixin(kind) for kind in kinds.all
}


def _make_effects_mixin(kind, is_phys):
    """creates an effects mixin for a kind"""

    def _make_xy_cls():
        pan = {param: xy_prop(param) for param in ['pan_x', 'pan_y']}
        color = {param: xy_prop(param) for param in ['color_x', 'color_y']}
        fx = {param: xy_prop(param) for param in ['fx_x', 'fx_y']}
        if is_phys:
            return type(
                'XYPhys',
                (),
                {
                    **pan,
                    **color,
                    **fx,
                },
            )
        return type(
            'XYVirt',
            (),
            {**pan},
        )

    def _make_sends_cls():
        if is_phys:
            return type(
                'FX',
                (),
                {
                    **{
                        param: send_prop(param)
                        for param in ['reverb', 'delay', 'fx1', 'fx2']
                    },
                    # **{
                    #    f'post{param}': bool_prop(f'post{param}')
                    #    for param in ['reverb', 'delay', 'fx1', 'fx2']
                    # },
                },
            )
        return type('FX', (), {})

    if kind.name == 'basic':
        steps = (_make_xy_cls,)
    elif kind.name == 'banana':
        steps = (_make_xy_cls,)
    elif kind.name == 'potato':
        steps = (_make_xy_cls, _make_sends_cls)
    return type(f'Effects{kind}', tuple(step() for step in steps), {})


def _make_effects_mixins(is_phys):
    return {kind.name: _make_effects_mixin(kind, is_phys) for kind in kinds.all}


def strip_factory(is_phys_strip, remote, i) -> Union[PhysicalStrip, VirtualStrip]:
    """
    Factory method for strips

    Mixes in required classes

    Returns a physical or virtual strip subclass
    """
    STRIP_cls = (
        PhysicalStrip.make(remote, i, is_phys_strip)
        if is_phys_strip
        else VirtualStrip.make(remote, i, is_phys_strip)
    )
    CHANNELOUTMIXIN_cls = _make_channelout_mixins[remote.kind.name]
    GAINLAYERMIXIN_cls = _make_gainlayer_mixin(remote, i)

    return type(
        f'{STRIP_cls.__name__}{remote.kind}',
        (STRIP_cls, CHANNELOUTMIXIN_cls, GAINLAYERMIXIN_cls),
        {
            'levels': StripLevel(remote, i),
            **{param: channel_bool_prop(param) for param in ['mono', 'solo', 'mute']},
            'label': channel_label_prop(),
        },
    )(remote, i)


def request_strip_obj(is_phys_strip, remote, i) -> Strip:
    """
    Strip entry point. Wraps factory method.

    Returns a reference to a strip subclass of a kind
    """
    return strip_factory(is_phys_strip, remote, i)
