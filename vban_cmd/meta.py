from functools import partial

from .enums import NBS
from .util import cache_bool, cache_float, cache_string


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


def channel_label_prop():
    """meta function for channel label parameters"""

    @partial(cache_string, param='label')
    def fget(self) -> str:
        return getattr(
            self.public_packets[NBS.zero],
            f'{"strip" if "strip" in type(self).__name__.lower() else "bus"}labels',
        )[self.index]

    def fset(self, val: str):
        self.setter('label', str(val))

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
        _type, axis = param.split('_')
        if self.public_packets[NBS.one] is None:
            return 0.0
        x, y = getattr(
            self.public_packets[NBS.one].strips[self.index], f'position_{_type.lower()}'
        )
        return x if axis == 'x' else y

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
        val = getattr(self.public_packets[NBS.one].strips[self.index], f'send_{param}')
        match param:
            case 'reverb' | 'fx1':
                return val[0]
            case 'delay' | 'fx2':
                return val[1]

    def fset(self, val):
        self.setter(param, val)

    return property(fget, fset)
