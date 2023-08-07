class VBANCMDError(Exception):
    """Base VBANCMD Exception class. Raised when general errors occur"""

    def __init__(self, msg):
        self.message = msg
        super().__init__(self.message)

    def __str__(self):
        return f"{type(self).__name__}: {self.message}"


class VBANCMDConnectionError(VBANCMDError):
    """Exception raised when connection/timeout errors occur"""
