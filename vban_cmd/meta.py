from functools import partial

from .util import cache_bool, cache_string


def channel_bool_prop(param):
    """meta function for channel boolean parameters"""

    @partial(cache_bool, param=param)
    def fget(self):
        cmd = self._cmd(param)
        self.logger.debug(f"getter: {cmd}")
        return (
            not int.from_bytes(
                getattr(
                    self.public_packet,
                    f"{'strip' if 'strip' in type(self).__name__.lower() else 'bus'}state",
                )[self.index],
                "little",
            )
            & getattr(self._modes, f"_{param.lower()}")
            == 0
        )

    def fset(self, val):
        self.setter(param, 1 if val else 0)

    return property(fget, fset)


def channel_label_prop():
    """meta function for channel label parameters"""

    @partial(cache_string, param="label")
    def fget(self) -> str:
        return getattr(
            self.public_packet,
            f"{'strip' if 'strip' in type(self).__name__.lower() else 'bus'}labels",
        )[self.index]

    def fset(self, val: str):
        self.setter("label", str(val))

    return property(fget, fset)


def strip_output_prop(param):
    """meta function for strip output parameters. (A1-A5, B1-B3)"""

    @partial(cache_bool, param=param)
    def fget(self):
        cmd = self._cmd(param)
        self.logger.debug(f"getter: {cmd}")
        return (
            not int.from_bytes(self.public_packet.stripstate[self.index], "little")
            & getattr(self._modes, f"_bus{param.lower()}")
            == 0
        )

    def fset(self, val):
        self.setter(param, 1 if val else 0)

    return property(fget, fset)


def bus_mode_prop(param):
    """meta function for bus mode parameters"""

    @partial(cache_bool, param=param)
    def fget(self):
        cmd = self._cmd(param)
        self.logger.debug(f"getter: {cmd}")
        return [
            (int.from_bytes(self.public_packet.busstate[self.index], "little") & val)
            >> 4
            for val in self._modes.modevals
        ] == self.modestates[param]

    def fset(self, val):
        self.setter(param, 1 if val else 0)

    return property(fget, fset)


def action_fn(param, val=1):
    """A function that performs an action"""

    def fdo(self):
        self.setter(param, val)

    return fdo
