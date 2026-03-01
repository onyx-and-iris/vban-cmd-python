from dataclasses import dataclass

from vban_cmd.enums import NBS
from vban_cmd.kinds import KindMapClass

VBAN_PROTOCOL_TXT = 0x40
VBAN_PROTOCOL_SERVICE = 0x60

VBAN_SERVICE_RTPACKETREGISTER = 32
VBAN_SERVICE_RTPACKET = 33
VBAN_SERVICE_MASK = 0xE0
VBAN_PROTOCOL_MASK = 0xE0
VBAN_SERVICE_REQUESTREPLY = 0x02
VBAN_SERVICE_FNCT_REPLY = 0x02

MAX_PACKET_SIZE = 1436
HEADER_SIZE = 4 + 1 + 1 + 1 + 1 + 16


@dataclass
class VbanPacket:
    """Represents the header of an incoming VBAN data packet"""

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
class VbanSubscribeHeader:
    """Represents the header of a subscription packet"""

    nbs: NBS = NBS.zero
    name: str = 'Register-RTP'
    timeout: int = 15

    @property
    def vban(self) -> bytes:
        return b'VBAN'

    @property
    def format_sr(self) -> bytes:
        return VBAN_PROTOCOL_SERVICE.to_bytes(1, 'little')

    @property
    def format_nbs(self) -> bytes:
        return (self.nbs.value & 0xFF).to_bytes(1, 'little')

    @property
    def format_nbc(self) -> bytes:
        return VBAN_SERVICE_RTPACKETREGISTER.to_bytes(1, 'little')

    @property
    def format_bit(self) -> bytes:
        return (self.timeout & 0xFF).to_bytes(1, 'little')

    @property
    def streamname(self) -> bytes:
        return self.name.encode('ascii') + bytes(16 - len(self.name))

    @classmethod
    def to_bytes(cls, nbs: NBS, framecounter: int) -> bytes:
        header = cls(nbs=nbs)

        data = bytearray()
        data.extend(header.vban)
        data.extend(header.format_sr)
        data.extend(header.format_nbs)
        data.extend(header.format_nbc)
        data.extend(header.format_bit)
        data.extend(header.streamname)
        data.extend(framecounter.to_bytes(4, 'little'))
        return bytes(data)


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
    protocol = format_sr & VBAN_PROTOCOL_MASK
    if protocol != VBAN_PROTOCOL_SERVICE:
        raise ValueError(f'Not a service protocol packet: {protocol:02x}')

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
class VbanResponseHeader:
    """Represents the header of a response packet"""

    name: str = 'Voicemeeter-RTP'
    format_sr: int = VBAN_PROTOCOL_SERVICE
    format_nbs: int = 0
    format_nbc: int = VBAN_SERVICE_RTPACKET
    format_bit: int = 0
    framecounter: int = 0

    @property
    def vban(self) -> bytes:
        return b'VBAN'

    @property
    def streamname(self) -> bytes:
        return self.name.encode('ascii') + bytes(16 - len(self.name))

    @classmethod
    def from_bytes(cls, data: bytes):
        """Parse a VbanResponseHeader from bytes."""
        parsed = _parse_vban_service_header(data)

        # Validate this is an RTPacket response
        if parsed['format_nbc'] != VBAN_SERVICE_RTPACKET:
            raise ValueError(
                f'Not an RTPacket response packet: {parsed["format_nbc"]:02x}'
            )

        return cls(**parsed)


@dataclass
class VbanMatrixResponseHeader:
    """Represents the header of a matrix response packet"""

    name: str = 'Request Reply'
    format_sr: int = VBAN_PROTOCOL_SERVICE
    format_nbs: int = VBAN_SERVICE_FNCT_REPLY
    format_nbc: int = VBAN_SERVICE_REQUESTREPLY
    format_bit: int = 0
    framecounter: int = 0

    @property
    def vban(self) -> bytes:
        return b'VBAN'

    @property
    def streamname(self) -> bytes:
        return self.name.encode('ascii')[:16].ljust(16, b'\x00')

    @classmethod
    def from_bytes(cls, data: bytes):
        """Parse a matrix response packet from bytes."""
        parsed = _parse_vban_service_header(data)

        # Validate this is a service reply packet
        if parsed['format_nbs'] != VBAN_SERVICE_FNCT_REPLY:
            raise ValueError(f'Not a service reply packet: {parsed["format_nbs"]:02x}')

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


@dataclass
class VbanRequestHeader:
    """Represents the header of a request packet"""

    name: str
    bps_index: int
    channel: int
    framecounter: int = 0

    @property
    def vban(self) -> bytes:
        return b'VBAN'

    @property
    def sr(self) -> bytes:
        return (VBAN_PROTOCOL_TXT + self.bps_index).to_bytes(1, 'little')

    @property
    def nbs(self) -> bytes:
        return (0).to_bytes(1, 'little')

    @property
    def nbc(self) -> bytes:
        return (self.channel).to_bytes(1, 'little')

    @property
    def bit(self) -> bytes:
        return (0x10).to_bytes(1, 'little')

    @property
    def streamname(self) -> bytes:
        return self.name.encode() + bytes(16 - len(self.name))

    @classmethod
    def to_bytes(
        cls, name: str, bps_index: int, channel: int, framecounter: int
    ) -> bytes:
        header = cls(
            name=name, bps_index=bps_index, channel=channel, framecounter=framecounter
        )

        data = bytearray()
        data.extend(header.vban)
        data.extend(header.sr)
        data.extend(header.nbs)
        data.extend(header.nbc)
        data.extend(header.bit)
        data.extend(header.streamname)
        data.extend(header.framecounter.to_bytes(4, 'little'))
        return bytes(data)

    @classmethod
    def encode_with_payload(
        cls, name: str, bps_index: int, channel: int, framecounter: int, payload: str
    ) -> bytes:
        """Creates the complete packet with header and payload."""
        return cls.to_bytes(name, bps_index, channel, framecounter) + payload.encode()
