from .errors import VMCMDErrors
from . import channel
from .channel import Channel
from . import kinds
from .meta import bus_output_prop

class OutputBus(Channel):
    """ Base class for output buses. """
    @classmethod
    def make(cls, is_physical, remote, index, *args, **kwargs):
        """
        Factory function for output busses.
        Returns a physical/virtual bus of a kind.
        """
        OutputBus = PhysicalOutputBus if is_physical else VirtualOutputBus
        OB_cls = type(f'Bus{remote.kind.name}', (OutputBus,), {
            'levels': BusLevel(remote, index),
        })
        return OB_cls(remote, index, *args, **kwargs)

    @property
    def identifier(self):
        return f'Bus[{self.index}]'

    @property
    def mute(self) -> bool:
        data = self.getter()
        return not int.from_bytes(data.busstate[self.index], 'little') & self._modes._mute == 0

    @mute.setter
    def mute(self, val: bool):
        if not isinstance(val, bool) and val not in (0,1):
            raise VMCMDErrors('mute is a boolean parameter')
        self.setter('mute', 1 if val else 0)

    @property
    def mono(self) -> bool:
        data = self.getter()
        return not int.from_bytes(data.busstate[self.index], 'little') & self._modes._mono == 0

    @mono.setter
    def mono(self, val: bool):
        if not isinstance(val, bool) and val not in (0,1):
            raise VMCMDErrors('mono is a boolean parameter')
        self.setter('mono', 1 if val else 0)

    @property
    def eq(self) -> bool:
        data = self.getter()
        return not int.from_bytes(data.busstate[self.index], 'little') & self._modes._eq == 0

    @eq.setter
    def eq(self, val: bool):
        if not isinstance(val, bool) and val not in (0,1):
            raise ('eq is a boolean parameter')
        self.setter('eq.On', 1 if val else 0)

    @property
    def eq_ab(self) -> bool:
        data = self.getter()
        return not int.from_bytes(data.busstate[self.index], 'little') & self._modes._eqb == 0

    @eq_ab.setter
    def eq_ab(self, val: bool):
        if not isinstance(val, bool) and val not in (0,1):
            raise VMCMDErrors('eq_ab is a boolean parameter')
        self.setter('eq.ab', 1 if val else 0)

    @property
    def label(self) -> str:
        data = self.getter()
        return data.buslabels[self.index]

    @label.setter
    def label(self, val: str):
        if not isinstance(val, str):
            raise VMCMDErrors('label is a string parameter')
        self.setter('Label', val)


class PhysicalOutputBus(OutputBus):
    @property
    def device(self) -> str:
        data = self.getter()
        return

    @property
    def sr(self) -> int:
        data = self.getter()
        return


class VirtualOutputBus(OutputBus):
    pass


class BusLevel(OutputBus):
    def __init__(self, remote, index):
        super().__init__(remote, index)
        self.level_map = _bus_maps[remote.kind.id]

    def getter_level(self, mode=None):
        def fget(data, i):
            return data.outputlevels[i]

        range_ = self.level_map[self.index]
        data = self._remote.get_rt()
        levels = tuple(fget(data, i) for i in range(*range_))
        return levels

    @property
    def all(self) -> tuple:
        return self.getter_level()

def _make_bus_level_map(kind):
    phys_out, virt_out = kind.outs
    return tuple((i, i+8) for i in range(0, (phys_out+virt_out)*8, 8))

_bus_maps = {kind.id: _make_bus_level_map(kind) for kind in kinds.all}
