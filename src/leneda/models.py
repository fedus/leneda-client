"""
Data models for the Leneda API responses.

This module provides typed data classes for the various responses from the Leneda API,
making it easier to work with the data in a type-safe manner.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List

from dateutil import parser

from .obis_codes import ObisCode

# Set up logging
logger = logging.getLogger("leneda.models")


@dataclass
class MeteringValue:
    """A single metering value from a time series."""

    value: float
    started_at: datetime
    type: str
    version: int
    calculated: bool

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MeteringValue":
        """Create a MeteringValue from a dictionary."""
        try:
            # Handle the required fields
            value = float(data["value"])

            # Parse ISO format string to datetime using dateutil
            started_at = parser.isoparse(data["startedAt"])

            # Get type, version and calculated
            type_value = data["type"]
            version = int(data["version"])
            calculated = bool(data["calculated"])

            return cls(
                value=value,
                started_at=started_at,
                type=type_value,
                version=version,
                calculated=calculated,
            )
        except KeyError as e:
            # Log the error and the data that caused it
            logger.error(f"Missing key in API response: {e}")
            logger.debug(f"API response data: {data}")
            raise
        except Exception as e:
            logger.error(f"Error parsing metering value: {e}")
            logger.debug(f"API response data: {data}")
            raise


@dataclass
class MeteringData:
    """Metering data for a specific metering point and OBIS code."""

    metering_point_code: str
    obis_code: ObisCode
    interval_length: str
    unit: str
    items: List[MeteringValue] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MeteringData":
        """Create a MeteringData from a dictionary."""
        try:
            # Log the raw data for debugging
            logger.debug(f"Creating MeteringData from: {data}")

            # Use values from the response
            metering_point_code_value = data["meteringPointCode"]
            obis_code_value = ObisCode(data["obisCode"])

            # Extract items safely
            items_data = data.get("items", [])
            items = []

            for item_data in items_data:
                try:
                    item = MeteringValue.from_dict(item_data)
                    items.append(item)
                except Exception as e:
                    logger.warning(f"Skipping invalid item: {e}")
                    logger.debug(f"Invalid item data: {item_data}")

            return cls(
                metering_point_code=metering_point_code_value,
                obis_code=obis_code_value,
                interval_length=data.get("intervalLength", ""),
                unit=data.get("unit", ""),
                items=items,
            )
        except KeyError as e:
            logger.error(f"Missing key in API response: {e}")
            logger.debug(f"API response data: {data}")
            raise
        except Exception as e:
            logger.error(f"Error creating MeteringData: {e}")
            logger.debug(f"API response data: {data}")
            raise

    def to_dict(self) -> Dict[str, Any]:
        """Convert the MeteringData to a dictionary."""
        return {
            "meteringPointCode": self.metering_point_code,
            "obisCode": self.obis_code,
            "intervalLength": self.interval_length,
            "unit": self.unit,
            "items": [
                {
                    "value": item.value,
                    "startedAt": item.started_at.isoformat(),
                    "type": item.type,
                    "version": item.version,
                    "calculated": item.calculated,
                }
                for item in self.items
            ],
        }

    def __str__(self) -> str:
        """Return a string representation of the MeteringData."""
        return (
            f"MeteringData(metering_point_code={self.metering_point_code}, "
            f"obis_code={self.obis_code}, unit={self.unit}, "
            f"items_count={len(self.items)})"
        )


@dataclass
class AggregatedMeteringValue:
    """A single aggregated metering value."""

    value: float
    started_at: datetime
    ended_at: datetime
    calculated: bool

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AggregatedMeteringValue":
        """Create an AggregatedMeteringValue from a dictionary."""
        try:
            # Handle the required fields
            value = float(data["value"])

            # Parse ISO format string to datetime using dateutil
            started_at = parser.isoparse(data["startedAt"])
            ended_at = parser.isoparse(data["endedAt"])

            # Get calculated
            calculated = bool(data["calculated"])

            return cls(
                value=value,
                started_at=started_at,
                ended_at=ended_at,
                calculated=calculated,
            )
        except KeyError as e:
            logger.error(f"Missing key in API response: {e}")
            logger.debug(f"API response data: {data}")
            raise
        except Exception as e:
            logger.error(f"Error parsing aggregated metering value: {e}")
            logger.debug(f"API response data: {data}")
            raise


@dataclass
class AggregatedMeteringData:
    """Aggregated metering data for a specific metering point and OBIS code."""

    unit: str
    aggregated_time_series: List[AggregatedMeteringValue] = field(default_factory=list)

    @classmethod
    def from_dict(
        cls,
        data: Dict[str, Any],
    ) -> "AggregatedMeteringData":
        """Create an AggregatedMeteringData from a dictionary."""
        try:
            # Log the raw data for debugging
            logger.debug(f"Creating AggregatedMeteringData from: {data}")

            # Extract items safely
            time_series_data = data.get("aggregatedTimeSeries", [])
            time_series = []

            for item_data in time_series_data:
                try:
                    item = AggregatedMeteringValue.from_dict(item_data)
                    time_series.append(item)
                except Exception as e:
                    logger.warning(f"Skipping invalid aggregated item: {e}")
                    logger.debug(f"Invalid item data: {item_data}")

            return cls(unit=data["unit"], aggregated_time_series=time_series)
        except KeyError as e:
            logger.error(f"Missing key in API response: {e}")
            logger.debug(f"API response data: {data}")
            raise
        except Exception as e:
            logger.error(f"Error creating AggregatedMeteringData: {e}")
            logger.debug(f"API response data: {data}")
            raise

    def to_dict(self) -> Dict[str, Any]:
        """Convert the AggregatedMeteringData to a dictionary."""
        return {
            "unit": self.unit,
            "aggregatedTimeSeries": [
                {
                    "value": item.value,
                    "startedAt": item.started_at.isoformat(),
                    "endedAt": item.ended_at.isoformat(),
                    "calculated": item.calculated,
                }
                for item in self.aggregated_time_series
            ],
        }

    def __str__(self) -> str:
        """Return a string representation of the AggregatedMeteringData."""
        return (
            f"AggregatedMeteringData(unit={self.unit}, "
            f"items_count={len(self.aggregated_time_series)})"
        )


class AuthenticationProbeResult(Enum):
    """Result of an authentication probe."""

    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    UNKNOWN = "UNKNOWN"
