from functools import partial

from .enums import NBS
from .util import cache_bool, cache_float, cache_int, cache_string


def channel_bool_prop(param):
    """meta function for channel boolean parameters"""

    @partial(cache_bool, param=param)
    def fget(self):
        cmd = self._cmd(param)
        self.logger.debug(f'getter: {cmd}')
        return (
            not int.from_bytes(
                getattr(
                    self.public_packets[NBS.zero],
                    f'{"strip" if "strip" in type(self).__name__.lower() else "bus"}state',
                )[self.index],
                'little',
            )
            & getattr(self._modes, f'_{param.lower()}')
            == 0
        )

    def fset(self, val):
        self.setter(param, 1 if val else 0)

    return property(fget, fset)


def channel_int_prop(param):
    """meta function for channel integer parameters"""

    @partial(cache_int, param=param)
    def fget(self):
        cmd = self._cmd(param)
        self.logger.debug(f'getter: {cmd}')
        return int.from_bytes(
            getattr(
                self.public_packets[NBS.zero],
                f'{"strip" if "strip" in type(self).__name__.lower() else "bus"}state',
            )[self.index],
            'little',
        ) & getattr(self._modes, f'_{param.lower()}')

    def fset(self, val):
        self.setter(param, val)

    return property(fget, fset)


def channel_label_prop():
    """meta function for channel label parameters"""

    @partial(cache_string, param='label')
    def fget(self) -> str:
        if 'strip' in type(self).__name__.lower():
            return self.public_packets[NBS.zero].labels.strip[self.index]
        else:
            return self.public_packets[NBS.zero].labels.bus[self.index]

    def fset(self, val: str):
        self.setter('label', f'"{val}"')

    return property(fget, fset)


def strip_output_prop(param):
    """meta function for strip output parameters. (A1-A5, B1-B3)"""

    @partial(cache_bool, param=param)
    def fget(self):
        cmd = self._cmd(param)
        self.logger.debug(f'getter: {cmd}')
        return (
            not int.from_bytes(
                self.public_packets[NBS.zero].stripstate[self.index], 'little'
            )
            & getattr(self._modes, f'_bus{param.lower()}')
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
        self.logger.debug(f'getter: {cmd}')
        return [
            (
                int.from_bytes(
                    self.public_packets[NBS.zero].busstate[self.index], 'little'
                )
                & val
            )
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


def xy_prop(param):
    """meta function for XY pad parameters"""

    @partial(cache_float, param=param)
    def fget(self):
        cmd = self._cmd(param)
        self.logger.debug(f'getter: {cmd}')
        if self.public_packets[NBS.one] is None:
            return 0.0

        positions = self.public_packets[NBS.one].strips[self.index].positions
        match param:
            case 'pan_x':
                return positions.pan_x
            case 'pan_y':
                return positions.pan_y
            case 'color_x':
                return positions.color_x
            case 'color_y':
                return positions.color_y
            case 'fx1':
                return positions.fx1
            case 'fx2':
                return positions.fx2

    def fset(self, val):
        self.setter(param, val)

    return property(fget, fset)


def send_prop(param):
    """meta function for send parameters"""

    @partial(cache_float, param=param)
    def fget(self):
        cmd = self._cmd(param)
        self.logger.debug(f'getter: {cmd}')
        if self.public_packets[NBS.one] is None:
            return 0.0

        sends = self.public_packets[NBS.one].strips[self.index].sends
        match param:
            case 'reverb':
                return sends.reverb
            case 'delay':
                return sends.delay
            case 'fx1':
                return sends.fx1
            case 'fx2':
                return sends.fx2

    def fset(self, val):
        self.setter(param, val)

    return property(fget, fset)
