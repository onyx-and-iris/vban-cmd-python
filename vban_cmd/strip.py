import time
from abc import abstractmethod
from typing import Union

from .iremote import IRemote
from .kinds import kinds_all
from .meta import channel_bool_prop, channel_label_prop, strip_output_prop


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
        return f"Strip[{self.index}]"

    @property
    def limit(self) -> int:
        return

    @limit.setter
    def limit(self, val: int):
        self.setter("limit", val)

    @property
    def gain(self) -> float:
        val = self.getter("gain")
        if val is None:
            val = self.gainlayer[0].gain
        return round(val, 1)

    @gain.setter
    def gain(self, val: float):
        self.setter("gain", val)

    def fadeto(self, target: float, time_: int):
        self.setter("FadeTo", f"({target}, {time_})")
        time.sleep(self._remote.DELAY)

    def fadeby(self, change: float, time_: int):
        self.setter("FadeBy", f"({change}, {time_})")
        time.sleep(self._remote.DELAY)


class PhysicalStrip(Strip):
    def __str__(self):
        return f"{type(self).__name__}{self.index}"

    @property
    def comp(self) -> float:
        return

    @comp.setter
    def comp(self, val: float):
        self.setter("Comp", val)

    @property
    def gate(self) -> float:
        return

    @gate.setter
    def gate(self, val: float):
        self.setter("gate", val)

    @property
    def device(self):
        return

    @property
    def sr(self):
        return


class VirtualStrip(Strip):
    def __str__(self):
        return f"{type(self).__name__}{self.index}"

    mc = channel_bool_prop("mc")

    mono = mc

    @property
    def k(self) -> int:
        return

    @k.setter
    def k(self, val: int):
        self.setter("karaoke", val)

    def appgain(self, name: str, gain: float):
        self.setter("AppGain", f'("{name}", {gain})')

    def appmute(self, name: str, mute: bool = None):
        self.setter("AppMute", f'("{name}", {1 if mute else 0})')


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

        if self._remote.running and self._remote.event.ldirty:
            return tuple(
                fget(i)
                for i in self._remote.cache["strip_level"][
                    self.range[0] : self.range[-1]
                ]
            )
        return tuple(
            fget(i)
            for i in self._remote._get_levels(self.public_packet)[0][
                self.range[0] : self.range[-1]
            ]
        )

    @property
    def identifier(self) -> str:
        return f"Strip[{self.index}]"

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
        return f"Strip[{self.index}]"

    @property
    def gain(self) -> float:
        def fget():
            val = getattr(self.public_packet, f"stripgainlayer{self._i+1}")[self.index]
            if 0 <= val <= 1200:
                return val * 0.01
            return (((1 << 16) - 1) - val) * -0.01

        val = self.getter(f"GainLayer[{self._i}]")
        return round(val if val else fget(), 1)

    @gain.setter
    def gain(self, val: float):
        self.setter(f"GainLayer[{self._i}]", val)


def _make_gainlayer_mixin(remote, index):
    """Creates a GainLayer mixin"""
    return type(
        f"GainlayerMixin",
        (),
        {
            "gainlayer": tuple(
                GainLayer(remote, index, i) for i in range(remote.kind.num_bus)
            )
        },
    )


def _make_channelout_mixin(kind):
    """Creates a channel out property mixin"""
    return type(
        f"ChannelOutMixin{kind}",
        (),
        {
            **{
                f"A{i}": strip_output_prop(f"A{i}") for i in range(1, kind.phys_out + 1)
            },
            **{
                f"B{i}": strip_output_prop(f"B{i}") for i in range(1, kind.virt_out + 1)
            },
        },
    )


_make_channelout_mixins = {
    kind.name: _make_channelout_mixin(kind) for kind in kinds_all
}


def strip_factory(is_phys_strip, remote, i) -> Union[PhysicalStrip, VirtualStrip]:
    """
    Factory method for strips

    Mixes in required classes

    Returns a physical or virtual strip subclass
    """
    STRIP_cls = PhysicalStrip if is_phys_strip else VirtualStrip
    CHANNELOUTMIXIN_cls = _make_channelout_mixins[remote.kind.name]
    GAINLAYERMIXIN_cls = _make_gainlayer_mixin(remote, i)

    return type(
        f"{STRIP_cls.__name__}{remote.kind}",
        (STRIP_cls, CHANNELOUTMIXIN_cls, GAINLAYERMIXIN_cls),
        {
            "levels": StripLevel(remote, i),
            **{param: channel_bool_prop(param) for param in ["mono", "solo", "mute"]},
            "label": channel_label_prop(),
        },
    )(remote, i)


def request_strip_obj(is_phys_strip, remote, i) -> Strip:
    """
    Strip entry point. Wraps factory method.

    Returns a reference to a strip subclass of a kind
    """
    return strip_factory(is_phys_strip, remote, i)
