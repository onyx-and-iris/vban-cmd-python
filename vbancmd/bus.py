from .errors import VMCMDErrors
from . import channel
from .channel import Channel
from . import kinds
from .meta import bus_mode_prop, bus_bool_prop

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

    mute = bus_bool_prop('mute')

    mono = bus_bool_prop('mono')

    eq = bus_bool_prop('eq.On')

    eq_ab = bus_bool_prop('eq.ab')

    @property
    def label(self) -> str:
        val = self.getter('label')
        if val is None:
            val = self.public_packet.buslabels[self.index]
            self._remote.cache[f'{self.identifier}.label'] = [val, False]
        return val

    @label.setter
    def label(self, val: str):
        if not isinstance(val, str):
            raise VMCMDErrors('label is a string parameter')
        self.setter('label', val)

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
        val = self.getter('gain')
        if val is None:
            val = round((fget() * 0.01), 1)
            self._remote.cache[f'{self.identifier}.gain'] = [val, False]
        return round(val, 1)
        

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
