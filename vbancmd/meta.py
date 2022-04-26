from .errors import VMCMDErrors
from time import sleep


def strip_bool_prop(param):
    """A strip bool prop."""

    def fget(self):
        val = self.getter(param)
        if val is None:
            val = (
                not int.from_bytes(self.public_packet.stripstate[self.index], "little")
                & getattr(self._modes, f"_{param}")
                == 0
            )
            return val
        return val == 1

    def fset(self, val):
        if not isinstance(val, bool) and val not in (0, 1):
            raise VMCMDErrors(f"{param} is a boolean parameter")
        self.setter(param, 1 if val else 0)

    return property(fget, fset)


def bus_bool_prop(param):
    """A bus bool prop."""

    def fget(self):
        val = self.getter(param)
        if val is None:
            val = (
                not int.from_bytes(self.public_packet.busstate[self.index], "little")
                & getattr(self._modes, f'_{param.replace(".", "_").lower()}')
                == 0
            )
            return val
        return val == 1

    def fset(self, val):
        if not isinstance(val, bool) and val not in (0, 1):
            raise VMCMDErrors(f"{param} is a boolean parameter")
        self.setter(param, 1 if val else 0)

    return property(fget, fset)


def strip_output_prop(param):
    """A strip output prop."""

    def fget(self):
        val = self.getter(param)
        if val is None:
            val = (
                not int.from_bytes(self.public_packet.stripstate[self.index], "little")
                & getattr(self._modes, f"_bus{param.lower()}")
                == 0
            )
            return val
        return val == 1

    def fset(self, val):
        if not isinstance(val, bool) and val not in (0, 1):
            raise VMCMDErrors(f"{param} is a boolean parameter")
        self.setter(param, 1 if val else 0)

    return property(fget, fset)


def bus_mode_prop(param):
    """A bus mode prop."""

    def fget(self):
        val = self.getter(f"mode.{param}")
        if val is None:
            if param == "normal":
                return any(
                    not int.from_bytes(
                        self.public_packet.busstate[self.index], "little"
                    )
                    & val
                    == 0
                    for val in self._modes.modevals
                )
            else:
                val = (
                    not int.from_bytes(
                        self.public_packet.busstate[self.index], "little"
                    )
                    & getattr(self._modes, f"_{param}")
                    == 0
                )
            return val
        return val == 1

    def fset(self, val):
        if not isinstance(val, bool) and val not in (0, 1):
            raise VMCMDErrors(f"mode.{param} is a boolean parameter")
        self.setter(f"mode.{param}", 1 if val else 0)

    return property(fget, fset)


def action_prop(param, val=1):
    """A param that performs an action"""

    def fdo(self):
        self.setter(param, val)

    return fdo
