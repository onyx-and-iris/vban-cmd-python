import socket
import threading
import time
from enum import IntEnum
from typing import Optional

from .packet import (
    HEADER_SIZE,
    RegisterRTHeader,
    VBAN_VMRT_Packet_Data,
    VBAN_VMRT_Packet_Header,
)
from .util import Socket


class Subscriber(threading.Thread):
    """fire a subscription packet every 10 seconds"""

    def __init__(self, remote):
        super().__init__(name="subscriber", target=self.register, daemon=True)
        self._rem = remote
        self.register_header = RegisterRTHeader()

    def register(self):
        while self._rem.running:
            try:
                self._rem.socks[Socket.register].sendto(
                    self.register_header.header,
                    (socket.gethostbyname(self._rem.ip), self._rem.port),
                )
                count = int.from_bytes(self.register_header.framecounter, "little") + 1
                self.register_header.framecounter = count.to_bytes(4, "little")
                time.sleep(10)
            except socket.gaierror as e:
                print(f"Unable to resolve hostname {self._rem.ip}")
                self._rem.socks[Socket.register].close()
                raise e


class Updater(threading.Thread):
    """
    continously updates the public packet

    notifies observers of event updates
    """

    def __init__(self, remote):
        super().__init__(name="updater", target=self.update, daemon=True)
        self._rem = remote
        self._rem.socks[Socket.response].bind(
            (socket.gethostbyname(socket.gethostname()), self._rem.port)
        )
        self.expected_packet = VBAN_VMRT_Packet_Header()
        self._rem._public_packet = self._get_rt()

    def _fetch_rt_packet(self) -> Optional[VBAN_VMRT_Packet_Data]:
        """Returns a valid RT Data Packet or None"""
        data, _ = self._rem.socks[Socket.response].recvfrom(2048)
        # check for packet data
        if len(data) > HEADER_SIZE:
            # check if packet is of type VBAN
            if self.expected_packet.header == data[: HEADER_SIZE - 4]:
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

    def _get_rt(self) -> VBAN_VMRT_Packet_Data:
        """Attempt to fetch data packet until a valid one found"""

        def fget():
            data = False
            while not data:
                data = self._fetch_rt_packet()
                time.sleep(self._rem.DELAY)
            return data

        return fget()

    def update(self):
        print(f"Listening for {', '.join(self._rem.event.get())} events")
        (
            self._rem.cache["strip_level"],
            self._rem.cache["bus_level"],
        ) = self._rem._get_levels(self._rem.public_packet)

        while self._rem.running:
            start = time.time()
            _pp = self._get_rt()
            self._rem._strip_buf, self._rem._bus_buf = self._rem._get_levels(_pp)
            self._rem._pdirty = _pp.pdirty(self._rem.public_packet)

            if self._rem.event.ldirty and self._rem.ldirty:
                self._rem.cache["strip_level"] = self._rem._strip_buf
                self._rem.cache["bus_level"] = self._rem._bus_buf
                self._rem.subject.notify("ldirty")
            if self._rem.public_packet != _pp:
                self._rem._public_packet = _pp
            if self._rem.event.pdirty and self._rem.pdirty:
                self._rem.subject.notify("pdirty")
            elapsed = time.time() - start
            if self._rem.ratelimit - elapsed > 0:
                time.sleep(self._rem.ratelimit - elapsed)
