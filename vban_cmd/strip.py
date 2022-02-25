from .errors import VMCMDErrors
from . import channel
from .channel import Channel
from . import kinds
from .meta import strip_output_prop

class InputStrip(Channel):
    """ Base class for input strips. """
    @classmethod
    def make(cls, is_physical, remote, index, **kwargs):
        """
        Factory function for input strips.
        Returns a physical/virtual strip of a kind.
        """
        PhysStrip, VirtStrip = _strip_pairs[remote.kind.id]
        InputStrip = PhysStrip if is_physical else VirtStrip
        IS_cls = type(f'Strip{remote.kind.name}', (InputStrip,), {
            'levels': StripLevel(remote, index),
        })
        return IS_cls(remote, index, **kwargs)

    @property
    def identifier(self):
        return f'Strip[{self.index}]'

    @property
    def mono(self) -> bool:
        data = self.getter()
        return not int.from_bytes(data.stripstate[self.index], 'little') & self._modes._mono == 0

    @mono.setter
    def mono(self, val: bool):
        if not isinstance(val, bool) and val not in (0,1):
            raise VMCMDErrors('mono is a boolean parameter')
        self.setter('mono', 1 if val else 0)

    @property
    def solo(self) -> bool:
        data = self.getter()
        return not int.from_bytes(data.stripstate[self.index], 'little') & self._modes._solo == 0

    @solo.setter
    def solo(self, val: bool):
        if not isinstance(val, bool) and val not in (0,1):
            raise VMCMDErrors('solo is a boolean parameter')
        self.setter('solo', 1 if val else 0)

    @property
    def mute(self) -> bool:
        data = self.getter()
        return not int.from_bytes(data.stripstate[self.index], 'little') & self._modes._mute == 0

    @mute.setter
    def mute(self, val: bool):
        if not isinstance(val, bool) and val not in (0,1):
            raise VMCMDErrors('mute is a boolean parameter')
        self.setter('mute', 1 if val else 0)

    @property
    def limit(self) -> int:
        data = self.getter()
        return

    @limit.setter
    def limit(self, val: int):
        if val not in range(-40,13):
            raise VMCMDErrors('Expected value from -40 to 12')
        self.setter('limit', val)

    @property
    def label(self) -> str:
        data = self.getter()
        return data.striplabels[self.index]

    @label.setter
    def label(self, val: str):
        if not isinstance(val, str):
            raise VMCMDErrors('label is a string parameter')
        self.setter('label', val)


class PhysicalInputStrip(InputStrip):
    @property
    def comp(self) -> float:
        data = self.getter()
        return

    @comp.setter
    def comp(self, val: float):
        self.setter('Comp', val)

    @property
    def gate(self) -> float:
        data = self.getter()
        return

    @gate.setter
    def gate(self, val: float):
        self.setter('gate', val)
        
    @property
    def device(self):
        data = self.getter()
        return

    @property
    def sr(self):
        data = self.getter()
        return


class VirtualInputStrip(InputStrip):
    @property
    def mc(self) -> bool:
        data = self.getter()
        return

    @mc.setter
    def mc(self, val: bool):
        if not isinstance(val, bool) and val not in (0,1):
            raise VMCMDErrors('mc is a boolean parameter')
        self.setter('mc', 1 if val else 0)
    mono = mc

    @property
    def k(self) -> int:
        data = self.getter()
        return

    @k.setter
    def k(self, val: int):
        if val not in range(5):
            raise VMCMDErrors('Expected value from 0 to 4')
        self.setter('karaoke', val)


class StripLevel(InputStrip):
    def __init__(self, remote, index):
        super().__init__(remote, index)
        self.level_map = _strip_maps[remote.kind.id]

    def getter_level(self, mode=None):
        def fget(data, i):
            return data.inputlevels[i]

        range_ = self.level_map[self.index]
        data = self._remote.get_rt()
        levels = tuple(fget(data, i) for i in range(*range_))
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


def _make_strip_mixin(kind):
    """ Creates a mixin with the kind's strip layout set as class variables. """
    num_A, num_B = kind.outs
    return type(f'StripMixin{kind.name}', (), {
    **{f'A{i}': strip_output_prop(f'A{i}') for i in range(1, num_A+1)},
    **{f'B{i}': strip_output_prop(f'B{i}') for i in range(1, num_B+1)}
    })

_strip_mixins = {kind.id: _make_strip_mixin(kind) for kind in kinds.all}

def _make_strip_pair(kind):
    """ Creates a PhysicalInputStrip and a VirtualInputStrip of a kind. """
    StripMixin = _strip_mixins[kind.id]
    PhysStrip = type(f'PhysicalInputStrip{kind.name}', (PhysicalInputStrip, StripMixin), {})
    VirtStrip = type(f'VirtualInputStrip{kind.name}', (VirtualInputStrip, StripMixin), {})
    return (PhysStrip, VirtStrip)

_strip_pairs = {kind.id: _make_strip_pair(kind) for kind in kinds.all}

def _make_strip_level_map(kind):
    phys_in, virt_in = kind.ins
    phys_map = tuple((i, i+2) for i in range(0, phys_in*2, 2))
    virt_map = tuple((i, i+8) for i in range(phys_in*2, phys_in*2+virt_in*8, 8))
    return phys_map+virt_map

_strip_maps  = {kind.id: _make_strip_level_map(kind) for kind in kinds.all}
