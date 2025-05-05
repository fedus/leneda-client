"""
Tests for the Leneda API client.
"""

import json
import os
import sys
import unittest
from unittest.mock import MagicMock, patch

import requests

# Add the src directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.leneda import LenedaClient
from src.leneda.exceptions import (
    ForbiddenException,
    UnauthorizedException,
)
from src.leneda.models import (
    AggregatedMeteringData,
    AggregatedMeteringValue,
    MeteringData,
    MeteringValue,
)
from src.leneda.obis_codes import ObisCode


class TestLenedaClient(unittest.TestCase):
    """Test cases for the LenedaClient class."""

    def setUp(self):
        """Set up test fixtures."""
        self.api_key = "test_api_key"
        self.energy_id = "test_energy_id"
        self.client = LenedaClient(self.api_key, self.energy_id)

        # Sample response data
        self.sample_metering_data = {
            "meteringPointCode": "LU-METERING_POINT1",
            "obisCode": ObisCode.ELEC_CONSUMPTION_ACTIVE,
            "intervalLength": "PT15M",
            "unit": "kWh",
            "items": [
                {
                    "value": 1.234,
                    "startedAt": "2023-01-01T00:00:00Z",
                    "type": "Measured",
                    "version": 1,
                    "calculated": False,
                },
                {
                    "value": 2.345,
                    "startedAt": "2023-01-01T00:15:00Z",
                    "type": "Measured",
                    "version": 1,
                    "calculated": False,
                },
            ],
        }

        self.sample_aggregated_data = {
            "unit": "kWh",
            "aggregatedTimeSeries": [
                {
                    "value": 10.123,
                    "startedAt": "2023-01-01T00:00:00Z",
                    "endedAt": "2023-01-02T00:00:00Z",
                    "calculated": False,
                },
                {
                    "value": 12.345,
                    "startedAt": "2023-01-02T00:00:00Z",
                    "endedAt": "2023-01-03T00:00:00Z",
                    "calculated": False,
                },
            ],
        }

    @patch("requests.request")
    def test_get_time_series(self, mock_request):
        """Test getting time series data."""
        # Set up the mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = self.sample_metering_data
        mock_response.content = json.dumps(self.sample_metering_data).encode()
        mock_request.return_value = mock_response

        # Call the method
        result = self.client.get_metering_data(
            "LU-METERING_POINT1",
            ObisCode.ELEC_CONSUMPTION_ACTIVE,
            "2023-01-01T00:00:00Z",
            "2023-01-02T00:00:00Z",
        )

        # Check the result
        self.assertIsInstance(result, MeteringData)
        self.assertEqual(result.metering_point_code, "LU-METERING_POINT1")
        self.assertEqual(result.obis_code, ObisCode.ELEC_CONSUMPTION_ACTIVE)
        self.assertEqual(result.unit, "kWh")
        self.assertEqual(len(result.items), 2)

        # Check the first item
        self.assertIsInstance(result.items[0], MeteringValue)
        self.assertEqual(result.items[0].value, 1.234)
        self.assertEqual(result.items[0].started_at.isoformat(), "2023-01-01T00:00:00+00:00")
        self.assertEqual(result.items[0].type, "Measured")
        self.assertEqual(result.items[0].version, 1)
        self.assertEqual(result.items[0].calculated, False)

        # Check that the request was made correctly
        mock_request.assert_called_once_with(
            method="GET",
            url="https://api.leneda.lu/api/metering-points/LU-METERING_POINT1/time-series",
            headers={
                "X-API-KEY": "test_api_key",
                "X-ENERGY-ID": "test_energy_id",
                "Content-Type": "application/json",
            },
            params={
                "obisCode": ObisCode.ELEC_CONSUMPTION_ACTIVE.value,
                "startDateTime": "2023-01-01T00:00:00Z",
                "endDateTime": "2023-01-02T00:00:00Z",
            },
            json=None,
        )

    @patch("requests.request")
    def test_get_aggregated_time_series(self, mock_request):
        """Test getting aggregated time series data."""
        # Set up the mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = self.sample_aggregated_data
        mock_response.content = json.dumps(self.sample_aggregated_data).encode()
        mock_request.return_value = mock_response

        # Call the method
        result = self.client.get_aggregated_metering_data(
            "LU-METERING_POINT1",
            ObisCode.ELEC_CONSUMPTION_ACTIVE,
            "2023-01-01",
            "2023-01-31",
            "Day",
            "Accumulation",
        )

        # Check the result
        self.assertIsInstance(result, AggregatedMeteringData)
        self.assertEqual(result.unit, "kWh")
        self.assertEqual(len(result.aggregated_time_series), 2)

        # Check the first item
        self.assertIsInstance(result.aggregated_time_series[0], AggregatedMeteringValue)
        self.assertEqual(result.aggregated_time_series[0].value, 10.123)
        self.assertEqual(
            result.aggregated_time_series[0].started_at.isoformat(),
            "2023-01-01T00:00:00+00:00",
        )
        self.assertEqual(
            result.aggregated_time_series[0].ended_at.isoformat(),
            "2023-01-02T00:00:00+00:00",
        )
        self.assertEqual(result.aggregated_time_series[0].calculated, False)

        # Check that the request was made correctly
        mock_request.assert_called_once_with(
            method="GET",
            url="https://api.leneda.lu/api/metering-points/LU-METERING_POINT1/time-series/aggregated",
            headers={
                "X-API-KEY": "test_api_key",
                "X-ENERGY-ID": "test_energy_id",
                "Content-Type": "application/json",
            },
            params={
                "obisCode": ObisCode.ELEC_CONSUMPTION_ACTIVE.value,
                "startDate": "2023-01-01",
                "endDate": "2023-01-31",
                "aggregationLevel": "Day",
                "transformationMode": "Accumulation",
            },
            json=None,
        )

    @patch("requests.request")
    def test_request_metering_data_access(self, mock_request):
        """Test requesting metering data access."""
        # Set up the mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"requestId": "test-request-id", "status": "PENDING"}
        mock_request.return_value = mock_response

        # Call the method
        result = self.client.request_metering_data_access(
            from_energy_id="test_energy_id",
            from_name="Test User",
            metering_point_codes=["LU-METERING_POINT1"],
            obis_codes=[ObisCode.ELEC_CONSUMPTION_ACTIVE],
        )

        # Check the result
        self.assertEqual(result["requestId"], "test-request-id")
        self.assertEqual(result["status"], "PENDING")

        # Check that the request was made correctly
        mock_request.assert_called_once_with(
            method="POST",
            url="https://api.leneda.lu/api/metering-data-access-request",
            headers={
                "X-API-KEY": "test_api_key",
                "X-ENERGY-ID": "test_energy_id",
                "Content-Type": "application/json",
            },
            params=None,
            json={
                "from": "test_energy_id",
                "fromName": "Test User",
                "meteringPointCodes": ["LU-METERING_POINT1"],
                "obisCodes": [ObisCode.ELEC_CONSUMPTION_ACTIVE.value],
            },
        )

    @patch("requests.request")
    def test_unauthorized_error(self, mock_request):
        """Test handling of 401 Unauthorized errors."""
        # Set up the mock response with 401 status
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.content = b"Unauthorized"
        mock_request.return_value = mock_response

        # Call the method and check that it raises UnauthorizedException
        with self.assertRaises(UnauthorizedException) as context:
            self.client.get_metering_data(
                "LU-METERING_POINT1",
                ObisCode.ELEC_CONSUMPTION_ACTIVE,
                "2023-01-01T00:00:00Z",
                "2023-01-02T00:00:00Z",
            )

        # Check the error message
        self.assertIn("API authentication failed", str(context.exception))

    @patch("requests.request")
    def test_forbidden_error(self, mock_request):
        """Test handling of 403 Forbidden errors."""
        # Set up the mock response with 403 status
        mock_response = MagicMock()
        mock_response.status_code = 403
        mock_response.content = b"Forbidden"
        mock_request.return_value = mock_response

        # Call the method and check that it raises ForbiddenException
        with self.assertRaises(ForbiddenException) as context:
            self.client.get_metering_data(
                "LU-METERING_POINT1",
                ObisCode.ELEC_CONSUMPTION_ACTIVE,
                "2023-01-01T00:00:00Z",
                "2023-01-02T00:00:00Z",
            )

        # Check the error message
        self.assertIn("geoblocking", str(context.exception))

    @patch("requests.request")
    def test_error_handling(self, mock_request):
        """Test error handling for other HTTP errors."""
        # Set up the mock response to raise an exception
        mock_request.side_effect = requests.exceptions.HTTPError("404 Client Error")

        # Call the method and check that it raises an exception
        with self.assertRaises(requests.exceptions.HTTPError):
            self.client.get_metering_data(
                "LU-METERING_POINT1",
                ObisCode.ELEC_CONSUMPTION_ACTIVE,
                "2023-01-01T00:00:00Z",
                "2023-01-02T00:00:00Z",
            )

    @patch("requests.request")
    def test_probe_metering_point_obis_code_valid(self, mock_request):
        """Test probe_metering_point_obis_code with a valid metering point and OBIS code."""
        # Set up the mock response with valid data
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"unit": "kWh", "aggregatedTimeSeries": []}
        mock_response.content = json.dumps(mock_response.json.return_value).encode()
        mock_request.return_value = mock_response

        # Call the method
        result = self.client.probe_metering_point_obis_code(
            "LU-METERING_POINT1", ObisCode.ELEC_CONSUMPTION_ACTIVE
        )

        # Check the result
        self.assertTrue(result)

        # Check that the request was made correctly
        mock_request.assert_called_once()

    @patch("requests.request")
    def test_probe_metering_point_obis_code_invalid(self, mock_request):
        """Test probe_metering_point_obis_code with an invalid metering point or unsupported OBIS code."""
        # Set up the mock response with null unit
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"unit": None, "aggregatedTimeSeries": []}
        mock_response.content = json.dumps(mock_response.json.return_value).encode()
        mock_request.return_value = mock_response

        # Call the method
        result = self.client.probe_metering_point_obis_code(
            "INVALID-METERING-POINT", ObisCode.ELEC_CONSUMPTION_ACTIVE
        )

        # Check the result
        self.assertFalse(result)

        # Check that the request was made correctly
        mock_request.assert_called_once()

    @patch("requests.request")
    def test_get_supported_obis_codes(self, mock_request):
        """Test getting supported OBIS codes for a metering point."""

        # Set up the mock response to return different results for different OBIS codes
        def mock_response_side_effect(*args, **kwargs):
            mock_response = MagicMock()
            mock_response.status_code = 200

            # Check which OBIS code is being probed
            obis_code = kwargs.get("params", {}).get("obisCode")
            if obis_code == ObisCode.ELEC_CONSUMPTION_ACTIVE.value:
                mock_response.json.return_value = {"unit": "kWh", "aggregatedTimeSeries": []}
            elif obis_code == ObisCode.ELEC_PRODUCTION_ACTIVE.value:
                mock_response.json.return_value = {"unit": "kWh", "aggregatedTimeSeries": []}
            else:
                mock_response.json.return_value = {"unit": None, "aggregatedTimeSeries": []}

            mock_response.content = json.dumps(mock_response.json.return_value).encode()
            return mock_response

        mock_request.side_effect = mock_response_side_effect

        # Call the method
        result = self.client.get_supported_obis_codes("LU-METERING_POINT1")

        # Check the result
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)  # We expect 2 supported OBIS codes
        self.assertIn(ObisCode.ELEC_CONSUMPTION_ACTIVE, result)
        self.assertIn(ObisCode.ELEC_PRODUCTION_ACTIVE, result)

        # Check that the request was made for each OBIS code
        self.assertEqual(mock_request.call_count, len(ObisCode))

    @patch("requests.request")
    def test_get_supported_obis_codes_none(self, mock_request):
        """Test getting supported OBIS codes when none are supported."""
        # Set up the mock response to return null unit for all OBIS codes
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"unit": None, "aggregatedTimeSeries": []}
        mock_response.content = json.dumps(mock_response.json.return_value).encode()
        mock_request.return_value = mock_response

        # Call the method
        result = self.client.get_supported_obis_codes("INVALID-METERING-POINT")

        # Check the result
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 0)  # No supported OBIS codes

        # Check that the request was made for each OBIS code
        self.assertEqual(mock_request.call_count, len(ObisCode))


if __name__ == "__main__":
    unittest.main()
