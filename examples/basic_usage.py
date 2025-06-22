"""
Basic usage examples for the Leneda API client.

This script demonstrates basic usage of the Leneda API client.
It accepts API credentials via command-line arguments or environment variables.

Environment variables:
    LENEDA_API_KEY: Your Leneda API key
    LENEDA_ENERGY_ID: Your Energy ID

Usage:
    python basic_usage.py --api-key YOUR_API_KEY --energy-id YOUR_ENERGY_ID --metering-point LU-METERING_POINT1
"""

import argparse
import asyncio
import logging
import os
import sys
from datetime import datetime, timedelta

from leneda import LenedaClient
from leneda.obis_codes import ObisCode

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("leneda_example")


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Leneda API Client Basic Usage Example")

    # API credentials
    parser.add_argument(
        "--api-key",
        help="Your Leneda API key (or set LENEDA_API_KEY environment variable)",
    )
    parser.add_argument(
        "--energy-id",
        help="Your Energy ID (or set LENEDA_ENERGY_ID environment variable)",
    )

    # Other parameters
    parser.add_argument(
        "--metering-point",
        help="Metering point code (default: LU-METERING_POINT1)",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=7,
        help="Number of days to retrieve data for (default: 7)",
    )
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")

    return parser.parse_args()


def get_credentials(args: argparse.Namespace) -> tuple[str, str]:
    """Get API credentials from arguments or environment variables."""
    api_key = args.api_key or os.environ.get("LENEDA_API_KEY")
    energy_id = args.energy_id or os.environ.get("LENEDA_ENERGY_ID")

    if not api_key:
        logger.error(
            "API key not provided. Use --api-key or set LENEDA_API_KEY environment variable."
        )
        sys.exit(1)

    if not energy_id:
        logger.error(
            "Energy ID not provided. Use --energy-id or set LENEDA_ENERGY_ID environment variable."
        )
        sys.exit(1)

    return api_key, energy_id


async def main() -> None:
    # Parse command-line arguments
    args = parse_arguments()

    # Set up debug logging if requested
    if args.debug:
        logging.getLogger("leneda").setLevel(logging.DEBUG)
        logger.setLevel(logging.DEBUG)
        logger.debug("Debug logging enabled")

    # Get API credentials
    api_key, energy_id = get_credentials(args)

    # Get other parameters
    metering_point = args.metering_point
    days = args.days

    # Initialize the client
    client = LenedaClient(api_key, energy_id, debug=args.debug)

    # Example 1: Get hourly electricity consumption data for the specified number of days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    print(f"\nExample 1: Getting hourly electricity consumption data for the last {days} days")
    consumption_data = await client.get_metering_data(
        metering_point_code=metering_point,
        obis_code=ObisCode.ELEC_CONSUMPTION_ACTIVE,
        start_date_time=start_date.strftime("%Y-%m-%dT%H:%M:%SZ"),
        end_date_time=end_date.strftime("%Y-%m-%dT%H:%M:%SZ"),
    )

    # Process and display the data
    print(f"Retrieved {len(consumption_data.items)} consumption measurements")
    print(f"Unit: {consumption_data.unit}")
    print(f"Interval length: {consumption_data.interval_length}")
    print(f"Metering point: {consumption_data.metering_point_code}")
    print(f"OBIS code: {consumption_data.obis_code}")

    # Display the first 3 items
    if consumption_data.items:
        print("\nFirst 3 measurements:")
        for item in consumption_data.items[:3]:
            print(
                f"Time: {item.started_at.isoformat()}, Value: {item.value} {consumption_data.unit}, "
                f"Type: {item.type}, Version: {item.version}, Calculated: {item.calculated}"
            )

    # Example 2: Get monthly aggregated electricity consumption for the current year
    today = datetime.now()
    start_of_year = datetime(today.year, 1, 1)

    print("\nExample 2: Getting monthly aggregated electricity consumption for the current year")
    aggregated_data = await client.get_aggregated_metering_data(
        metering_point_code=metering_point,
        obis_code=ObisCode.ELEC_CONSUMPTION_ACTIVE,
        start_date=start_of_year.strftime("%Y-%m-%d"),
        end_date=today.strftime("%Y-%m-%d"),
        aggregation_level="Month",
        transformation_mode="Accumulation",
    )

    # Process and display the data
    print(f"Retrieved {len(aggregated_data.aggregated_time_series)} monthly measurements")
    print(f"Unit: {aggregated_data.unit}")

    # Display all measurements
    if aggregated_data.aggregated_time_series:
        print("\nMonthly measurements:")
        for metering_value in aggregated_data.aggregated_time_series:
            print(
                f"Period: {metering_value.started_at.strftime('%Y-%m')}, "
                f"Value: {metering_value.value} {aggregated_data.unit}, "
                f"Calculated: {metering_value.calculated}"
            )


if __name__ == "__main__":
    asyncio.run(main())
