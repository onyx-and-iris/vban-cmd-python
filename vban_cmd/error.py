from .packet.enums import ServiceTypes, SubProtocols


class VBANCMDError(Exception):
    """Base VBANCMD Exception class."""


class VBANCMDConnectionError(VBANCMDError):
    """Exception raised when connection/timeout errors occur"""


class VBANCMDPacketError(VBANCMDError):
    """Exception raised when packet parsing errors occur"""

    def __init__(self, message: str, protocol: SubProtocols, type_: ServiceTypes):
        super().__init__(message)
        self.protocol = protocol
        self.type = type_
