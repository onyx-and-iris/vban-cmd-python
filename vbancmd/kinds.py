import sys
import platform
from collections import namedtuple
from .errors import VMCMDErrors

"""
Represents a major version of Voicemeeter and describes
its strip layout.
"""
VMKind = namedtuple('VMKind', ['id', 'name', 'ins', 'outs', 'executable', 'vban'])

bits = 64 if sys.maxsize > 2**32 else 32
os = platform.system()

_kind_map = {
  'basic': VMKind('basic', 'Basic', (2,1), (1,1), 'voicemeeter.exe', (4, 4)),
  'banana': VMKind('banana', 'Banana', (3,2), (3,2), 'voicemeeterpro.exe', (8, 8)),
  'potato': VMKind('potato', 'Potato', (5,3), (5,3),
  f'voicemeeter8{"x64" if bits == 64 else ""}.exe', (8, 8))
}

def get(kind_id):
    try:
        return _kind_map[kind_id]
    except KeyError:
        raise VMCMDErrors(f'Invalid Voicemeeter kind: {kind_id}')

all = list(_kind_map.values())
