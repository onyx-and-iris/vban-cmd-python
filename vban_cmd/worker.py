import logging
import threading
import time

from .enums import NBS
from .error import VBANCMDConnectionError, VBANCMDPacketError
from .packet.enums import SubProtocols
from .packet.headers import (
    HEADER_SIZE,
    VbanRTPacket,
    VbanRTResponseHeader,
    VbanRTSubscribeHeader,
)
from .packet.nbs0 import VbanRTPacketNBS0
from .packet.nbs1 import VbanRTPacketNBS1

logger = logging.getLogger(__name__)


class Subscriber(threading.Thread):
    """fire a subscription packet every 10 seconds"""

    def __init__(self, remote, stop_event):
        super().__init__(name='subscriber', daemon=False)
        self._remote = remote
        self.stop_event = stop_event
        self.logger = logger.getChild(self.__class__.__name__)

    def run(self):
        while not self.stopped():
            for nbs in NBS:
                sub_packet = VbanRTSubscribeHeader().to_bytes(
                    nbs, self._remote._get_next_framecounter()
                )
                self._remote.sock.sendto(
                    sub_packet, (self._remote.host, self._remote.port)
                )

            self.wait_until_stopped(10)
        self.logger.debug(f'terminating {self.name} thread')

    def stopped(self):
        return self.stop_event.is_set()

    def wait_until_stopped(self, timeout, period=0.2):
        must_end = time.time() + timeout
        while time.time() < must_end:
            if self.stopped():
                break
            time.sleep(period)


class Producer(threading.Thread):
    """Continously send job queue to the Updater thread at a rate of self._remote.ratelimit."""

    def __init__(self, remote, queue, stop_event):
        super().__init__(name='producer', daemon=False)
        self._remote = remote
        self.queue = queue
        self.stop_event = stop_event
        self.logger = logger.getChild(self.__class__.__name__)
        self._remote._public_packets = [None] * (max(NBS) + 1)
        _pp = self._get_rt()
        self._remote._public_packets[_pp.nbs] = _pp
        (
            self._remote.cache['strip_level'],
            self._remote.cache['bus_level'],
        ) = self._remote.public_packets[NBS.zero].levels

    def _get_rt(self) -> VbanRTPacket:
        """Attempt to fetch data packet until a valid one found"""
        while True:
            try:
                data, _ = self._remote.sock.recvfrom(2048)
                if len(data) < HEADER_SIZE:
                    continue
            except TimeoutError as e:
                self.logger.exception(f'{type(e).__name__}: {e}')
                raise VBANCMDConnectionError(
                    f'timeout waiting for response from {self._remote.host}:{self._remote.port}'
                ) from e

            try:
                header = VbanRTResponseHeader.from_bytes(data[:HEADER_SIZE])
            except VBANCMDPacketError as e:
                match e.protocol:
                    case SubProtocols.SERVICE:
                        # Silently ignore periodic SERVICE packets unrelated to vban-cmd
                        pass
                    case _:
                        self.logger.debug(f'Error parsing response packet: {e}')
                continue

            match header.format_nbs:
                case NBS.zero:
                    return VbanRTPacketNBS0.from_bytes(
                        nbs=NBS.zero, kind=self._remote.kind, data=data
                    )

                case NBS.one:
                    return VbanRTPacketNBS1.from_bytes(
                        nbs=NBS.one, kind=self._remote.kind, data=data
                    )

    def stopped(self):
        return self.stop_event.is_set()

    def run(self):
        while not self.stopped():
            pdirty = ldirty = False
            _pp = self._get_rt()
            match _pp.nbs:
                case NBS.zero:
                    ldirty = _pp.ldirty(
                        self._remote.cache['strip_level'],
                        self._remote.cache['bus_level'],
                    )
                    pdirty = _pp.pdirty(self._remote.public_packets[NBS.zero])
                case NBS.one:
                    pdirty = True

            if pdirty or ldirty:
                self._remote._public_packets[_pp.nbs] = _pp
            self._remote._pdirty = pdirty
            self._remote._ldirty = ldirty

            if self._remote.event.pdirty:
                self.queue.put('pdirty')
            if self._remote.event.ldirty:
                self.queue.put('ldirty')
        self.logger.debug(f'terminating {self.name} thread')
        self.queue.put(None)


class Updater(threading.Thread):
    """
    continously updates the public packet

    notifies observers of event updates
    """

    def __init__(self, remote, queue):
        super().__init__(name='updater', daemon=True)
        self._remote = remote
        self.queue = queue
        self.logger = logger.getChild(self.__class__.__name__)
        self._remote._strip_comp = [False] * (self._remote.kind.num_strip_levels)
        self._remote._bus_comp = [False] * (self._remote.kind.num_bus_levels)

    def run(self):
        """
        Continously update observers of dirty states.

        Generate _strip_comp, _bus_comp and update level cache if ldirty.
        """
        while event := self.queue.get():
            if event == 'pdirty' and self._remote.pdirty:
                self._remote.subject.notify(event)
            elif event == 'ldirty' and self._remote.ldirty:
                self._remote._strip_comp, self._remote._bus_comp = (
                    self._remote._public_packets[NBS.zero]._strip_comp,
                    self._remote._public_packets[NBS.zero]._bus_comp,
                )
                (
                    self._remote.cache['strip_level'],
                    self._remote.cache['bus_level'],
                ) = self._remote.public_packets[NBS.zero].levels
                self._remote.subject.notify(event)
        self.logger.debug(f'terminating {self.name} thread')
