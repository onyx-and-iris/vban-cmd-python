from .errors import VMCMDErrors

def strip_output_prop(param):
    """ A strip output prop. """
    def fget(self):
        data = self._remote.public_packet
        return not int.from_bytes(data.stripstate[self.index], 'little') & getattr(self._modes, f'_bus{param.lower()}') == 0
    def fset(self, val):
        if not isinstance(val, bool) and val not in (0, 1):
            raise VMCMDErrors(f'{param} is a boolean parameter')
        self.setter(param, 1 if val else 0)
    return property(fget, fset)
