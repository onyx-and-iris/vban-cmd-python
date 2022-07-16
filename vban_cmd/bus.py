import time
from abc import abstractmethod
from enum import IntEnum
from typing import Union

from .error import VMCMDErrors
from .iremote import IRemote
from .meta import bus_mode_prop, channel_bool_prop, channel_label_prop

BusModes = IntEnum(
    "BusModes",
    "normal amix bmix repeat composite tvmix upmix21 upmix41 upmix61 centeronly lfeonly rearonly",
    start=0,
)


class Bus(IRemote):
    """
    Implements the common interface

    Defines concrete implementation for bus
    """

    @abstractmethod
    def __str__(self):
        pass

    @property
    def identifier(self) -> str:
        return f"Bus[{self.index}]"

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

        val = self.getter("gain")
        if val is None:
            val = fget() * 0.01
        return round(val, 1)

    @gain.setter
    def gain(self, val: float):
        self.setter("gain", val)


class PhysicalBus(Bus):
    def __str__(self):
        return f"{type(self).__name__}{self.index}"

    @property
    def device(self) -> str:
        return

    @property
    def sr(self) -> int:
        return


class VirtualBus(Bus):
    def __str__(self):
        return f"{type(self).__name__}{self.index}"


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

        return tuple(
            round(-i * 0.01, 1)
            for i in self._remote.cache["bus_level"][self.range[0] : self.range[-1]]
        )

    @property
    def identifier(self) -> str:
        return f"Bus[{self.index}]"

    @property
    def all(self) -> tuple:
        return self.getter()

    @property
    def is_updated(self) -> bool:
        return any(self._remote._bus_comp[self.range[0] : self.range[-1]])


def _make_bus_mode_mixin():
    """Creates a mixin of Bus Modes."""

    def identifier(self) -> str:
        return f"Bus[{self.index}].mode"

    def get(self):
        time.sleep(0.01)
        for i, val in enumerate(
            [
                self.amix,
                self.bmix,
                self.repeat,
                self.composite,
                self.tvmix,
                self.upmix21,
                self.upmix41,
                self.upmix61,
                self.centeronly,
                self.lfeonly,
                self.rearonly,
            ]
        ):
            if val:
                return BusModes(i + 1).name
        return "normal"

    return type(
        "BusModeMixin",
        (IRemote,),
        {
            "identifier": property(identifier),
            **{mode.name: bus_mode_prop(mode.name) for mode in BusModes},
            "get": get,
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
        f"{BUS_cls.__name__}{remote.kind}",
        (BUS_cls,),
        {
            "levels": BusLevel(remote, i),
            "mode": BUSMODEMIXIN_cls(remote, i),
            **{param: channel_bool_prop(param) for param in ["mute", "mono"]},
            "eq": channel_bool_prop("eq.On"),
            "eq_ab": channel_bool_prop("eq.ab"),
            "label": channel_label_prop(),
        },
    )(remote, i)


def request_bus_obj(phys_bus, remote, i) -> Bus:
    """
    Bus entry point. Wraps factory method.

    Returns a reference to a bus subclass of a kind
    """
    return bus_factory(phys_bus, remote, i)
