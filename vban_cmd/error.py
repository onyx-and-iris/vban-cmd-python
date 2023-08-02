class VBANCMDError(Exception):
    """Base VBANCMD Exception class. Raised when general errors occur"""


class VBANCMDConnectionError(VBANCMDError):
    """Exception raised when connection/timeout errors occur"""
