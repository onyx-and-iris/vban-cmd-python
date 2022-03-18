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
    tests._modes = Modes()
    tests._rt_packet_socket.bind((socket.gethostbyname(socket.gethostname()), tests._port))
    tests.worker = Thread(target=tests._send_register_rt, daemon=True)
    tests.worker.start()
    tests._public_packet = tests._get_rt()
    tests.worker2 = Thread(target=tests._keepupdated, daemon=True)
    tests.worker2.start()

def teardown_package():
    tests.close()
