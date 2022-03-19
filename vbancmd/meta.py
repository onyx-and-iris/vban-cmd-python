from .errors import VMCMDErrors
from time import sleep

def strip_output_prop(param):
    """ A strip output prop. """
    def fget(self):
        return not int.from_bytes(self.public_packet.stripstate[self.index], 'little') & getattr(self._modes, f'_bus{param.lower()}') == 0
    def fset(self, val):
        if not isinstance(val, bool) and val not in (0, 1):
            raise VMCMDErrors(f'{param} is a boolean parameter')
        self.setter(param, 1 if val else 0)
    return property(fget, fset)

def bus_mode_prop(param):
    """ A strip output prop. """
    def fget(self):
        data = self.public_packet
        modes = {
            'normal': (False, False, False, False, False, False, False, False, False, False, False, False),
            'amix': (False, True, False, True, False, True, False, True, False, True, False, True),
            'repeat': (False, False, True, True, False, False, True, True, False, False, True, True),
            'bmix': (False, True, True, True, False, True, True, True, False, True, True, True),
            'composite': (False, False, False, False, True, True, True, True, False, False, False, False),
            'tvmix': (False, True, False, True, True, True, True, True, False, True, False, True),
            'upmix21': (False, False, True, True, True, True, True, True, False, False, True, True),
            'upmix41': (False, True, True, True, True, True, True, True, False, True, True, True),
            'upmix61': (False, False, False, False, False, False, False, False, True, True, True, True),
            'centeronly': (False, True, False, True, False, True, False, True, True, True, True, True),
            'lfeonly': (False, False, True, True, False, False, True, True, True, True, True, True),
            'rearonly': (False, True, True, True, False, True, True, True, True, True, True, True),
        }
        vals = tuple(not int.from_bytes(data.busstate[self.index], 'little') & val == 0 for val in self._modes.modevals)
        return vals == modes[param.lower()]
    def fset(self, val):
        if not isinstance(val, bool) and val not in (0, 1):
            raise VMCMDErrors(f'mode.{param} is a boolean parameter')
        self.setter(f'mode.{param}', 1 if val else 0)
    return property(fget, fset)
