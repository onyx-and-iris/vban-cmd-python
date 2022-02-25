import abc
import select
import socket
from time import sleep
import sys
from threading import Thread
from typing import NamedTuple

from .errors import VMCMDErrors
from . import kinds
from .dataclass import (
    HEADER_SIZE,
    MAX_PACKET_SIZE,
    VBAN_VMRT_Packet_Data,
    VBAN_VMRT_Packet_Header,
    RegisterRTHeader,
    TextRequestHeader
)
from .strip import InputStrip

class VbanCmd(abc.ABC):
    def __init__(self, *args, **kwargs):
        self._ip = kwargs['ip']
        self._port = kwargs['port']
        self._streamname = kwargs['streamname']
        self._bps = kwargs['bps']
        self._channel = kwargs['channel']
        self._delay =  kwargs['delay']
        self._bps_opts = \
        [0, 110, 150, 300, 600, 1200, 2400, 4800, 9600, 14400,19200, 31250, 
        38400, 57600, 115200, 128000, 230400, 250000, 256000, 460800,921600, 
        1000000, 1500000, 2000000, 3000000]

        self._text_header = TextRequestHeader()
        self._register_rt_header = RegisterRTHeader()
        self.expected_packet = VBAN_VMRT_Packet_Header()

        self._rt_register_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._rt_packet_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._sendrequest_string_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        is_readable = []
        is_writable = [self._rt_register_socket, self._rt_packet_socket, self._sendrequest_string_socket]
        is_error = []
        self.ready_to_read, self.ready_to_write, in_error = select.select(is_readable, is_writable, is_error, 60)


    def __enter__(self):
        self._rt_packet_socket.bind((socket.gethostbyname(socket.gethostname()), self._port))
        worker = Thread(target=self._send_register_rt, daemon=True)
        worker.start()
        return self

    def _send_register_rt(self):
        if self._rt_register_socket in self.ready_to_write:
            while True:
                self._rt_register_socket.sendto(
                    self._register_rt_header.header + bytes(1), (socket.gethostbyname(self._ip), self._port)
                    )
                count = int.from_bytes(self._register_rt_header.framecounter, 'little') + 1
                self._register_rt_header.framecounter = count.to_bytes(4, 'little')
                sleep(10)

    def _fetch_rt_packet(self):
        data, _ = self._rt_packet_socket.recvfrom(1024*2)
        # check for packet data
        if len(data) > HEADER_SIZE:
            # check if packet is of type rt service
            if self.expected_packet.header == data[:HEADER_SIZE-4]:
                return VBAN_VMRT_Packet_Data(
                    _voicemeeterType=data[28:29],
                    _reserved=data[29:30],
                    _buffersize=data[30:32],
                    _voicemeeterVersion=data[32:36],
                    _optionBits=data[36:40],
                    _samplerate=data[40:44],
                    _inputLeveldB100=data[44:112],
                    _outputLeveldB100=data[112:240],
                    _TransportBit=data[240:244],
                    _stripState=data[244:276],
                    _busState=data[276:308],
                    _stripGaindB100Layer1=data[308:324],
                    _stripGaindB100Layer2=data[324:340],
                    _stripGaindB100Layer3=data[340:356],
                    _stripGaindB100Layer4=data[356:372],
                    _stripGaindB100Layer5=data[372:388],
                    _stripGaindB100Layer6=data[388:404],
                    _stripGaindB100Layer7=data[404:420],
                    _stripGaindB100Layer8=data[420:436],
                    _busGaindB100=data[436:452],
                    _stripLabelUTF8c60=data[452:932],
                    _busLabelUTF8c60=data[932:1412],
                )
            return False

    def get_rt(self):
        data = False
        while not data:
            data = self._fetch_rt_packet()
        return data

    def set_rt(self, id_, param, val):
        cmd = f'{id_}.{param}={val}'
        if self._sendrequest_string_socket in self.ready_to_write:
            print(f'sending {cmd} to {socket.gethostbyname(self._ip)}:{self._port}')
            self._sendrequest_string_socket.sendto(
                self._text_header.header + cmd.encode(), (socket.gethostbyname(self._ip), self._port)
                )
            count = int.from_bytes(self._text_header.framecounter, 'little') + 1
            self._text_header.framecounter = count.to_bytes(4, 'little')
            sleep(self._delay)

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self._rt_packet_socket.close()
        sys.exit()


def _make_remote(kind: NamedTuple) -> VbanCmd:
    """
    Creates a new remote class and sets its number of inputs
    and outputs for a VM kind.

    The returned class will subclass VbanCmd.
    """
    def init(self, *args, **kwargs):
        defaultkwargs = {
            'ip': None, 'port': 6990, 'streamname': 'Command1', 'bps': 0, 
            'channel': 0, 'delay': 0.03,
            }
        kwargs = defaultkwargs | kwargs
        VbanCmd.__init__(self, *args, **kwargs)
        self.kind = kind
        self.phys_in, self.virt_in = kind.ins
        self.phys_out, self.virt_out = kind.outs
        self.strip = \
        tuple(InputStrip.make((i < self.phys_in), self, i)
        for i in range(self.phys_in + self.virt_in))

    return type(f'VbanCmd{kind.name}', (VbanCmd,), {
        '__init__': init,
    })

_remotes = {kind.id: _make_remote(kind) for kind in kinds.all}

def connect(kind_id: str, *args, **kwargs):
    try:
        VBANCMD_cls = _remotes[kind_id]
        return VBANCMD_cls(**kwargs)
    except KeyError as err:
        raise VMCMDErrors(f'Invalid Voicemeeter kind: {kind_id}')
