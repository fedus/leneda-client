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
import logging
import os
import sys
from datetime import datetime, timedelta
from typing import Optional

import matplotlib.pyplot as plt
import pandas as pd

from leneda import LenedaClient
from leneda.models import AggregatedMeteringData, MeteringData
from leneda.obis_codes import ObisCode

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("leneda_advanced_example")


def parse_arguments():
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
        default="LU-METERING_POINT1",
        help="Metering point code (default: LU-METERING_POINT1)",
    )
    parser.add_argument(
        "--example",
        type=int,
        choices=[1, 2, 3, 4],
        default=0,
        help="Run a specific example (1-4) or all if not specified",
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
        default=datetime.now().year,
        help=f"Year for analysis (default: {datetime.now().year})",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=50.0,
        help="Anomaly detection threshold percentage (default: 50.0)",
    )
    parser.add_argument(
        "--save-plots",
        action="store_true",
        help="Save plots to files instead of displaying them",
    )
    parser.add_argument(
        "--output-dir",
        default="./plots",
        help="Directory to save plots (default: ./plots)",
    )
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")

    return parser.parse_args()


def get_credentials(args):
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


def convert_to_dataframe(metering_data: MeteringData) -> pd.DataFrame:
    """Convert MeteringData to a pandas DataFrame for analysis."""
    data = [
        {
            "timestamp": item.started_at,
            "value": item.value,
            "unit": metering_data.unit,
            "metering_point": metering_data.metering_point_code,
            "obis_code": metering_data.obis_code,
            "type": item.type,
            "version": item.version,
            "calculated": item.calculated,
        }
        for item in metering_data.items
    ]

    df = pd.DataFrame(data)
    df.set_index("timestamp", inplace=True)
    return df


def convert_aggregated_to_dataframe(
    aggregated_data: AggregatedMeteringData,
) -> pd.DataFrame:
    """Convert AggregatedMeteringData to a pandas DataFrame for analysis."""
    data = [
        {
            "start_date": item.started_at,
            "end_date": item.ended_at,
            "value": item.value,
            "unit": aggregated_data.unit,
            "calculated": item.calculated,
        }
        for item in aggregated_data.aggregated_time_series
    ]

    df = pd.DataFrame(data)
    df.set_index("start_date", inplace=True)
    return df


def plot_consumption_data(df: pd.DataFrame, title: str, save_path: Optional[str] = None) -> None:
    """Plot consumption data from a DataFrame."""
    plt.figure(figsize=(12, 6))
    plt.plot(df.index, df["value"], marker="o", linestyle="-", markersize=4)
    plt.title(title)
    plt.xlabel("Time")
    plt.ylabel(f"Consumption ({df['unit'].iloc[0]})")
    plt.grid(True)
    plt.tight_layout()

    if save_path:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path)
        logger.info(f"Plot saved to {save_path}")
    else:
        plt.show()

    plt.close()


def compare_consumption_periods(
    client: LenedaClient,
    metering_point: str,
    period1_start: datetime,
    period1_end: datetime,
    period2_start: datetime,
    period2_end: datetime,
    save_path: Optional[str] = None,
) -> None:
    """Compare consumption data between two time periods."""
    # Get data for period 1
    period1_data = client.get_metering_data(
        metering_point_code=metering_point,
        obis_code=ObisCode.ELEC_CONSUMPTION_ACTIVE,
        start_date_time=period1_start,
        end_date_time=period1_end,
    )

    # Get data for period 2
    period2_data = client.get_metering_data(
        metering_point_code=metering_point,
        obis_code=ObisCode.ELEC_CONSUMPTION_ACTIVE,
        start_date_time=period2_start,
        end_date_time=period2_end,
    )

    # Convert to DataFrames
    df1 = convert_to_dataframe(period1_data)
    df2 = convert_to_dataframe(period2_data)

    # Resample to daily data for better comparison
    daily1 = df1.resample("D").sum()
    daily2 = df2.resample("D").sum()

    # Calculate total consumption
    total1 = df1["value"].sum()
    total2 = df2["value"].sum()

    # Calculate average consumption
    avg1 = df1["value"].mean()
    avg2 = df2["value"].mean()

    # Calculate percentage difference
    pct_diff = ((total2 - total1) / total1) * 100 if total1 > 0 else 0

    # Print comparison
    period1_str = f"{period1_start.strftime('%Y-%m-%d')} to {period1_end.strftime('%Y-%m-%d')}"
    period2_str = f"{period2_start.strftime('%Y-%m-%d')} to {period2_end.strftime('%Y-%m-%d')}"

    print("\nConsumption Comparison:")
    print(f"Period 1 ({period1_str}):")
    print(f"  - Total: {total1:.2f} {df1['unit'].iloc[0]}")
    print(f"  - Average: {avg1:.2f} {df1['unit'].iloc[0]}")

    print(f"\nPeriod 2 ({period2_str}):")
    print(f"  - Total: {total2:.2f} {df2['unit'].iloc[0]}")
    print(f"  - Average: {avg2:.2f} {df2['unit'].iloc[0]}")

    print("\nComparison:")
    print(f"  - Absolute difference: {total2 - total1:.2f} {df1['unit'].iloc[0]}")
    print(f"  - Percentage difference: {pct_diff:.2f}%")

    # Plot comparison
    plt.figure(figsize=(12, 6))

    plt.subplot(2, 1, 1)
    plt.bar(range(len(daily1)), daily1["value"], label=f"Period 1 ({period1_str})")
    plt.xticks(range(len(daily1)), [d.strftime("%a %d") for d in daily1.index], rotation=45)
    plt.ylabel(f"Daily Consumption ({df1['unit'].iloc[0]})")
    plt.legend()
    plt.grid(True, alpha=0.3)

    plt.subplot(2, 1, 2)
    plt.bar(
        range(len(daily2)),
        daily2["value"],
        label=f"Period 2 ({period2_str})",
        color="orange",
    )
    plt.xticks(range(len(daily2)), [d.strftime("%a %d") for d in daily2.index], rotation=45)
    plt.ylabel(f"Daily Consumption ({df2['unit'].iloc[0]})")
    plt.legend()
    plt.grid(True, alpha=0.3)

    plt.tight_layout()

    if save_path:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path)
        logger.info(f"Plot saved to {save_path}")
    else:
        plt.show()

    plt.close()


def analyze_monthly_trends(
    client: LenedaClient,
    metering_point: str,
    year: int,
    save_path: Optional[str] = None,
) -> None:
    """Analyze monthly consumption trends for a specific year."""
    # Get monthly aggregated data for the year
    start_date = datetime(year, 1, 1)
    end_date = datetime(year, 12, 31)

    monthly_data = client.get_aggregated_metering_data(
        metering_point_code=metering_point,
        obis_code=ObisCode.ELEC_CONSUMPTION_ACTIVE,
        start_date=start_date,
        end_date=end_date,
        aggregation_level="Month",
        transformation_mode="Accumulation",
    )

    # Convert to DataFrame
    df = convert_aggregated_to_dataframe(monthly_data)

    # Print monthly consumption
    print(f"\nMonthly Consumption for {year}:")
    for idx, row in df.iterrows():
        month_name = idx.strftime("%B")
        print(f"  - {month_name}: {row['value']:.2f} {row['unit']}")

    # Calculate statistics
    total = df["value"].sum()
    average = df["value"].mean()
    max_month = df["value"].idxmax().strftime("%B")
    min_month = df["value"].idxmin().strftime("%B")

    print("\nYearly Statistics:")
    print(f"  - Total consumption: {total:.2f} {df['unit'].iloc[0]}")
    print(f"  - Average monthly consumption: {average:.2f} {df['unit'].iloc[0]}")
    print(
        f"  - Highest consumption month: {max_month} ({df['value'].max():.2f} {df['unit'].iloc[0]})"
    )
    print(
        f"  - Lowest consumption month: {min_month} ({df['value'].min():.2f} {df['unit'].iloc[0]})"
    )

    # Plot monthly consumption
    plt.figure(figsize=(12, 6))
    plt.bar(range(len(df)), df["value"], color="green")
    plt.xticks(range(len(df)), [d.strftime("%b") for d in df.index], rotation=0)
    plt.title(f"Monthly Electricity Consumption for {year}")
    plt.xlabel("Month")
    plt.ylabel(f"Consumption ({df['unit'].iloc[0]})")
    plt.grid(True, axis="y", alpha=0.3)
    plt.tight_layout()

    if save_path:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path)
        logger.info(f"Plot saved to {save_path}")
    else:
        plt.show()

    plt.close()


def detect_consumption_anomalies(
    client: LenedaClient,
    metering_point: str,
    start_date: datetime,
    end_date: datetime,
    threshold_pct: float = 50.0,
    save_path: Optional[str] = None,
) -> None:
    """Detect anomalies in consumption data based on percentage deviation from the mean."""
    # Get hourly consumption data
    consumption_data = client.get_metering_data(
        metering_point_code=metering_point,
        obis_code=ObisCode.ELEC_CONSUMPTION_ACTIVE,
        start_date_time=start_date,
        end_date_time=end_date,
    )

    # Convert to DataFrame
    df = convert_to_dataframe(consumption_data)

    # Calculate statistics
    mean = df["value"].mean()
    std = df["value"].std()
    threshold = mean * (threshold_pct / 100)

    # Detect anomalies
    anomalies = df[abs(df["value"] - mean) > threshold].copy()

    print("\nAnomaly Detection:")
    print(f"  - Period: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    print(f"  - Average consumption: {mean:.2f} {df['unit'].iloc[0]}")
    print(f"  - Standard deviation: {std:.2f} {df['unit'].iloc[0]}")
    print(
        f"  - Threshold for anomaly: {threshold:.2f} {df['unit'].iloc[0]} ({threshold_pct}% of mean)"
    )
    print(f"  - Number of anomalies detected: {len(anomalies)}")

    if not anomalies.empty:
        print("\nTop 5 Anomalies:")
        # Sort by absolute deviation from mean
        anomalies["deviation"] = abs(anomalies["value"] - mean)
        anomalies = anomalies.sort_values("deviation", ascending=False)

        for idx, row in anomalies.head(5).iterrows():
            deviation_pct = (row["deviation"] / mean) * 100
            print(
                f"  - {idx.strftime('%Y-%m-%d %H:%M')}: {row['value']:.2f} {row['unit']} "
                f"(Deviation: {deviation_pct:.2f}%)"
            )

        # Plot the data with anomalies highlighted
        plt.figure(figsize=(12, 6))
        plt.plot(
            df.index,
            df["value"],
            marker=".",
            linestyle="-",
            markersize=2,
            label="Normal",
        )
        plt.scatter(anomalies.index, anomalies["value"], color="red", s=50, label="Anomaly")
        plt.axhline(y=mean, color="green", linestyle="--", label=f"Mean ({mean:.2f})")
        plt.axhline(
            y=mean + threshold,
            color="orange",
            linestyle="--",
            label=f"Upper Threshold ({mean + threshold:.2f})",
        )
        plt.axhline(
            y=mean - threshold,
            color="orange",
            linestyle="--",
            label=f"Lower Threshold ({mean - threshold:.2f})",
        )

        plt.title("Electricity Consumption with Anomalies")
        plt.xlabel("Time")
        plt.ylabel(f"Consumption ({df['unit'].iloc[0]})")
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()

        if save_path:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            plt.savefig(save_path)
            logger.info(f"Plot saved to {save_path}")
        else:
            plt.show()

        plt.close()


def main():
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
    year = args.year
    threshold = args.threshold
    save_plots = args.save_plots
    output_dir = args.output_dir

    # Initialize the client
    client = LenedaClient(api_key, energy_id, debug=args.debug)

    try:
        # Run all examples or a specific one based on the command-line argument
        if example_num == 0 or example_num == 1:
            # Example 1: Get and visualize hourly electricity consumption for the last week
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)

            print(
                f"\nExample 1: Visualizing hourly electricity consumption for the last {days} days"
            )
            consumption_data = client.get_metering_data(
                metering_point_code=metering_point,
                obis_code=ObisCode.ELEC_CONSUMPTION_ACTIVE,
                start_date_time=start_date,
                end_date_time=end_date,
            )

            # Convert to DataFrame and plot
            df = convert_to_dataframe(consumption_data)
            plot_consumption_data(
                df,
                f"Hourly Electricity Consumption ({start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')})",
                save_path=(
                    os.path.join(output_dir, "hourly_consumption.png") if save_plots else None
                ),
            )

        if example_num == 0 or example_num == 2:
            # Example 2: Compare consumption between two weeks
            current_week_end = datetime.now()
            current_week_start = current_week_end - timedelta(days=7)
            previous_week_end = current_week_start
            previous_week_start = previous_week_end - timedelta(days=7)

            print("\nExample 2: Comparing consumption between two weeks")
            compare_consumption_periods(
                client,
                metering_point,
                previous_week_start,
                previous_week_end,
                current_week_start,
                current_week_end,
                save_path=(
                    os.path.join(output_dir, "weekly_comparison.png") if save_plots else None
                ),
            )

        if example_num == 0 or example_num == 3:
            # Example 3: Analyze monthly trends for the specified year
            print(f"\nExample 3: Analyzing monthly trends for {year}")
            analyze_monthly_trends(
                client,
                metering_point,
                year,
                save_path=(
                    os.path.join(output_dir, f"monthly_trends_{year}.png") if save_plots else None
                ),
            )

        if example_num == 0 or example_num == 4:
            # Example 4: Detect consumption anomalies for the last 30 days
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)

            print("\nExample 4: Detecting consumption anomalies for the last 30 days")
            detect_consumption_anomalies(
                client,
                metering_point,
                start_date,
                end_date,
                threshold_pct=threshold,
                save_path=(os.path.join(output_dir, "anomalies.png") if save_plots else None),
            )

    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)


if __name__ == "__main__":
    main()
