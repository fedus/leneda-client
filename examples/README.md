# Leneda API Client Examples

This directory contains example scripts demonstrating how to use the Leneda API client.

## Prerequisites

Before running these examples, make sure you have installed the Leneda API client:

```bash
# python-venv commands included for convenience
python3 -m venv ./venv
. venv/bin/activate
pip install -U setuptools pip
pip install leneda-client
```

## Usage

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
