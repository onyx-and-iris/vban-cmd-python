import abc
import logging

logger = logging.getLogger(__name__)


class IRemote(abc.ABC):
    """
    Common interface between base class and extended (higher) classes

    Provides some default implementation
    """

    def __init__(self, remote, index=None):
        self._remote = remote
        self.index = index
        self.logger = logger.getChild(self.__class__.__name__)

    def getter(self, param):
        cmd = self._cmd(param)
        self.logger.debug(f'getter: {cmd}')
        if cmd in self._remote.cache:
            return self._remote.cache.pop(cmd)
        if self._remote.sync:
            self._remote.clear_dirty()

    def setter(self, param, val):
        """Sends a string request RT packet."""
        self.logger.debug(f'setter: {self._cmd(param)}={val}')
        self._remote._set_rt(self._cmd(param), val)

    def _cmd(self, param):
        cmd = (self.identifier,)
        if param:
            cmd += (f'.{param}',)
        return ''.join(cmd)

    @property
    @abc.abstractmethod
    def identifier(self):
        pass

    @property
    def public_packets(self):
        """Returns an RT data packet."""
        return self._remote.public_packets

    def apply(self, data):
        """Sets all parameters of a dict for the channel."""

        script = ''

        def fget(attr, val):
            if attr == 'mode':
                return (f'mode.{val}', 1)
            elif attr == 'knob':
                return ('', val)
            return (attr, val)

        for attr, val in data.items():
            if not isinstance(val, dict):
                if attr in dir(self):  # avoid calling getattr (with hasattr)
                    attr, val = fget(attr, val)
                    if isinstance(val, bool):
                        val = 1 if val else 0

                    self._remote.cache[self._cmd(attr)] = val
                    script += f'{self._cmd(attr)}={val};'
            else:
                target = getattr(self, attr)
                target.apply(val)

        self._remote.sendtext(script)
