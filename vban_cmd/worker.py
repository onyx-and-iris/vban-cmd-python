import logging
import socket
import threading
import time
from typing import Optional

from .error import VBANCMDError
from .packet import HEADER_SIZE, SubscribeHeader, VbanRtPacket, VbanRtPacketHeader
from .util import Socket


class Subscriber(threading.Thread):
    """fire a subscription packet every 10 seconds"""

    def __init__(self, remote):
        super().__init__(name="subscriber", target=self.subscribe, daemon=True)
        self._remote = remote
        self.packet = SubscribeHeader()

    def subscribe(self):
        while self._remote.running:
            try:
                self._remote.socks[Socket.register].sendto(
                    self.packet.header,
                    (socket.gethostbyname(self._remote.ip), self._remote.port),
                )
                count = int.from_bytes(self.packet.framecounter, "little") + 1
                self.packet.framecounter = count.to_bytes(4, "little")
                time.sleep(10)
            except socket.gaierror as e:
                err_msg = f"Unable to resolve hostname {self._remote.ip}"
                print(err_msg)
                raise VBANCMDError(err_msg)


class Updater(threading.Thread):
    """
    continously updates the public packet

    notifies observers of event updates
    """

    logger = logging.getLogger("worker.updater")

    def __init__(self, remote):
        super().__init__(name="updater", target=self.update, daemon=True)
        self._remote = remote
        self._remote.socks[Socket.response].settimeout(5)
        self._remote.socks[Socket.response].bind(
            (socket.gethostbyname(socket.gethostname()), self._remote.port)
        )
        self.packet_expected = VbanRtPacketHeader()
        self._remote._public_packet = self._get_rt()

    def _fetch_rt_packet(self) -> Optional[VbanRtPacket]:
        try:
            data, _ = self._remote.socks[Socket.response].recvfrom(2048)
            # check for packet data
            if len(data) > HEADER_SIZE:
                # check if packet is of type rt packet response
                if self.packet_expected.header == data[: HEADER_SIZE - 4]:
                    return VbanRtPacket(
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
        except TimeoutError as e:
            err_msg = f"Unable to establish connection with {self._remote.ip}"
            print(err_msg)
            raise VBANCMDError(err_msg)

    def _get_rt(self) -> VbanRtPacket:
        """Attempt to fetch data packet until a valid one found"""

        def fget():
            data = False
            while not data:
                data = self._fetch_rt_packet()
                time.sleep(self._remote.DELAY)
            return data

        return fget()

    def update(self):
        (
            self._remote.cache["strip_level"],
            self._remote.cache["bus_level"],
        ) = self._remote._get_levels(self._remote.public_packet)

        while self._remote.running:
            start = time.time()
            _pp = self._get_rt()
            self._remote._strip_buf, self._remote._bus_buf = self._remote._get_levels(
                _pp
            )
            self._remote._pdirty = _pp.pdirty(self._remote.public_packet)

            if self._remote.event.ldirty and self._remote.ldirty:
                self._remote.cache["strip_level"] = self._remote._strip_buf
                self._remote.cache["bus_level"] = self._remote._bus_buf
                self._remote.subject.notify("ldirty")
            if self._remote.public_packet != _pp:
                self._remote._public_packet = _pp
            if self._remote.event.pdirty and self._remote.pdirty:
                self._remote.subject.notify("pdirty")
            elapsed = time.time() - start
            if self._remote.ratelimit - elapsed > 0:
                time.sleep(self._remote.ratelimit - elapsed)
