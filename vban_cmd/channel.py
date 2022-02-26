import abc
from .errors import VMCMDErrors
from dataclasses import dataclass

@dataclass
class Modes:
    """ Channel Modes """
    _mute: hex=0x00000001
    _solo: hex=0x00000002
    _mono: hex=0x00000004
    _mutec: hex=0x00000008

    _mixdown: hex=0x00000010
    _repeat: hex=0x00000020
    _mixdownb: hex=0x00000030
    _composite: hex=0x00000040
    _upmixtv: hex=0x00000050
    _updmix2: hex=0x00000060
    _upmix4: hex=0x00000070
    _upmix6: hex=0x00000080
    _center: hex=0x00000090
    _lfe: hex=0x000000A0
    _rear: hex=0x000000B0

    _mask: hex=0x000000F0

    _eq: hex=0x00000100
    _cross: hex=0x00000200
    _eqb: hex=0x00000800

    _busa: hex=0x00001000
    _busa1: hex=0x00001000
    _busa2: hex=0x00002000
    _busa3: hex=0x00004000
    _busa4: hex=0x00008000
    _busa5: hex=0x00080000

    _busb: hex=0x00010000
    _busb1: hex=0x00010000
    _busb2: hex=0x00020000
    _busb3: hex=0x00040000

    _pan0: hex=0x00000000
    _pancolor: hex=0x00100000
    _panmod: hex=0x00200000
    _panmask: hex=0x00F00000

    _postfx_r: hex=0x01000000
    _postfx_d: hex=0x02000000
    _postfx1: hex=0x04000000
    _postfx2: hex=0x08000000

    _sel: hex=0x10000000
    _monitor: hex=0x20000000

class Channel(abc.ABC):
    """ Base class for InputStrip and OutputBus. """
    def __init__(self, remote, index):
        self._remote = remote
        self.index = index
        self._modes = Modes()

    def setter(self, param, val):
        """ Sends a string request RT packet. """
        self._remote.set_rt(f'{self.identifier}', param, val)

    @abc.abstractmethod
    def identifier(self):
        pass

    @property
    def public_packet(self):
        """ Returns an RT data packet. """
        return self._remote.public_packet
