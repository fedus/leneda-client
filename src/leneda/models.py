"""
Data models for the Leneda API responses.

This module provides typed data classes for the various responses from the Leneda API,
making it easier to work with the data in a type-safe manner.
"""

import logging
from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum
from typing import Any, Dict, List, Optional

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


@dataclass
class SharingGroup:
    """A sharing group returned by the Leneda API."""

    id: str
    contract_number: str
    type: str
    owner_energy_id: str
    manager_energy_id: str
    start_date: date
    end_date: Optional[date] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SharingGroup":
        """Create a SharingGroup from a dictionary."""
        try:
            return cls(
                id=data["id"],
                contract_number=data["contractNumber"],
                type=data["type"],
                owner_energy_id=data["ownerEnergyId"],
                manager_energy_id=data["managerEnergyId"],
                start_date=date.fromisoformat(data["startDate"]),
                end_date=(date.fromisoformat(data["endDate"]) if data.get("endDate") else None),
            )
        except KeyError as e:
            logger.error(f"Missing key in sharing group API response: {e}")
            logger.debug(f"API response data: {data}")
            raise
        except Exception as e:
            logger.error(f"Error parsing sharing group: {e}")
            logger.debug(f"API response data: {data}")
            raise

    def to_dict(self) -> Dict[str, Any]:
        """Convert the SharingGroup to a dictionary."""
        return {
            "id": self.id,
            "contractNumber": self.contract_number,
            "type": self.type,
            "ownerEnergyId": self.owner_energy_id,
            "managerEnergyId": self.manager_energy_id,
            "startDate": self.start_date.isoformat(),
            "endDate": self.end_date.isoformat() if self.end_date else None,
        }


@dataclass
class SharingGroupsPage:
    """Paginated sharing groups response."""

    content: List[SharingGroup] = field(default_factory=list)
    has_next_page: bool = False
    number: int = 1
    size: int = 10
    total_elements: int = 0
    total_pages: int = 0

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SharingGroupsPage":
        """Create a SharingGroupsPage from a dictionary."""
        try:
            groups = []
            for item_data in data.get("content", []):
                try:
                    groups.append(SharingGroup.from_dict(item_data))
                except Exception as e:
                    logger.warning(f"Skipping invalid sharing group: {e}")
                    logger.debug(f"Invalid sharing group data: {item_data}")

            return cls(
                content=groups,
                has_next_page=bool(data.get("hasNextPage", False)),
                number=int(data.get("number", 1)),
                size=int(data.get("size", 10)),
                total_elements=int(data.get("totalElements", len(groups))),
                total_pages=int(data.get("totalPages", 1)),
            )
        except Exception as e:
            logger.error(f"Error creating SharingGroupsPage: {e}")
            logger.debug(f"API response data: {data}")
            raise

    def to_dict(self) -> Dict[str, Any]:
        """Convert the SharingGroupsPage to a dictionary."""
        return {
            "content": [group.to_dict() for group in self.content],
            "hasNextPage": self.has_next_page,
            "number": self.number,
            "size": self.size,
            "totalElements": self.total_elements,
            "totalPages": self.total_pages,
        }
