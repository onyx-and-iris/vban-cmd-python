class VBANCMDError(Exception):
    """Base VBANCMD Exception class."""


class VBANCMDConnectionError(VBANCMDError):
    """Exception raised when connection/timeout errors occur"""
