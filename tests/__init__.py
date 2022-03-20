import vbancmd
from vbancmd import kinds
from vbancmd.channel import Modes
import socket
from threading import Thread

_kind = 'potato'
opts = {
    'ip': 'ws.local',
    'streamname': 'testing',
    'port': 6990,
    'bps': 0,
}

vbanrs = {kind.id: vbancmd.connect(_kind, **opts) for kind in kinds.all}
tests = vbanrs[_kind]

def setup_package():
    tests.login()

def teardown_package():
    tests.logout()
