import abc
import time
from typing import Union

from .enums import NBS, BusModes
from .iremote import IRemote
from .meta import bus_mode_prop, channel_bool_prop, channel_int_prop, channel_label_prop


class Bus(IRemote):
    """
    Implements the common interface

    Defines concrete implementation for bus
    """

    @abc.abstractmethod
    def __str__(self):
        pass

    @property
    def identifier(self) -> str:
        return f'bus[{self.index}]'

    @property
    def gain(self) -> float:
        val = self.getter('gain')
        if val:
            return round(val, 2)
        else:
            return self.public_packets[NBS.zero].busgain[self.index]

    @gain.setter
    def gain(self, val: float):
        self.setter('gain', val)

    def fadeto(self, target: float, time_: int):
        self.setter('FadeTo', f'({target}, {time_})')
        time.sleep(self._remote.DELAY)

    def fadeby(self, change: float, time_: int):
        self.setter('FadeBy', f'({change}, {time_})')
        time.sleep(self._remote.DELAY)


class BusEQ(IRemote):
    @classmethod
    def make(cls, remote, index):
        BUSEQ_cls = type(
            f'BusEQ{remote.kind}',
            (cls,),
            {
                **{param: channel_bool_prop(param) for param in ['on', 'ab']},
            },
        )
        return BUSEQ_cls(remote, index)

    @property
    def identifier(self) -> str:
        return f'bus[{self.index}].eq'


class PhysicalBus(Bus):
    def __str__(self):
        return f'{type(self).__name__}{self.index}'

    @property
    def device(self) -> str:
        return

    @property
    def sr(self) -> int:
        return


class VirtualBus(Bus):
    def __str__(self):
        return f'{type(self).__name__}{self.index}'


class BusLevel(IRemote):
    def __init__(self, remote, index):
        super().__init__(remote, index)
        self.level_map = tuple(
            (i, i + 8)
            for i in range(0, (remote.kind.phys_out + remote.kind.virt_out) * 8, 8)
        )
        self.range = self.level_map[self.index]

    def getter(self):
        """Returns a tuple of level values for the channel."""

        if not self._remote.stopped() and self._remote.event.ldirty:
            return self._remote.cache['bus_level'][self.range[0] : self.range[-1]]
        return self.public_packets[NBS.zero].levels.bus[self.range[0] : self.range[-1]]

    @property
    def identifier(self) -> str:
        return f'bus[{self.index}]'

    @property
    def all(self) -> tuple:
        return self.getter()

    @property
    def isdirty(self) -> bool:
        """
        Returns dirty status for this specific channel.

        Expected to be used in a callback only.
        """
        return any(self._remote._bus_comp[self.range[0] : self.range[-1]])

    is_updated = isdirty


def _make_bus_mode_mixin():
    """Creates a mixin of Bus Modes."""

    mode_names = [
        'normal',
        'amix',
        'repeat',
        'bmix',
        'composite',
        'tvmix',
        'upmix21',
        'upmix41',
        'upmix61',
        'centeronly',
        'lfeonly',
        'rearonly',
    ]

    def identifier(self) -> str:
        return f'bus[{self.index}].mode'

    def get(self):
        """Get current bus mode using ChannelState for clean bit extraction."""
        mode_cache_items = [
            (k, v)
            for k, v in self._remote.cache.items()
            if k.startswith(f'{self.identifier}.') and v == 1
        ]

        if mode_cache_items:
            latest_cached = mode_cache_items[-1][0]
            mode_name = latest_cached.split('.')[-1]
            return mode_name

        bus_state = self.public_packets[NBS.zero].states.bus[self.index]

        # Extract bus mode from bits 4-7 (mask 0xF0, shift right by 4)
        mode_value = (bus_state._state & 0x000000F0) >> 4

        return mode_names[mode_value] if mode_value < len(mode_names) else 'normal'

    return type(
        'BusModeMixin',
        (IRemote,),
        {
            'identifier': property(identifier),
            **{mode.name: bus_mode_prop(mode.name) for mode in BusModes},
            'get': get,
        },
    )


def bus_factory(phys_bus, remote, i) -> Union[PhysicalBus, VirtualBus]:
    """
    Factory method for buses

    Returns a physical or virtual bus subclass
    """
    BUS_cls = PhysicalBus if phys_bus else VirtualBus
    BUSMODEMIXIN_cls = _make_bus_mode_mixin()
    return type(
        f'{BUS_cls.__name__}{remote.kind}',
        (BUS_cls,),
        {
            'eq': BusEQ.make(remote, i),
            'levels': BusLevel(remote, i),
            'mode': BUSMODEMIXIN_cls(remote, i),
            **{param: channel_bool_prop(param) for param in ('mute',)},
            **{param: channel_int_prop(param) for param in ('mono',)},
            'label': channel_label_prop(),
        },
    )(remote, i)


def request_bus_obj(phys_bus, remote, i) -> Bus:
    """
    Bus entry point. Wraps factory method.

    Returns a reference to a bus subclass of a kind
    """
    return bus_factory(phys_bus, remote, i)
