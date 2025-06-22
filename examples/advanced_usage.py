"""
Advanced usage examples for the Leneda API client.

This script demonstrates more complex use cases of the Leneda API client,
including data analysis, visualization, and error handling.
It accepts API credentials via command-line arguments or environment variables.

Environment variables:
LENEDA_API_KEY: Your Leneda API key
LENEDA_ENERGY_ID: Your Energy ID

Usage:
python advanced_usage.py --api-key YOUR_API_KEY --energy-id YOUR_ENERGY_ID --metering-point LU-METERING_POINT1
python advanced_usage.py --api-key YOUR_API_KEY --energy-id YOUR_ENERGY_ID --metering-point LU-METERING_POINT1 --example 2
"""

import argparse
import asyncio
import logging
import os
import sys
from datetime import datetime, timedelta
from typing import Optional

import matplotlib.pyplot as plt
import pandas as pd

from leneda import LenedaClient
from leneda.models import MeteringData
from leneda.obis_codes import ObisCode

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("leneda_advanced_example")


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Leneda API Client Advanced Usage Example")

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
        "--example",
        type=int,
        default=0,
        help="Example number to run (0 for all, 1-3 for specific examples)",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=7,
        help="Number of days to retrieve data for (default: 7)",
    )
    parser.add_argument(
        "--year",
        type=int,
        default=None,
        help="Year to analyze (default: current year)",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.0,
        help="Threshold for anomaly detection (default: 0.0)",
    )
    parser.add_argument(
        "--save-plots",
        action="store_true",
        help="Save plots to files instead of displaying them",
    )
    parser.add_argument(
        "--output-dir",
        default="plots",
        help="Directory to save plots (default: plots)",
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


def convert_to_dataframe(data: MeteringData) -> pd.DataFrame:
    """Convert MeteringData to a pandas DataFrame."""
    df = pd.DataFrame(
        [
            {
                "timestamp": item.started_at,
                "value": item.value,
                "type": item.type,
                "calculated": item.calculated,
            }
            for item in data.items
        ]
    )
    df.set_index("timestamp", inplace=True)
    return df


def plot_consumption_data(
    df: pd.DataFrame, title: str, unit: str, save_path: Optional[str] = None
) -> None:
    """Plot consumption data."""
    plt.figure(figsize=(12, 6))
    plt.plot(df.index, df["value"], label="Consumption")
    plt.title(title)
    plt.xlabel("Time")
    plt.ylabel(f"Consumption ({unit})")
    plt.grid(True)
    plt.legend()

    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path)
        plt.close()
    else:
        plt.show()


def detect_anomalies(df: pd.DataFrame, threshold: float) -> pd.DataFrame:
    """Detect anomalies in the data using a simple threshold-based approach."""
    mean = df["value"].mean()
    std = df["value"].std()
    df["anomaly"] = abs(df["value"] - mean) > (threshold * std)
    return df


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
    example_num = args.example
    days = args.days
    threshold = args.threshold
    save_plots = args.save_plots
    output_dir = args.output_dir

    # Initialize the client
    client = LenedaClient(api_key, energy_id, debug=args.debug)

    # Run all examples or a specific one based on the command-line argument
    if example_num == 0 or example_num == 1:
        # Example 1: Get and visualize hourly electricity consumption for the last week
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        print(
            f"\nExample 1: Visualizing hourly electricity consumption (kWh) for the last {days} days"
        )
        consumption_data = await client.get_metering_data(
            metering_point_code=metering_point,
            obis_code=ObisCode.ELEC_CONSUMPTION_ACTIVE,
            start_date_time=start_date,
            end_date_time=end_date,
        )

        # Convert to DataFrame and compute kWh for each 15-min period
        df = convert_to_dataframe(consumption_data)
        df["kWh"] = df["value"] * 0.25  # 15 min = 0.25 h
        # Resample to hourly energy (sum of 4 periods per hour)
        hourly_kwh = df["kWh"].resample("H").sum()
        plt.figure(figsize=(12, 6))
        plt.plot(hourly_kwh.index, hourly_kwh.values, label="Hourly Energy Consumption")
        plt.title(
            f"Hourly Electricity Consumption (kWh) ({start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')})"
        )
        plt.xlabel("Time")
        plt.ylabel("Consumption (kWh)")
        plt.grid(True)
        plt.legend()
        if save_plots:
            os.makedirs(output_dir, exist_ok=True)
            plt.savefig(os.path.join(output_dir, "hourly_consumption_kwh.png"))
            plt.close()
        else:
            plt.show()

    if example_num == 0 or example_num == 2:
        # Example 2: Analyze daily consumption patterns (average power in kW)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)  # Last 30 days

        print("\nExample 2: Analyzing daily average power patterns (kW)")
        consumption_data = await client.get_metering_data(
            metering_point_code=metering_point,
            obis_code=ObisCode.ELEC_CONSUMPTION_ACTIVE,
            start_date_time=start_date,
            end_date_time=end_date,
        )

        # Convert to DataFrame and analyze
        df = convert_to_dataframe(consumption_data)
        df["hour"] = df.index.hour
        df["day_of_week"] = df.index.day_name()

        # Calculate average power by hour (kW)
        hourly_avg = df.groupby("hour")["value"].mean()
        plt.figure(figsize=(12, 6))
        hourly_avg.plot(kind="bar")
        plt.title("Average Hourly Power (kW)")
        plt.xlabel("Hour of Day")
        plt.ylabel("Average Power (kW)")
        plt.grid(True)
        if save_plots:
            os.makedirs(output_dir, exist_ok=True)
            plt.savefig(os.path.join(output_dir, "hourly_patterns_kw.png"))
            plt.close()
        else:
            plt.show()

    if example_num == 0 or example_num == 3:
        # Example 3: Detect anomalies in consumption data
        end_date = datetime.now()
        start_date = end_date - timedelta(days=90)  # Last 90 days

        print("\nExample 3: Detecting anomalies in consumption data")
        consumption_data = await client.get_metering_data(
            metering_point_code=metering_point,
            obis_code=ObisCode.ELEC_CONSUMPTION_ACTIVE,
            start_date_time=start_date,
            end_date_time=end_date,
        )

        # Convert to DataFrame and detect anomalies
        df = convert_to_dataframe(consumption_data)
        df = detect_anomalies(df, threshold)

        # Plot the data with anomalies highlighted
        plt.figure(figsize=(12, 6))
        plt.plot(df.index, df["value"], label="Consumption")
        anomalies = df[df["anomaly"]]
        plt.scatter(
            anomalies.index,
            anomalies["value"],
            color="red",
            label="Anomalies",
            zorder=5,
        )
        plt.title(f"Electricity Consumption with Anomalies (Threshold: {threshold}σ)")
        plt.xlabel("Time")
        plt.ylabel(f"Consumption ({consumption_data.unit})")
        plt.grid(True)
        plt.legend()

        if save_plots:
            os.makedirs(output_dir, exist_ok=True)
            plt.savefig(os.path.join(output_dir, "anomalies.png"))
            plt.close()
        else:
            plt.show()


if __name__ == "__main__":
    asyncio.run(main())
