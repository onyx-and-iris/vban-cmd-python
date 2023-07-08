from abc import abstractmethod

from .iremote import IRemote


class VbanStream(IRemote):
    """
    Implements the common interface

    Defines concrete implementation for vban stream
    """

    @abstractmethod
    def __str__(self):
        pass

    @property
    def identifier(self) -> str:
        return f"vban.{self.direction}stream[{self.index}]"

    @property
    def on(self) -> bool:
        return

    @on.setter
    def on(self, val: bool):
        self.setter("on", 1 if val else 0)

    @property
    def name(self) -> str:
        return

    @name.setter
    def name(self, val: str):
        self.setter("name", val)

    @property
    def ip(self) -> str:
        return

    @ip.setter
    def ip(self, val: str):
        self.setter("ip", val)

    @property
    def port(self) -> int:
        return

    @port.setter
    def port(self, val: int):
        if not 1024 <= val <= 65535:
            self.logger.warning(
                f"port got: {val} but expected a value from 1024 to 65535"
            )
        self.setter("port", val)

    @property
    def sr(self) -> int:
        return

    @sr.setter
    def sr(self, val: int):
        opts = (11025, 16000, 22050, 24000, 32000, 44100, 48000, 64000, 88200, 96000)
        if val not in opts:
            self.logger.warning(f"sr got: {val} but expected a value in {opts}")
        self.setter("sr", val)

    @property
    def channel(self) -> int:
        return

    @channel.setter
    def channel(self, val: int):
        if not 1 <= val <= 8:
            self.logger.warning(f"channel got: {val} but expected a value from 1 to 8")
        self.setter("channel", val)

    @property
    def bit(self) -> int:
        return

    @bit.setter
    def bit(self, val: int):
        if val not in (16, 24):
            self.logger.warning(f"bit got: {val} but expected value 16 or 24")
        self.setter("bit", 1 if (val == 16) else 2)

    @property
    def quality(self) -> int:
        return

    @quality.setter
    def quality(self, val: int):
        if not 0 <= val <= 4:
            self.logger.warning(f"quality got: {val} but expected a value from 0 to 4")
        self.setter("quality", val)

    @property
    def route(self) -> int:
        return

    @route.setter
    def route(self, val: int):
        if not 0 <= val <= 8:
            self.logger.warning(f"route got: {val} but expected a value from 0 to 8")
        self.setter("route", val)


class VbanInstream(VbanStream):
    """
    class representing a vban instream

    subclasses VbanStream
    """

    def __str__(self):
        return f"{type(self).__name__}{self._remote.kind}{self.index}"

    @property
    def direction(self) -> str:
        return "in"

    @property
    def sr(self) -> int:
        return

    @property
    def channel(self) -> int:
        return

    @property
    def bit(self) -> int:
        return


class VbanOutstream(VbanStream):
    """
    class representing a vban outstream

    Subclasses VbanStream
    """

    def __str__(self):
        return f"{type(self).__name__}{self._remote.kind}{self.index}"

    @property
    def direction(self) -> str:
        return "out"


class Vban:
    """
    class representing the vban module

    Contains two tuples, one for each stream type
    """

    def __init__(self, remote):
        self.remote = remote
        num_instream, num_outstream = remote.kind.vban
        self.instream = tuple(VbanInstream(remote, i) for i in range(num_instream))
        self.outstream = tuple(VbanOutstream(remote, i) for i in range(num_outstream))

    def enable(self):
        """if VBAN disabled there can be no communication with it"""

    def disable(self):
        self.remote._set_rt("vban.Enable", 0)


def vban_factory(remote) -> Vban:
    """
    Factory method for vban

    Returns a class that represents the VBAN module.
    """
    VBAN_cls = Vban
    return type(f"{VBAN_cls.__name__}", (VBAN_cls,), {})(remote)


def request_vban_obj(remote) -> Vban:
    """
    Vban entry point.

    Returns a reference to a Vban class of a kind
    """
    return vban_factory(remote)
