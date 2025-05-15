# Leneda API Client

[![PyPI version](https://img.shields.io/pypi/v/leneda-client.svg)](https://pypi.org/project/leneda-client/)
[![Python Versions](https://img.shields.io/pypi/pyversions/leneda-client)](https://pypi.org/project/leneda-client/)
[![License](https://img.shields.io/github/license/fedus/leneda-client)](https://github.com/fedus/leneda-client/blob/main/LICENSE)


A Python client for interacting with the Leneda energy data platform API.

PLEASE NOTE: As long as the library is in a version below 1.0.0, breaking changes
may also be introduced between minor version bumps.

## Overview

This client provides a simple interface to the Leneda API, which allows users to:

- Retrieve metering data for specific time ranges
- Get aggregated metering data (hourly, daily, weekly, monthly, or total)
- Create metering data access requests
- Use predefined OBIS code constants for easy reference

## Installation

```bash
pip install leneda-client
```

## Trying it out

```bash
$ export LENEDA_ENERGY_ID='LUXE-xx-yy-1234'
$ export LENEDA_API_KEY='YOUR-API-KEY'
$ python examples/basic_usage.py --metering-point LU0000012345678901234000000000000
Example 1: Getting hourly electricity consumption data for the last 7 days
Retrieved 514 consumption measurements
Unit: kW
Interval length: PT15M
Metering point: LU0000012345678901234000000000000
OBIS code: ObisCode.ELEC_CONSUMPTION_ACTIVE

First 3 measurements:
Time: 2025-04-18T13:30:00+00:00, Value: 0.048 kW, Type: Actual, Version: 2, Calculated: False
Time: 2025-04-18T13:45:00+00:00, Value: 0.08 kW, Type: Actual, Version: 2, Calculated: False
Time: 2025-04-18T14:00:00+00:00, Value: 0.08 kW, Type: Actual, Version: 2, Calculated: False

Example 2: Getting monthly aggregated electricity consumption for 2025
Retrieved 4 monthly aggregations
Unit: kWh

Monthly consumption:
Period: 2024-12 to 2025-01, Value: 30.858 kWh, Calculated: False
Period: 2025-01 to 2025-02, Value: 148.985 kWh, Calculated: False
Period: 2025-02 to 2025-03, Value: 44.619 kWh, Calculated: False
Period: 2025-03 to 2025-04, Value: 29.662 kWh, Calculated: False
```
