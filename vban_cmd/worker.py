import socket
import threading
import time

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
                print(f"Unable to resolve hostname {self._remote.ip}")
                self._remote.socks[Socket.register].close()
                raise e


class Updater(threading.Thread):
    """
    continously updates the public packet

    notifies observers of event updates
    """

    def __init__(self, remote):
        super().__init__(name="updater", target=self.update, daemon=True)
        self._remote = remote
        self._remote.socks[Socket.response].bind(
            (socket.gethostbyname(socket.gethostname()), self._remote.port)
        )
        self.packet_expected = VbanRtPacketHeader()
        self._remote._public_packet = self._get_rt()

    def _get_rt(self) -> VbanRtPacket:
        """Attempt to fetch data packet until a valid one found"""

        while True:
            data, _ = self._remote.socks[Socket.response].recvfrom(2048)
            # check for packet data
            if len(data) > HEADER_SIZE:
                # check if packet is of type rt packet response
                if self.packet_expected.header == data[: HEADER_SIZE - 4]:
                    return VbanRtPacket(data)
            time.sleep(self._remote.DELAY)

    def update(self):
        print(f"Listening for {', '.join(self._remote.event.get())} events")
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
