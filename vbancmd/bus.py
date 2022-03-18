from .errors import VMCMDErrors
from . import channel
from .channel import Channel
from . import kinds
from .meta import bus_mode_prop

class OutputBus(Channel):
    """ Base class for output buses. """
    @classmethod
    def make(cls, is_physical, remote, index, *args, **kwargs):
        """
        Factory function for output busses.
        Returns a physical/virtual bus of a kind.
        """
        BusModeMixin = _make_bus_mode_mixin(cls)
        OutputBus = PhysicalOutputBus if is_physical else VirtualOutputBus
        OB_cls = type(f'Bus{remote.kind.name}', (OutputBus,), {
            'levels': BusLevel(remote, index),
            'mode': BusModeMixin(remote, index),
        })
        return OB_cls(remote, index, *args, **kwargs)

    @property
    def identifier(self):
        return f'Bus[{self.index}]'

    @property
    def mute(self) -> bool:
        return not int.from_bytes(self.public_packet.busstate[self.index], 'little') & self._modes._mute == 0

    @mute.setter
    def mute(self, val: bool):
        if not isinstance(val, bool) and val not in (0,1):
            raise VMCMDErrors('mute is a boolean parameter')
        self.setter('mute', 1 if val else 0)

    @property
    def mono(self) -> bool:
        return not int.from_bytes(self.public_packet.busstate[self.index], 'little') & self._modes._mono == 0

    @mono.setter
    def mono(self, val: bool):
        if not isinstance(val, bool) and val not in (0,1):
            raise VMCMDErrors('mono is a boolean parameter')
        self.setter('mono', 1 if val else 0)

    @property
    def eq(self) -> bool:
        return not int.from_bytes(self.public_packet.busstate[self.index], 'little') & self._modes._eq == 0

    @eq.setter
    def eq(self, val: bool):
        if not isinstance(val, bool) and val not in (0,1):
            raise ('eq is a boolean parameter')
        self.setter('eq.On', 1 if val else 0)

    @property
    def eq_ab(self) -> bool:
        return not int.from_bytes(self.public_packet.busstate[self.index], 'little') & self._modes._eqb == 0

    @eq_ab.setter
    def eq_ab(self, val: bool):
        if not isinstance(val, bool) and val not in (0,1):
            raise VMCMDErrors('eq_ab is a boolean parameter')
        self.setter('eq.ab', 1 if val else 0)

    @property
    def label(self) -> str:
        return self.public_packet.buslabels[self.index]

    @label.setter
    def label(self, val: str):
        if not isinstance(val, str):
            raise VMCMDErrors('label is a string parameter')
        self.setter('Label', val)

    @property
    def gain(self) -> float:
        def fget():
            val = self.public_packet.busgain[self.index]
            if val < 10000:
                return -val
            elif val == ((1 << 16) - 1):
                return 0
            else:
                return ((1 << 16) - 1) - val
        return round((fget() * 0.01), 1)

    @gain.setter
    def gain(self, val: float):
        self.setter('gain', val)


class PhysicalOutputBus(OutputBus):
    @property
    def device(self) -> str:
        return

    @property
    def sr(self) -> int:
        return


class VirtualOutputBus(OutputBus):
    pass


class BusLevel(OutputBus):
    def __init__(self, remote, index):
        super().__init__(remote, index)
        self.level_map = _bus_maps[remote.kind.id]

    def getter_level(self, mode=None):
        def fget(i, data):
            val = data.outputlevels[i]
            return -val * 0.01

        range_ = self.level_map[self.index]
        data = self.public_packet
        levels = tuple(round(fget(i, data), 1) for i in range(*range_))
        return levels

    @property
    def all(self) -> tuple:
        return self.getter_level()

def _make_bus_level_map(kind):
    phys_out, virt_out = kind.outs
    return tuple((i, i+8) for i in range(0, (phys_out+virt_out)*8, 8))

_bus_maps = {kind.id: _make_bus_level_map(kind) for kind in kinds.all}

def _make_bus_mode_mixin(cls):
    """ Creates a mixin of Bus Modes. """
    return type('BusModeMixin', (cls,), {
        **{f'{mode.lower()}': bus_mode_prop(mode) for mode in
        ['normal', 'Amix', 'Bmix', 'Repeat', 'Composite', 'TVMix', 'UpMix21',
        'UpMix41', 'UpMix61', 'CenterOnly', 'LFEOnly', 'RearOnly']},
    })
