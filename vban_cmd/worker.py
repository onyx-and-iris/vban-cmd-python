import logging
import socket
import threading
import time
from typing import Optional

from .error import VBANCMDConnectionError
from .packet import HEADER_SIZE, SubscribeHeader, VbanRtPacket, VbanRtPacketHeader
from .util import Socket

logger = logging.getLogger(__name__)


class Subscriber(threading.Thread):
    """fire a subscription packet every 10 seconds"""

    def __init__(self, remote):
        super().__init__(name="subscriber", daemon=True)
        self._remote = remote
        self.logger = logger.getChild(self.__class__.__name__)
        self.packet = SubscribeHeader()

    def run(self):
        while self._remote.running:
            try:
                self._remote.socks[Socket.register].sendto(
                    self.packet.header,
                    (socket.gethostbyname(self._remote.ip), self._remote.port),
                )
                self.packet.framecounter = (
                    int.from_bytes(self.packet.framecounter, "little") + 1
                ).to_bytes(4, "little")
                time.sleep(10)
            except socket.gaierror as e:
                self.logger.exception(f"{type(e).__name__}: {e}")
                raise VBANCMDConnectionError(
                    f"unable to resolve hostname {self._remote.ip}"
                ) from e


class Producer(threading.Thread):
    """Continously send job queue to the Updater thread at a rate of self._remote.ratelimit."""

    def __init__(self, remote, queue):
        super().__init__(name="producer", daemon=True)
        self._remote = remote
        self.queue = queue
        self.logger = logger.getChild(self.__class__.__name__)
        self.packet_expected = VbanRtPacketHeader()
        self._remote._public_packet = self._get_rt()
        (
            self._remote.cache["strip_level"],
            self._remote.cache["bus_level"],
        ) = self._remote._get_levels(self._remote.public_packet)

    def _get_rt(self) -> VbanRtPacket:
        """Attempt to fetch data packet until a valid one found"""

        def fget():
            data = None
            while not data:
                data = self._fetch_rt_packet()
                time.sleep(self._remote.DELAY)
            return data

        return fget()

    def _fetch_rt_packet(self) -> Optional[VbanRtPacket]:
        try:
            data, _ = self._remote.socks[Socket.response].recvfrom(2048)
            # check for packet data
            if len(data) > HEADER_SIZE:
                # check if packet is of type rt packet response
                if self.packet_expected.header == data[: HEADER_SIZE - 4]:
                    return VbanRtPacket(kind=self._remote.kind, data=data)
        except TimeoutError as e:
            self.logger.exception(f"{type(e).__name__}: {e}")
            raise VBANCMDConnectionError(
                f"timeout waiting for RtPacket from {self._remote.ip}"
            ) from e

    def run(self):
        while self._remote.running:
            _pp = self._get_rt()
            pdirty = _pp.pdirty(self._remote.public_packet)
            ldirty = _pp.ldirty(
                self._remote.cache["strip_level"], self._remote.cache["bus_level"]
            )

            if pdirty or ldirty:
                self._remote._public_packet = _pp
            self._remote._pdirty = pdirty
            self._remote._ldirty = ldirty

            if self._remote.event.pdirty:
                self.queue.put("pdirty")
            if self._remote.event.ldirty:
                self.queue.put("ldirty")
            time.sleep(self._remote.ratelimit)
        self.logger.debug(f"terminating {self.name} thread")
        self.queue.put(None)


class Updater(threading.Thread):
    """
    continously updates the public packet

    notifies observers of event updates
    """

    def __init__(self, remote, queue):
        super().__init__(name="updater", daemon=True)
        self._remote = remote
        self.queue = queue
        self.logger = logger.getChild(self.__class__.__name__)
        self._remote.socks[Socket.response].settimeout(self._remote.timeout)
        self._remote.socks[Socket.response].bind(
            (socket.gethostbyname(socket.gethostname()), self._remote.port)
        )
        p_in, v_in = self._remote.kind.ins
        self._remote._strip_comp = [False] * (2 * p_in + 8 * v_in)
        self._remote._bus_comp = [False] * (self._remote.kind.num_bus * 8)

    def run(self):
        """
        Continously update observers of dirty states.

        Generate _strip_comp, _bus_comp and update level cache if ldirty.
        """
        while True:
            event = self.queue.get()
            if event is None:
                self.logger.debug(f"terminating {self.name} thread")
                break

            if event == "pdirty" and self._remote.pdirty:
                self._remote.subject.notify(event)
            elif event == "ldirty" and self._remote.ldirty:
                self._remote._strip_comp, self._remote._bus_comp = (
                    self._remote._public_packet._strip_comp,
                    self._remote._public_packet._bus_comp,
                )
                (
                    self._remote.cache["strip_level"],
                    self._remote.cache["bus_level"],
                ) = (
                    self._remote._public_packet.inputlevels,
                    self._remote._public_packet.outputlevels,
                )
                self._remote.subject.notify(event)
