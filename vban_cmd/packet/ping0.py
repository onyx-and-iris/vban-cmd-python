from dataclasses import dataclass
from enum import Enum

from .headers import VbanPingHeader

# VBAN PING bitType constants
VBANPING_TYPE_RECEPTOR = 0x00000001  # Simple receptor
VBANPING_TYPE_TRANSMITTER = 0x00000002  # Simple Transmitter
VBANPING_TYPE_RECEPTORSPOT = 0x00000004  # SPOT receptor
VBANPING_TYPE_TRANSMITTERSPOT = 0x00000008  # SPOT transmitter
VBANPING_TYPE_VIRTUALDEVICE = 0x00000010  # Virtual Device
VBANPING_TYPE_VIRTUALMIXER = 0x00000020  # Virtual Mixer
VBANPING_TYPE_MATRIX = 0x00000040  # MATRIX
VBANPING_TYPE_DAW = 0x00000080  # Workstation
VBANPING_TYPE_SERVER = 0x01000000  # VBAN SERVER

# VBAN PING bitfeature constants
VBANPING_FEATURE_AUDIO = 0x00000001
VBANPING_FEATURE_AOIP = 0x00000002
VBANPING_FEATURE_VOIP = 0x00000004
VBANPING_FEATURE_SERIAL = 0x00000100
VBANPING_FEATURE_MIDI = 0x00000300
VBANPING_FEATURE_FRAME = 0x00001000
VBANPING_FEATURE_TXT = 0x00010000


class VbanServerType(Enum):
    """VBAN server types detected from PONG responses"""

    UNKNOWN = 0
    VOICEMEETER = VBANPING_TYPE_VIRTUALMIXER
    MATRIX = VBANPING_TYPE_MATRIX


@dataclass
class VbanPing0Payload:
    """Represents the VBAN PING0 payload structure as defined in the VBAN protocol documentation."""

    def __init__(self):
        self.bit_type = VBANPING_TYPE_RECEPTOR
        self.bit_feature = VBANPING_FEATURE_TXT
        self.bit_feature_ex = 0x00000000
        self.preferred_rate = 48000
        self.min_rate = 8000
        self.max_rate = 192000
        self.color_rgb = 0x00FF0000
        self.version = b'\x01\x02\x03\x04'
        self.gps_position = b'\x00' * 8
        self.user_position = b'\x00' * 8
        self.lang_code = b'EN\x00\x00\x00\x00\x00\x00'
        self.reserved = b'\x00' * 8
        self.reserved_ex = b'\x00' * 64
        self.distant_ip = b'\x00' * 32
        self.distant_port = 0
        self.distant_reserved = 0
        self.device_name = b'VBAN-CMD-Python\x00'.ljust(64, b'\x00')
        self.manufacturer_name = b'Python-VBAN\x00'.ljust(64, b'\x00')
        self.application_name = b'vban-cmd\x00'.ljust(64, b'\x00')
        self.host_name = b'localhost\x00'.ljust(64, b'\x00')
        self.user_name = b'Python User\x00'.ljust(128, b'\x00')
        self.user_comment = b'VBAN CMD Python Client\x00'.ljust(128, b'\x00')

    @classmethod
    def to_bytes(cls) -> bytes:
        """Convert payload to bytes"""
        payload = cls()

        data = bytearray()
        data.extend(payload.bit_type.to_bytes(4, 'little'))
        data.extend(payload.bit_feature.to_bytes(4, 'little'))
        data.extend(payload.bit_feature_ex.to_bytes(4, 'little'))
        data.extend(payload.preferred_rate.to_bytes(4, 'little'))
        data.extend(payload.min_rate.to_bytes(4, 'little'))
        data.extend(payload.max_rate.to_bytes(4, 'little'))
        data.extend(payload.color_rgb.to_bytes(4, 'little'))
        data.extend(payload.version)
        data.extend(payload.gps_position)
        data.extend(payload.user_position)
        data.extend(payload.lang_code)
        data.extend(payload.reserved)
        data.extend(payload.reserved_ex)
        data.extend(payload.distant_ip)
        data.extend(payload.distant_port.to_bytes(2, 'little'))
        data.extend(payload.distant_reserved.to_bytes(2, 'little'))
        data.extend(payload.device_name)
        data.extend(payload.manufacturer_name)
        data.extend(payload.application_name)
        data.extend(payload.host_name)
        data.extend(payload.user_name)
        data.extend(payload.user_comment)
        return bytes(data)

    @classmethod
    def create_packet(cls, framecounter: int) -> bytes:
        """Creates a complete PING packet with header and payload."""
        data = bytearray()
        data.extend(VbanPingHeader.to_bytes(framecounter))
        data.extend(cls.to_bytes())
        return bytes(data)

    @staticmethod
    def detect_server_type(pong_data: bytes) -> VbanServerType:
        """Detect server type from PONG response packet.

        Args:
            pong_data: Raw bytes from PONG response packet

        Returns:
            VbanServerType enum indicating the detected server type
        """
        try:
            if len(pong_data) >= 32:
                frame_counter_bytes = pong_data[28:32]
                frame_counter = int.from_bytes(frame_counter_bytes, 'little')

                if frame_counter == VbanServerType.MATRIX.value:
                    return VbanServerType.MATRIX
                elif frame_counter == VbanServerType.VOICEMEETER.value:
                    return VbanServerType.VOICEMEETER

            return VbanServerType.UNKNOWN

        except Exception:
            return VbanServerType.UNKNOWN
