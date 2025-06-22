"""
Custom exceptions for the Leneda API client.
"""


class LenedaException(Exception):
    """Base exception for all Leneda API client exceptions."""

    pass


class UnauthorizedException(LenedaException):
    """Raised when API authentication fails (401 Unauthorized)."""

    pass


class ForbiddenException(LenedaException):
    """Raised when access is forbidden (403 Forbidden), typically due to geoblocking or other access restrictions."""

    pass


class MeteringPointNotFoundException(LenedaException):
    """Raised when a metering point is not found."""

    pass
