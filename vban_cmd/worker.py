import logging
import socket
import threading
import time

from .enums import NBS
from .error import VBANCMDConnectionError
from .packet import (
    HEADER_SIZE,
    VBAN_PROTOCOL_SERVICE,
    VBAN_SERVICE_RTPACKET,
    SubscribeHeader,
    VbanRtPacket,
    VbanRtPacketHeader,
    VbanRtPacketNBS0,
    VbanRtPacketNBS1,
)
from .util import bump_framecounter

logger = logging.getLogger(__name__)


class Subscriber(threading.Thread):
    """fire a subscription packet every 10 seconds"""

    def __init__(self, remote, stop_event):
        super().__init__(name='subscriber', daemon=False)
        self._remote = remote
        self.stop_event = stop_event
        self.logger = logger.getChild(self.__class__.__name__)
        self._framecounter = 0

    def run(self):
        while not self.stopped():
            try:
                for nbs in NBS:
                    sub_packet = SubscribeHeader().to_bytes(nbs, self._framecounter)
                    self._remote.sock.sendto(
                        sub_packet, (self._remote.ip, self._remote.port)
                    )
                    self._framecounter = bump_framecounter(self._framecounter)
                    self.logger.debug(
                        f'sent subscription for NBS {nbs.name} to {self._remote.ip}:{self._remote.port}'
                    )

                self.wait_until_stopped(10)
            except socket.gaierror as e:
                self.logger.exception(f'{type(e).__name__}: {e}')
                raise VBANCMDConnectionError(
                    f'unable to resolve hostname {self._remote.ip}'
                ) from e
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
        self._remote.sock.settimeout(self._remote.timeout)
        self._remote._public_packets = [None] * (max(NBS) + 1)
        _pp = self._get_rt()
        self._remote._public_packets[_pp.nbs] = _pp
        (
            self._remote.cache['strip_level'],
            self._remote.cache['bus_level'],
        ) = self._remote._get_levels(self._remote.public_packets[NBS.zero])

    def _get_rt(self) -> VbanRtPacket:
        """Attempt to fetch data packet until a valid one found"""

        while True:
            if resp := self._fetch_rt_packet():
                return resp

    def _fetch_rt_packet(self) -> VbanRtPacket | None:
        try:
            data, _ = self._remote.sock.recvfrom(2048)
            if len(data) < HEADER_SIZE:
                return

            response_header = VbanRtPacketHeader.from_bytes(data[:HEADER_SIZE])
            if (
                response_header.format_sr != VBAN_PROTOCOL_SERVICE
                or response_header.format_nbc != VBAN_SERVICE_RTPACKET
            ):
                return

            match response_header.format_nbs:
                case NBS.zero:
                    """
                    self.logger.debug(
                        'Received NB0 RTP Packet from %s, Size: %d bytes',
                        addr,
                        len(data),
                    )
                    """

                    return VbanRtPacketNBS0.from_bytes(
                        nbs=NBS.zero, kind=self._remote.kind, data=data
                    )

                case NBS.one:
                    """
                    self.logger.debug(
                        'Received NB1 RTP Packet from %s, Size: %d bytes',
                        addr,
                        len(data),
                    )
                    """

                    return VbanRtPacketNBS1.from_bytes(
                        nbs=NBS.one, kind=self._remote.kind, data=data
                    )
            return None
        except TimeoutError as e:
            self.logger.exception(f'{type(e).__name__}: {e}')
            raise VBANCMDConnectionError(
                f'timeout waiting for RtPacket from {self._remote.ip}'
            ) from e

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
            time.sleep(self._remote.ratelimit)
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
                ) = (
                    self._remote._public_packets[NBS.zero].inputlevels,
                    self._remote._public_packets[NBS.zero].outputlevels,
                )
                self._remote.subject.notify(event)
        self.logger.debug(f'terminating {self.name} thread')
