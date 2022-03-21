import abc
from .errors import VMCMDErrors
from .meta import action_prop

class ICommand(abc.ABC):
    """ Command Base Class """
    def __init__(self, remote):
        self._remote = remote

    def setter(self, param, val):
        """ Sends a string request RT packet. """
        self._remote.set_rt(f'{self.identifier}', param, val)

    @abc.abstractmethod
    def identifier(self):
        pass


class Command(ICommand):
    """ Command Concrete Class """
    @classmethod
    def make(cls, remote):
        """
        Factory function for command class.

        Returns a Command class of a kind.
        """
        CMD_cls = type(f'Command{remote.kind.name}', (cls,), {
            **{param: action_prop(param)
            for param in ['show', 'shutdown', 'restart']},
            'hide': action_prop('show', val=0),
        })
        return CMD_cls(remote)

    @property
    def identifier(self) -> str:
        return 'Command'

    def set_showvbanchat(self, val: bool):
        if not isinstance(val, bool) and val not in (0,1):
            raise VMCMDErrors('showvbanchat is a boolean parameter')
        self.setter('DialogShow.VBANCHAT', 1 if val else 0)
    showvbanchat = property(fset=set_showvbanchat)

    def set_lock(self, val: bool):
        if not isinstance(val, bool) and val not in (0,1):
            raise VMCMDErrors('lock is a boolean parameter')
        self.setter('lock', 1 if val else 0)        
    lock = property(fset=set_lock)
