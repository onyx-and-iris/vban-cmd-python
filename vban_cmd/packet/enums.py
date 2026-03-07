from enum import Flag


class SubProtocols(Flag):
    """Sub Protocols - Bit flags that can be combined"""

    AUDIO = 0x00
    SERIAL = 0x20
    TEXT = 0x40
    SERVICE = 0x60
    MASK = 0xE0


class ServiceTypes(Flag):
    """Service Types - Bit flags that can be combined"""

    PING = 0
    PONG = 0
    CHATUTF8 = 1
    RTPACKETREGISTER = 32
    RTPACKET = 33
    REQUESTREPLY = 0x02  # A Matrix reply
    FNCT_REPLY = 0x80  # An RTPacket reply


class StreamTypes(Flag):
    """Stream Types - Bit flags that can be combined"""

    ASCII = 0x00
    UTF8 = 0x10
    WCHAR = 0x20


class ChannelModes(Flag):
    """Channel Modes - Bit flags that can be combined"""

    MUTE = 0x00000001
    SOLO = 0x00000002
    MONO = 0x00000004
    MC = 0x00000008

    AMIX = 0x00000010
    REPEAT = 0x00000020
    BMIX = 0x00000030
    COMPOSITE = 0x00000040
    TVMIX = 0x00000050
    UPMIX21 = 0x00000060
    UPMIX41 = 0x00000070
    UPMIX61 = 0x00000080
    CENTERONLY = 0x00000090
    LFEONLY = 0x000000A0
    REARONLY = 0x000000B0

    MASK = 0x000000F0

    ON = 0x00000100  # eq.on
    CROSS = 0x00000200
    AB = 0x00000800  # eq.ab

    BUSA = 0x00001000
    BUSA1 = 0x00001000
    BUSA2 = 0x00002000
    BUSA3 = 0x00004000
    BUSA4 = 0x00008000
    BUSA5 = 0x00080000

    BUSB = 0x00010000
    BUSB1 = 0x00010000
    BUSB2 = 0x00020000
    BUSB3 = 0x00040000

    PAN0 = 0x00000000
    PANCOLOR = 0x00100000
    PANMOD = 0x00200000
    PANMASK = 0x00F00000

    POSTFX_R = 0x01000000
    POSTFX_D = 0x02000000
    POSTFX1 = 0x04000000
    POSTFX2 = 0x08000000

    SEL = 0x10000000
    MONITOR = 0x20000000
