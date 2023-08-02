import logging
from abc import abstractmethod
from enum import IntEnum
from functools import cached_property
from typing import Iterable

from .bus import request_bus_obj as bus
from .command import Command
from .config import request_config as configs
from .error import VBANCMDError
from .kinds import KindMapClass
from .kinds import request_kind_map as kindmap
from .macrobutton import MacroButton
from .strip import request_strip_obj as strip
from .vban import request_vban_obj as vban
from .vbancmd import VbanCmd

logger = logging.getLogger(__name__)


class FactoryBuilder:
    """
    Builder class for factories.

    Separates construction from representation.
    """

    BuilderProgress = IntEnum(
        "BuilderProgress", "strip bus command macrobutton vban", start=0
    )

    def __init__(self, factory, kind: KindMapClass):
        self._factory = factory
        self.kind = kind
        self._info = (
            f"Finished building strips for {self._factory}",
            f"Finished building buses for {self._factory}",
            f"Finished building commands for {self._factory}",
            f"Finished building macrobuttons for {self._factory}",
            f"Finished building vban in/out streams for {self._factory}",
        )
        self.logger = logger.getChild(self.__class__.__name__)

    def _pinfo(self, name: str) -> None:
        """prints progress status for each step"""
        name = name.split("_")[1]
        self.logger.info(self._info[int(getattr(self.BuilderProgress, name))])

    def make_strip(self):
        self._factory.strip = tuple(
            strip(i < self.kind.phys_in, self._factory, i)
            for i in range(self.kind.num_strip)
        )
        return self

    def make_bus(self):
        self._factory.bus = tuple(
            bus(i < self.kind.phys_out, self._factory, i)
            for i in range(self.kind.num_bus)
        )
        return self

    def make_command(self):
        self._factory.command = Command.make(self._factory)
        return self

    def make_macrobutton(self):
        self._factory.button = tuple(MacroButton(self._factory, i) for i in range(80))
        return self

    def make_vban(self):
        self._factory.vban = vban(self._factory)
        return self


class FactoryBase(VbanCmd):
    """Base class for factories, subclasses VbanCmd."""

    def __init__(self, kind_id: str, **kwargs):
        defaultkwargs = {
            "ip": None,
            "port": 6980,
            "streamname": "Command1",
            "bps": 0,
            "channel": 0,
            "ratelimit": 0.01,
            "timeout": 5,
            "outbound": False,
            "sync": False,
            "pdirty": False,
            "ldirty": False,
        }
        if "subs" in kwargs:
            defaultkwargs |= kwargs.pop("subs")  # for backwards compatibility
        kwargs = defaultkwargs | kwargs
        self.kind = kindmap(kind_id)
        super().__init__(**kwargs)
        self.builder = FactoryBuilder(self, self.kind)
        self._steps = (
            self.builder.make_strip,
            self.builder.make_bus,
            self.builder.make_command,
            self.builder.make_macrobutton,
            self.builder.make_vban,
        )
        self._configs = None

    def __str__(self) -> str:
        return f"Voicemeeter {self.kind}"

    def __repr__(self):
        return (
            type(self).__name__
            + f"({self.kind}, ip='{self.ip}', port={self.port}, streamname='{self.streamname}')"
        )

    @property
    @abstractmethod
    def steps(self):
        pass

    @cached_property
    def configs(self):
        self._configs = configs(self.kind.name)
        return self._configs


class BasicFactory(FactoryBase):
    """
    Represents a Basic VbanCmd subclass

    Responsible for directing the builder class
    """

    def __new__(cls, *args, **kwargs):
        if cls is BasicFactory:
            raise TypeError(f"'{cls.__name__}' does not support direct instantiation")
        return object.__new__(cls)

    def __init__(self, kind_id, **kwargs):
        super().__init__(kind_id, **kwargs)
        [step()._pinfo(step.__name__) for step in self.steps]

    @property
    def steps(self) -> Iterable:
        """steps required to build the interface for a kind"""
        return self._steps


class BananaFactory(FactoryBase):
    """
    Represents a Banana VbanCmd subclass

    Responsible for directing the builder class
    """

    def __new__(cls, *args, **kwargs):
        if cls is BananaFactory:
            raise TypeError(f"'{cls.__name__}' does not support direct instantiation")
        return object.__new__(cls)

    def __init__(self, kind_id, **kwargs):
        super().__init__(kind_id, **kwargs)
        [step()._pinfo(step.__name__) for step in self.steps]

    @property
    def steps(self) -> Iterable:
        """steps required to build the interface for a kind"""
        return self._steps


class PotatoFactory(FactoryBase):
    """
    Represents a Potato VbanCmd subclass

    Responsible for directing the builder class
    """

    def __new__(cls, *args, **kwargs):
        if cls is PotatoFactory:
            raise TypeError(f"'{cls.__name__}' does not support direct instantiation")
        return object.__new__(cls)

    def __init__(self, kind_id: str, **kwargs):
        super().__init__(kind_id, **kwargs)
        [step()._pinfo(step.__name__) for step in self.steps]

    @property
    def steps(self) -> Iterable:
        """steps required to build the interface for a kind"""
        return self._steps


def vbancmd_factory(kind_id: str, **kwargs) -> VbanCmd:
    """
    Factory method, invokes a factory creation class of a kind

    Returns a VbanCmd class of a kind
    """
    match kind_id:
        case "basic":
            _factory = BasicFactory
        case "banana":
            _factory = BananaFactory
        case "potato":
            _factory = PotatoFactory
        case _:
            raise ValueError(f"Unknown Voicemeeter kind '{kind_id}'")
    return type(f"VbanCmd{kind_id.capitalize()}", (_factory,), {})(kind_id, **kwargs)


def request_vbancmd_obj(kind_id: str, **kwargs) -> VbanCmd:
    """
    Interface entry point. Wraps factory method and handles errors

    Returns a reference to a VbanCmd class of a kind
    """
    logger_entry = logger.getChild("factory.request_vbancmd_obj")

    VBANCMD_obj = None
    try:
        VBANCMD_obj = vbancmd_factory(kind_id, **kwargs)
    except (ValueError, TypeError) as e:
        logger_entry.exception(f"{type(e).__name__}: {e}")
        raise VBANCMDError(str(e)) from e
    return VBANCMD_obj
