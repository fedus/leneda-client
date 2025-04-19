"""
OBIS (Object Identification System) codes for the Leneda API.

This module provides constants for the various OBIS codes used in the Leneda platform,
making it easier to reference the correct codes when retrieving energy data.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List


@dataclass
class ObisCodeInfo:
    """Information about an OBIS code."""

    code: str
    unit: str
    service_type: str
    description: str


class ObisCode(str, Enum):
    """OBIS codes for all energy types."""

    # Electricity Consumption
    ELEC_CONSUMPTION_ACTIVE = "1-1:1.29.0"  # Measured active consumption (kW)
    ELEC_CONSUMPTION_REACTIVE = "1-1:3.29.0"  # Measured reactive consumption (kVAR)

    # Consumption covered by production sharing groups
    ELEC_CONSUMPTION_COVERED_LAYER1 = "1-65:1.29.1"  # Layer 1 sharing Group (AIR)
    ELEC_CONSUMPTION_COVERED_LAYER2 = "1-65:1.29.3"  # Layer 2 sharing Group (ACR/ACF/AC1)
    ELEC_CONSUMPTION_COVERED_LAYER3 = "1-65:1.29.2"  # Layer 3 sharing Group (CEL)
    ELEC_CONSUMPTION_COVERED_LAYER4 = "1-65:1.29.4"  # Layer 4 sharing Group (APS/CER/CEN)
    ELEC_CONSUMPTION_REMAINING = (
        "1-65:1.29.9"  # Remaining consumption after sharing invoiced by supplier
    )

    # Electricity Production
    ELEC_PRODUCTION_ACTIVE = "1-1:2.29.0"  # Measured active production (kW)
    ELEC_PRODUCTION_REACTIVE = "1-1:4.29.0"  # Measured reactive production (kVAR)

    # Production shared within sharing groups
    ELEC_PRODUCTION_SHARED_LAYER1 = "1-65:2.29.1"  # Layer 1 sharing Group (AIR)
    ELEC_PRODUCTION_SHARED_LAYER2 = "1-65:2.29.3"  # Layer 2 sharing Group (ACR/ACF/AC1)
    ELEC_PRODUCTION_SHARED_LAYER3 = "1-65:2.29.2"  # Layer 3 sharing Group (CEL)
    ELEC_PRODUCTION_SHARED_LAYER4 = "1-65:2.29.4"  # Layer 4 sharing Group (APS/CER/CEN)
    ELEC_PRODUCTION_REMAINING = "1-65:2.29.9"  # Remaining production after sharing sold to market

    # Gas Consumption
    GAS_CONSUMPTION_VOLUME = "7-1:99.23.15"  # Measured consumed volume (m³)
    GAS_CONSUMPTION_STANDARD_VOLUME = "7-1:99.23.17"  # Measured consumed standard volume (Nm³)
    GAS_CONSUMPTION_ENERGY = "7-20:99.33.17"  # Measured consumed energy (kWh)


# Complete mapping of all OBIS codes to their details
OBIS_CODES: Dict[str, ObisCodeInfo] = {
    # Electricity Consumption
    ObisCode.ELEC_CONSUMPTION_ACTIVE: ObisCodeInfo(
        ObisCode.ELEC_CONSUMPTION_ACTIVE,
        "kW",
        "Consumption",
        "Measured active consumption",
    ),
    ObisCode.ELEC_CONSUMPTION_REACTIVE: ObisCodeInfo(
        ObisCode.ELEC_CONSUMPTION_REACTIVE,
        "kVAR",
        "Consumption",
        "Measured reactive consumption",
    ),
    ObisCode.ELEC_CONSUMPTION_COVERED_LAYER1: ObisCodeInfo(
        ObisCode.ELEC_CONSUMPTION_COVERED_LAYER1,
        "kW",
        "Consumption",
        "Consumption covered by production of layer 1 sharing Group (AIR)",
    ),
    ObisCode.ELEC_CONSUMPTION_COVERED_LAYER2: ObisCodeInfo(
        ObisCode.ELEC_CONSUMPTION_COVERED_LAYER2,
        "kW",
        "Consumption",
        "Consumption covered by production of layer 2 sharing Group (ACR/ACF/AC1)",
    ),
    ObisCode.ELEC_CONSUMPTION_COVERED_LAYER3: ObisCodeInfo(
        ObisCode.ELEC_CONSUMPTION_COVERED_LAYER3,
        "kW",
        "Consumption",
        "Consumption covered by production of layer 3 sharing Group (CEL)",
    ),
    ObisCode.ELEC_CONSUMPTION_COVERED_LAYER4: ObisCodeInfo(
        ObisCode.ELEC_CONSUMPTION_COVERED_LAYER4,
        "kW",
        "Consumption",
        "Consumption covered by production of layer 4 sharing Group (APS/CER/CEN)",
    ),
    ObisCode.ELEC_CONSUMPTION_REMAINING: ObisCodeInfo(
        ObisCode.ELEC_CONSUMPTION_REMAINING,
        "kW",
        "Consumption",
        "Remaining consumption after sharing invoiced by supplier",
    ),
    # Electricity Production
    ObisCode.ELEC_PRODUCTION_ACTIVE: ObisCodeInfo(
        ObisCode.ELEC_PRODUCTION_ACTIVE, "kW", "Production", "Measured active production"
    ),
    ObisCode.ELEC_PRODUCTION_REACTIVE: ObisCodeInfo(
        ObisCode.ELEC_PRODUCTION_REACTIVE,
        "kVAR",
        "Consumption",
        "Measured reactive production",
    ),
    ObisCode.ELEC_PRODUCTION_SHARED_LAYER1: ObisCodeInfo(
        ObisCode.ELEC_PRODUCTION_SHARED_LAYER1,
        "kW",
        "Production",
        "Production shared within layer 1 sharing Group (AIR)",
    ),
    ObisCode.ELEC_PRODUCTION_SHARED_LAYER2: ObisCodeInfo(
        ObisCode.ELEC_PRODUCTION_SHARED_LAYER2,
        "kW",
        "Production",
        "Production shared within layer 2 sharing Group (ACR/ACF/AC1)",
    ),
    ObisCode.ELEC_PRODUCTION_SHARED_LAYER3: ObisCodeInfo(
        ObisCode.ELEC_PRODUCTION_SHARED_LAYER3,
        "kW",
        "Production",
        "Production shared within layer 3 sharing Group (CEL)",
    ),
    ObisCode.ELEC_PRODUCTION_SHARED_LAYER4: ObisCodeInfo(
        ObisCode.ELEC_PRODUCTION_SHARED_LAYER4,
        "kW",
        "Production",
        "Production shared within layer 4 sharing Group (APS/CER/CEN)",
    ),
    ObisCode.ELEC_PRODUCTION_REMAINING: ObisCodeInfo(
        ObisCode.ELEC_PRODUCTION_REMAINING,
        "kW",
        "Production",
        "Remaining production after sharing sold to market",
    ),
    # Gas Consumption
    ObisCode.GAS_CONSUMPTION_VOLUME: ObisCodeInfo(
        ObisCode.GAS_CONSUMPTION_VOLUME, "m³", "Consumption", "Measured consumed volume"
    ),
    ObisCode.GAS_CONSUMPTION_STANDARD_VOLUME: ObisCodeInfo(
        ObisCode.GAS_CONSUMPTION_STANDARD_VOLUME,
        "Nm³",
        "Consumption",
        "Measured consumed standard volume",
    ),
    ObisCode.GAS_CONSUMPTION_ENERGY: ObisCodeInfo(
        ObisCode.GAS_CONSUMPTION_ENERGY, "kWh", "Consumption", "Measured consumed energy"
    ),
}


def get_obis_info(obis_code: str) -> ObisCodeInfo:
    """
    Get information about an OBIS code.

    Args:
        obis_code: The OBIS code to look up

    Returns:
        Information about the OBIS code

    Raises:
        KeyError: If the OBIS code is not found

    Example:
        >>> info = get_obis_info(ObisCode.ELEC_CONSUMPTION_ACTIVE)
        >>> print(info.unit)
        'kW'
    """
    return OBIS_CODES[obis_code]


def get_unit(obis_code: str) -> str:
    """
    Get the unit of measurement for an OBIS code.

    Args:
        obis_code: The OBIS code to look up

    Returns:
        The unit of measurement

    Raises:
        KeyError: If the OBIS code is not found

    Example:
        >>> unit = get_unit(ObisCode.ELEC_CONSUMPTION_ACTIVE)
        >>> print(unit)
        'kW'
    """
    return OBIS_CODES[obis_code].unit


def list_all_obis_codes() -> List[ObisCodeInfo]:
    """
    Get a list of all OBIS codes and their information.

    Returns:
        A list of all OBIS code information

    Example:
        >>> codes = list_all_obis_codes()
        >>> print(len(codes))
        17
    """
    return list(OBIS_CODES.values())


def list_obis_codes_by_service_type(service_type: str) -> List[ObisCodeInfo]:
    """
    Get a list of OBIS codes filtered by service type.

    Args:
        service_type: The service type to filter by (e.g., "Consumption", "Production")

    Returns:
        A list of OBIS code information matching the service type

    Example:
        >>> codes = list_obis_codes_by_service_type("Production")
        >>> print(len(codes))
        7
    """
    return [info for info in OBIS_CODES.values() if info.service_type == service_type]
