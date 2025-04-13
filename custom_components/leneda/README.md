# Leneda Energy Integration for Home Assistant

This integration allows you to monitor your energy consumption and production from the Leneda energy platform in Luxembourg.

## Features

- Track electricity consumption and production
- Monitor gas consumption
- Yearly energy tracking (resets on January 1st)
- Compatible with Home Assistant Energy Dashboard
- Support for multiple accounts and metering points

## Installation

1. Copy the `custom_components/leneda` directory to your Home Assistant's `custom_components` directory.
2. Restart Home Assistant.
3. Go to Settings -> Devices & Services -> Add Integration.
4. Search for "Leneda Energy".
5. Enter your API token, Energy ID, and metering point IDs.

## Configuration

### API Token and Energy ID

You can obtain your API token and Energy ID from the Leneda platform. These are required to authenticate with the Leneda API.

### Metering Points

Enter your metering point IDs separated by commas (e.g., `MP001,MP002`). These are the unique identifiers for your energy meters.

### Adding New Metering Points

You can add new metering points in two ways:

1. **Using existing credentials**: If you want to add a new metering point to an existing configuration, go to Settings -> Devices & Services -> Leneda Energy -> Add Metering Point. Select "Use existing credentials" and enter the Energy ID and new metering point IDs.

2. **With new credentials**: If you want to add a new metering point with a different API token and Energy ID, go to Settings -> Devices & Services -> Leneda Energy -> Add Metering Point. Uncheck "Use existing credentials" and enter the new API token, Energy ID, and metering point IDs.

## Usage

Once configured, the integration will create the following sensors for each metering point:

- Electricity Consumption (kWh)
- Electricity Production (kWh)
- Gas Consumption (m³)

These sensors can be used in the Home Assistant Energy Dashboard or in automations and templates.

## Data Updates

The integration updates data every hour. Note that Leneda data may have a one-day lag, so the most recent data available will be from the previous day.

## How It Works

The integration uses the Leneda client library to fetch aggregated monthly data for the current year. It then sums up these monthly values to calculate the yearly total. This approach:

1. Handles the one-day lag in Leneda data
2. Provides a clean yearly total that resets on January 1st
3. Works well with Home Assistant's Energy Dashboard

## Troubleshooting

If you encounter issues with the integration:

1. Check that your API token and Energy ID are correct.
2. Verify that your metering point IDs are correct.
3. Check the Home Assistant logs for any error messages.
4. Ensure that your Home Assistant instance has internet access to reach the Leneda API.

## License

This integration is licensed under the MIT License. 