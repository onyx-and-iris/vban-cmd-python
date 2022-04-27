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
            modelist = {
                "amix": (1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1),
                "repeat": (0, 2, 2, 0, 0, 2, 2, 0, 0, 2, 2),
                "bmix": (1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3),
                "composite": (0, 0, 0, 4, 4, 4, 4, 0, 0, 0, 0),
                "tvmix": (1, 0, 1, 4, 5, 4, 5, 0, 1, 0, 1),
                "upmix21": (0, 2, 2, 4, 4, 6, 6, 0, 0, 2, 2),
                "upmix41": (1, 2, 3, 4, 5, 6, 7, 0, 1, 2, 3),
                "upmix61": (0, 0, 0, 0, 0, 0, 0, 8, 8, 8, 8),
                "centeronly": (1, 0, 1, 0, 1, 0, 1, 8, 9, 8, 9),
                "lfeonly": (0, 2, 2, 0, 0, 2, 2, 8, 8, 10, 10),
                "rearonly": (1, 2, 3, 0, 1, 2, 3, 8, 9, 10, 11),
            }
            vals = (
                int.from_bytes(self.public_packet.busstate[self.index], "little") & val
                for val in self._modes.modevals
            )
            if param == "normal":
                return not any(val for val in vals)
            return tuple(round(val / 16) for val in vals) == modelist[param]
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
