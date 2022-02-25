import vban_cmd
from vban_cmd import kinds
import socket
from threading import Thread

_kind = 'banana'

vbanrs = {kind.id: vban_cmd.connect(_kind, ip='ws.local') for kind in kinds.all}
tests = vbanrs[_kind]

def setup_package():
    tests._rt_packet_socket.bind((socket.gethostbyname(socket.gethostname()), tests._port))
    tests.worker = Thread(target=tests._send_register_rt, daemon=True)
    tests.worker.start()

def teardown_package():
    pass
