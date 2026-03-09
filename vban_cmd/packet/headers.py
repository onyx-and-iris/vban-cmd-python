import struct
from dataclasses import dataclass

from vban_cmd.enums import NBS
from vban_cmd.error import VBANCMDPacketError
from vban_cmd.kinds import KindMapClass

from .enums import ServiceTypes, StreamTypes, SubProtocols

PINGPONG_PACKET_SIZE = 704  # Size of the PING/PONG header + payload in bytes
MAX_PACKET_SIZE = 1436
HEADER_SIZE = 4 + 1 + 1 + 1 + 1 + 16

STREAMNAME_MAX_LENGTH = 16
# fmt: off
BPS_OPTS = [
    0, 110, 150, 300, 600, 1200, 2400, 4800, 9600, 14400, 19200, 31250,
    38400, 57600, 115200, 128000, 230400, 250000, 256000, 460800, 921600,
    1000000, 1500000, 2000000, 3000000,
]
# fmt: on


@dataclass
class VbanPingHeader:
    """Represents the header of a PING packet"""

    name: str = 'PING0'
    format_sr: int = SubProtocols.SERVICE.value
    format_nbs: int = 0
    format_nbc: int = ServiceTypes.PING.value
    format_bit: int = 0
    framecounter: int = 0

    @property
    def vban(self) -> bytes:
        return b'VBAN'

    @property
    def streamname(self) -> bytes:
        return self.name.encode('ascii')[:STREAMNAME_MAX_LENGTH].ljust(
            STREAMNAME_MAX_LENGTH, b'\x00'
        )

    @classmethod
    def to_bytes(cls, framecounter: int = 0) -> bytes:
        """Creates the PING header bytes only."""
        header = cls(framecounter=framecounter)

        return struct.pack(
            '<4s4B16sI',
            header.vban,
            header.format_sr,
            header.format_nbs,
            header.format_nbc,
            header.format_bit,
            header.streamname,
            header.framecounter,
        )


@dataclass
class VbanPongHeader:
    """Represents the header of a PONG response packet"""

    name: str = 'PING0'
    format_sr: int = SubProtocols.SERVICE.value
    format_nbs: int = 0
    format_nbc: int = ServiceTypes.PONG.value
    format_bit: int = 0
    framecounter: int = 0

    @property
    def vban(self) -> bytes:
        return b'VBAN'

    @property
    def streamname(self) -> bytes:
        return self.name.encode('ascii')[:STREAMNAME_MAX_LENGTH].ljust(
            STREAMNAME_MAX_LENGTH, b'\x00'
        )

    @classmethod
    def from_bytes(cls, data: bytes):
        """Parse a PONG response packet from bytes."""
        parsed = _parse_vban_service_header(data)

        # PONG responses use the same service type as PING (0x00)
        # and are identified by having payload data
        if parsed['format_nbc'] != ServiceTypes.PONG.value:
            raise VBANCMDPacketError(
                f'Not a PONG response packet: {parsed["format_nbc"]:02x}',
                protocol=SubProtocols(parsed['format_sr'] & SubProtocols.MASK.value),
                type_=ServiceTypes(parsed['format_nbc']),
            )

        return cls(**parsed)

    @classmethod
    def is_pong_response(cls, data: bytes) -> bool:
        """Check if packet is a PONG response by analyzing the actual response format."""
        try:
            parsed = _parse_vban_service_header(data)

            # Validate this is a service protocol packet with PING/PONG service type
            if parsed['format_nbc'] != ServiceTypes.PONG.value:
                return False

            if parsed['name'] not in ['PING0', 'VBAN Service']:
                return False

            # PONG should have payload data (same size as PING)
            return len(data) >= PINGPONG_PACKET_SIZE

        except (ValueError, Exception):
            return False


@dataclass
class VbanRTPacket:
    """Represents the header of an incoming RTPacket"""

    nbs: NBS
    _kind: KindMapClass
    _voicemeeterType: bytes
    _reserved: bytes
    _buffersize: bytes
    _voicemeeterVersion: bytes
    _optionBits: bytes
    _samplerate: bytes

    @property
    def voicemeetertype(self) -> str:
        """returns voicemeeter type as a string"""
        return ['', 'basic', 'banana', 'potato'][
            int.from_bytes(self._voicemeeterType, 'little')
        ]

    @property
    def voicemeeterversion(self) -> tuple:
        """returns voicemeeter version as a tuple"""
        return tuple(self._voicemeeterVersion[i] for i in range(3, -1, -1))

    @property
    def samplerate(self) -> int:
        """returns samplerate as an int"""
        return int.from_bytes(self._samplerate, 'little')


@dataclass
class VbanRTSubscribeHeader:
    """Represents the header of an RT subscription packet"""

    _nbs: NBS = NBS.zero
    name: str = 'Register-RTP'
    timeout: int = 15

    @property
    def vban(self) -> bytes:
        return b'VBAN'

    @property
    def sr(self) -> int:
        return SubProtocols.SERVICE.value

    @property
    def nbs(self) -> int:
        return self._nbs.value & 0xFF

    @property
    def nbc(self) -> int:
        return ServiceTypes.RTPACKETREGISTER.value

    @property
    def bit(self) -> int:
        return self.timeout & 0xFF

    @property
    def streamname(self) -> bytes:
        return self.name.encode()[:STREAMNAME_MAX_LENGTH].ljust(
            STREAMNAME_MAX_LENGTH, b'\x00'
        )

    @classmethod
    def to_bytes(cls, nbs: NBS, framecounter: int) -> bytes:
        header = cls(_nbs=nbs)

        return struct.pack(
            '<4s4B16sI',
            header.vban,
            header.sr,
            header.nbs,
            header.nbc,
            header.bit,
            header.streamname,
            framecounter,
        )


@dataclass
class VbanRTRequestHeader:
    """Represents the header of an RT request packet"""

    name: str
    bps: int
    channel: int
    framecounter: int = 0

    def __post_init__(self):
        if self.bps not in BPS_OPTS:
            raise ValueError(
                f'Invalid bps value: {self.bps}. Must be one of {BPS_OPTS}'
            )
        self.bps_index = BPS_OPTS.index(self.bps)

    @property
    def vban(self) -> bytes:
        return b'VBAN'

    @property
    def sr(self) -> int:
        return self.bps_index | SubProtocols.TEXT.value

    @property
    def nbs(self) -> int:
        return 0

    @property
    def nbc(self) -> int:
        return self.channel

    @property
    def bit(self) -> int:
        return StreamTypes.UTF8.value

    @property
    def streamname(self) -> bytes:
        return self.name.encode()[:STREAMNAME_MAX_LENGTH].ljust(
            STREAMNAME_MAX_LENGTH, b'\x00'
        )

    @classmethod
    def to_bytes(cls, name: str, bps: int, channel: int, framecounter: int) -> bytes:
        header = cls(name=name, bps=bps, channel=channel, framecounter=framecounter)

        return struct.pack(
            '<4s4B16sI',
            header.vban,
            header.sr,
            header.nbs,
            header.nbc,
            header.bit,
            header.streamname,
            header.framecounter,
        )

    @classmethod
    def encode_with_payload(
        cls, name: str, bps: int, channel: int, framecounter: int, payload: str
    ) -> bytes:
        """Creates the complete packet with header and payload."""
        return cls.to_bytes(name, bps, channel, framecounter) + payload.encode()


def _parse_vban_service_header(data: bytes) -> dict:
    """Common parsing and validation for VBAN service protocol headers."""
    if len(data) < HEADER_SIZE:
        raise ValueError('Data is too short to be a valid VBAN header')

    if data[:4] != b'VBAN':
        raise ValueError('Invalid VBAN magic bytes')

    format_sr = data[4]
    format_nbs = data[5]
    format_nbc = data[6]
    format_bit = data[7]

    # Verify this is a service protocol packet
    protocol = format_sr & SubProtocols.MASK.value
    if protocol != SubProtocols.SERVICE.value:
        raise VBANCMDPacketError(
            f'Invalid protocol in service header: {protocol:02x}',
            protocol=SubProtocols(protocol),
        )

    # Extract stream name and frame counter
    name = data[8:24].rstrip(b'\x00').decode('utf-8', errors='ignore')
    framecounter = int.from_bytes(data[24:28], 'little')

    return {
        'format_sr': format_sr,
        'format_nbs': format_nbs,
        'format_nbc': format_nbc,
        'format_bit': format_bit,
        'name': name,
        'framecounter': framecounter,
    }


@dataclass
class VbanRTResponseHeader:
    """Represents the header of an RT response packet"""

    name: str = 'Voicemeeter-RTP'
    format_sr: int = SubProtocols.SERVICE.value
    format_nbs: int = 0
    format_nbc: int = ServiceTypes.RTPACKET.value
    format_bit: int = 0
    framecounter: int = 0

    @property
    def vban(self) -> bytes:
        return b'VBAN'

    @property
    def streamname(self) -> bytes:
        return self.name.encode()[:STREAMNAME_MAX_LENGTH].ljust(
            STREAMNAME_MAX_LENGTH, b'\x00'
        )

    @classmethod
    def from_bytes(cls, data: bytes):
        """Parse a VbanResponseHeader from bytes."""
        parsed = _parse_vban_service_header(data)

        # Validate this is an RTPacket response
        if parsed['format_nbc'] != ServiceTypes.RTPACKET.value:
            raise VBANCMDPacketError(
                f'Not an RTPacket response packet: {parsed["format_nbc"]:02x}',
                protocol=SubProtocols(parsed['format_sr'] & SubProtocols.MASK.value),
                type_=ServiceTypes(parsed['format_nbc']),
            )

        return cls(**parsed)


@dataclass
class VbanMatrixResponseHeader:
    """Represents the header of a matrix response packet"""

    name: str = 'Request Reply'
    format_sr: int = SubProtocols.SERVICE.value
    format_nbs: int = ServiceTypes.FNCT_REPLY.value
    format_nbc: int = ServiceTypes.REQUESTREPLY.value
    format_bit: int = 0
    framecounter: int = 0

    @property
    def vban(self) -> bytes:
        return b'VBAN'

    @property
    def streamname(self) -> bytes:
        return self.name.encode()[:STREAMNAME_MAX_LENGTH].ljust(
            STREAMNAME_MAX_LENGTH, b'\x00'
        )

    @classmethod
    def from_bytes(cls, data: bytes):
        """Parse a matrix response packet from bytes."""
        parsed = _parse_vban_service_header(data)

        # Validate this is a service reply packet (dual encoding scheme)
        if parsed['format_nbs'] != ServiceTypes.FNCT_REPLY.value:
            raise VBANCMDPacketError(
                f'Not a service reply packet: {parsed["format_nbs"]:02x}',
                protocol=SubProtocols(parsed['format_sr'] & SubProtocols.MASK.value),
                type_=ServiceTypes(parsed['format_nbs']),
            )

        if parsed['format_nbc'] != ServiceTypes.REQUESTREPLY.value:
            raise VBANCMDPacketError(
                f'Not a request reply packet: {parsed["format_nbc"]:02x}',
                protocol=SubProtocols(parsed['format_sr'] & SubProtocols.MASK.value),
                type_=ServiceTypes(parsed['format_nbc']),
            )

        return cls(**parsed)

    @classmethod
    def extract_payload(cls, data: bytes) -> str:
        """Extract the text payload from a matrix response packet."""
        if len(data) <= HEADER_SIZE:
            return ''

        payload_bytes = data[HEADER_SIZE:]
        return payload_bytes.rstrip(b'\x00').decode('utf-8', errors='ignore')

    @classmethod
    def parse_response(cls, data: bytes) -> tuple['VbanMatrixResponseHeader', str]:
        """Parse a complete matrix response packet returning header and payload."""
        header = cls.from_bytes(data)
        payload = cls.extract_payload(data)
        return header, payload
