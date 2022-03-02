import vban_cmd
from vban_cmd import kinds
from vban_cmd.channel import Modes
import socket
from threading import Thread
from time import sleep

_kind = 'potato'
opts = {
    'ip': 'ws.local',
    'streamname': 'testing',
    'port': 6990,
    'bps': 0,
    'channel': 3
}

vbanrs = {kind.id: vban_cmd.connect(_kind, **opts) for kind in kinds.all}
tests = vbanrs[_kind]

def setup_package():
    tests._modes = Modes()
    tests._rt_packet_socket.bind((socket.gethostbyname(socket.gethostname()), tests._port))
    tests.worker = Thread(target=tests._send_register_rt, daemon=True)
    tests.worker.start()

def teardown_package():
    tests._rt_packet_socket.close()
    tests._rt_register_socket.close()
    tests._sendrequest_string_socket.close()
