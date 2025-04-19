"""
Leneda API client package.

This package provides a client for the Leneda API, which allows access to
energy consumption and production data for electricity and gas.
"""

# Import the client class
from .client import LenedaClient

# Import the data models
from .models import (
    AggregatedMeteringData,
    AggregatedMeteringValue,
    MeteringData,
    MeteringValue,
)

# Import the OBIS code constants
from .obis_codes import ObisCode

# Import the version
from .version import __version__

# Define what's available when using "from leneda import *"
__all__ = [
    "LenedaClient",
    "ObisCode",
    "MeteringValue",
    "MeteringData",
    "AggregatedMeteringValue",
    "AggregatedMeteringData",
    "__version__",
]
