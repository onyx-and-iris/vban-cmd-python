from .errors import VMCMDErrors
from . import channel
from .channel import Channel
from . import kinds
from .meta import strip_output_prop, strip_bool_prop


class InputStrip(Channel):
    """Base class for input strips."""

    @classmethod
    def make(cls, is_physical, remote, index, **kwargs):
        """
        Factory function for input strips.
        Returns a physical/virtual strip of a kind.
        """
        PhysStrip, VirtStrip = _strip_pairs[remote.kind.id]
        InputStrip = PhysStrip if is_physical else VirtStrip
        GainLayerMixin = _make_gainlayer_mixin(remote, index)
        IS_cls = type(
            f"Strip{remote.kind.name}",
            (InputStrip, GainLayerMixin),
            {
                "levels": StripLevel(remote, index),
            },
        )
        return IS_cls(remote, index, **kwargs)

    @property
    def identifier(self):
        return f"Strip[{self.index}]"

    mono = strip_bool_prop("mono")

    solo = strip_bool_prop("solo")

    mute = strip_bool_prop("mute")

    @property
    def limit(self) -> int:
        return

    @limit.setter
    def limit(self, val: int):
        self.setter("limit", val)

    @property
    def label(self) -> str:
        val = self.getter("label")
        if val is None:
            val = self.public_packet.striplabels[self.index]
            self._remote.cache[f"{self.identifier}.label"] = [val, False]
        return val

    @label.setter
    def label(self, val: str):
        if not isinstance(val, str):
            raise VMCMDErrors("label is a string parameter")
        self.setter("label", val)

    @property
    def gain(self) -> float:
        val = self.getter("GainLayer[0]")
        if val is None:
            val = self.gainlayer[0].gain
            self._remote.cache[f"{self.identifier}.GainLayer[0]"] = [val, False]
        return round(val, 1)

    @gain.setter
    def gain(self, val: float):
        self.setter("gain", val)


class PhysicalInputStrip(InputStrip):
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


class VirtualInputStrip(InputStrip):
    @property
    def mc(self) -> bool:
        return

    @mc.setter
    def mc(self, val: bool):
        if not isinstance(val, bool) and val not in (0, 1):
            raise VMCMDErrors("mc is a boolean parameter")
        self.setter("mc", 1 if val else 0)

    mono = mc

    @property
    def k(self) -> int:
        return

    @k.setter
    def k(self, val: int):
        self.setter("karaoke", val)


class StripLevel(InputStrip):
    def __init__(self, remote, index):
        super().__init__(remote, index)
        self.level_map = _strip_maps[remote.kind.id]

    def getter_level(self, mode=None):
        def fget(i, data):
            val = data.inputlevels[i]
            return -val * 0.01

        range_ = self.level_map[self.index]
        data = self.public_packet
        levels = tuple(round(fget(i, data), 1) for i in range(*range_))
        return levels

    @property
    def prefader(self) -> tuple:
        return self.getter_level()

    @property
    def postfader(self) -> tuple:
        return

    @property
    def postmute(self) -> tuple:
        return


class GainLayer(InputStrip):
    def __init__(self, remote, index, i):
        super().__init__(remote, index)
        self._i = i

    @property
    def gain(self) -> float:
        def fget():
            val = getattr(self.public_packet, f"stripgainlayer{self._i+1}")[self.index]
            if val < 10000:
                return -val
            elif val == ((1 << 16) - 1):
                return 0
            else:
                return ((1 << 16) - 1) - val

        val = self.getter(f"GainLayer[{self._i}]")
        if val is None:
            val = round((fget() * 0.01), 1)
            self._remote.cache[f"{self.identifier}.GainLayer[{self._i}]"] = [val, False]
            return val
        return round(val, 1)

    @gain.setter
    def gain(self, val: float):
        self.setter(f"GainLayer[{self._i}]", val)


def _make_gainlayer_mixin(remote, index):
    """Creates a GainLayer mixin"""
    return type(
        f"GainlayerMixin",
        (),
        {"gainlayer": tuple(GainLayer(remote, index, i) for i in range(8))},
    )


def _make_strip_mixin(kind):
    """Creates a mixin with the kind's strip layout set as class variables."""
    num_A, num_B = kind.outs
    return type(
        f"StripMixin{kind.name}",
        (),
        {
            **{f"A{i}": strip_output_prop(f"A{i}") for i in range(1, num_A + 1)},
            **{f"B{i}": strip_output_prop(f"B{i}") for i in range(1, num_B + 1)},
        },
    )


_strip_mixins = {kind.id: _make_strip_mixin(kind) for kind in kinds.all}


def _make_strip_pair(kind):
    """Creates a PhysicalInputStrip and a VirtualInputStrip of a kind."""
    StripMixin = _strip_mixins[kind.id]
    PhysStrip = type(
        f"PhysicalInputStrip{kind.name}", (PhysicalInputStrip, StripMixin), {}
    )
    VirtStrip = type(
        f"VirtualInputStrip{kind.name}", (VirtualInputStrip, StripMixin), {}
    )
    return (PhysStrip, VirtStrip)


_strip_pairs = {kind.id: _make_strip_pair(kind) for kind in kinds.all}


def _make_strip_level_map(kind):
    phys_in, virt_in = kind.ins
    phys_map = tuple((i, i + 2) for i in range(0, phys_in * 2, 2))
    virt_map = tuple(
        (i, i + 8) for i in range(phys_in * 2, phys_in * 2 + virt_in * 8, 8)
    )
    return phys_map + virt_map


_strip_maps = {kind.id: _make_strip_level_map(kind) for kind in kinds.all}
