"""
Tests for the Leneda API client.
"""

import json
import os
import sys
import unittest
from unittest.mock import AsyncMock, patch

import aiohttp
import pytest

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


@pytest.mark.asyncio
class TestLenedaClient:
    """Test cases for the LenedaClient class."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test fixtures."""
        self.api_key = "test_api_key"
        self.energy_id = "test_energy_id"
        self.client = LenedaClient(self.api_key, self.energy_id)

        # Sample response data
        self.sample_metering_data = {
            "meteringPointCode": "LU-METERING_POINT1",
            "obisCode": ObisCode.ELEC_CONSUMPTION_ACTIVE.value,
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

    @patch("aiohttp.ClientSession.request")
    async def test_get_time_series(self, mock_request):
        """Test getting time series data."""
        # Set up the mock response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=self.sample_metering_data)
        mock_response.content = json.dumps(self.sample_metering_data).encode()
        mock_response.raise_for_status = lambda: None
        mock_request.return_value.__aenter__.return_value = mock_response

        # Call the method
        result = await self.client.get_metering_data(
            "LU-METERING_POINT1",
            ObisCode.ELEC_CONSUMPTION_ACTIVE,
            "2023-01-01T00:00:00Z",
            "2023-01-02T00:00:00Z",
        )

        # Check the result
        assert isinstance(result, MeteringData)
        assert result.metering_point_code == "LU-METERING_POINT1"
        assert result.obis_code == ObisCode.ELEC_CONSUMPTION_ACTIVE
        assert result.unit == "kWh"
        assert len(result.items) == 2

        # Check the first item
        assert isinstance(result.items[0], MeteringValue)
        assert result.items[0].value == 1.234
        assert result.items[0].started_at.isoformat() == "2023-01-01T00:00:00+00:00"
        assert result.items[0].type == "Measured"
        assert result.items[0].version == 1
        assert result.items[0].calculated is False

        # Check that the request was made correctly
        mock_request.assert_called_once()
        call_kwargs = mock_request.call_args[1]
        assert call_kwargs["method"] == "GET"
        assert call_kwargs["headers"] == {
            "X-API-KEY": "test_api_key",
            "X-ENERGY-ID": "test_energy_id",
            "Content-Type": "application/json",
        }
        assert call_kwargs["params"] == {
            "obisCode": ObisCode.ELEC_CONSUMPTION_ACTIVE.value,
            "startDateTime": "2023-01-01T00:00:00Z",
            "endDateTime": "2023-01-02T00:00:00Z",
        }

    @patch("aiohttp.ClientSession.request")
    async def test_get_aggregated_time_series(self, mock_request):
        """Test getting aggregated time series data."""
        # Set up the mock response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=self.sample_aggregated_data)
        mock_response.content = json.dumps(self.sample_aggregated_data).encode()
        mock_response.raise_for_status = lambda: None
        mock_request.return_value.__aenter__.return_value = mock_response

        # Call the method
        result = await self.client.get_aggregated_metering_data(
            "LU-METERING_POINT1",
            ObisCode.ELEC_CONSUMPTION_ACTIVE,
            "2023-01-01",
            "2023-01-31",
            "Day",
            "Accumulation",
        )

        # Check the result
        assert isinstance(result, AggregatedMeteringData)
        assert result.unit == "kWh"
        assert len(result.aggregated_time_series) == 2

        # Check the first item
        assert isinstance(result.aggregated_time_series[0], AggregatedMeteringValue)
        assert result.aggregated_time_series[0].value == 10.123
        assert (
            result.aggregated_time_series[0].started_at.isoformat() == "2023-01-01T00:00:00+00:00"
        )
        assert result.aggregated_time_series[0].ended_at.isoformat() == "2023-01-02T00:00:00+00:00"
        assert result.aggregated_time_series[0].calculated is False

        # Check that the request was made correctly
        mock_request.assert_called_once()
        call_kwargs = mock_request.call_args[1]
        assert call_kwargs["method"] == "GET"
        assert call_kwargs["headers"] == {
            "X-API-KEY": "test_api_key",
            "X-ENERGY-ID": "test_energy_id",
            "Content-Type": "application/json",
        }
        assert call_kwargs["params"] == {
            "obisCode": ObisCode.ELEC_CONSUMPTION_ACTIVE.value,
            "startDate": "2023-01-01",
            "endDate": "2023-01-31",
            "aggregationLevel": "Day",
            "transformationMode": "Accumulation",
        }

    @patch("aiohttp.ClientSession.request")
    async def test_request_metering_data_access(self, mock_request):
        """Test requesting metering data access."""
        # Set up the mock response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(
            return_value={"requestId": "test-request-id", "status": "PENDING"}
        )
        mock_response.raise_for_status = lambda: None
        mock_request.return_value.__aenter__.return_value = mock_response

        # Call the method
        result = await self.client.request_metering_data_access(
            from_energy_id="test_energy_id",
            from_name="Test User",
            metering_point_codes=["LU-METERING_POINT1"],
            obis_codes=[ObisCode.ELEC_CONSUMPTION_ACTIVE],
        )

        # Check the result
        assert result["requestId"] == "test-request-id"
        assert result["status"] == "PENDING"

        # Check that the request was made correctly
        mock_request.assert_called_once()
        call_kwargs = mock_request.call_args[1]
        assert call_kwargs["method"] == "POST"
        assert call_kwargs["url"] == "https://api.leneda.lu/api/metering-data-access-request"
        assert call_kwargs["headers"] == {
            "X-API-KEY": "test_api_key",
            "X-ENERGY-ID": "test_energy_id",
            "Content-Type": "application/json",
        }
        assert call_kwargs["json"] == {
            "from": "test_energy_id",
            "fromName": "Test User",
            "meteringPointCodes": ["LU-METERING_POINT1"],
            "obisCodes": [ObisCode.ELEC_CONSUMPTION_ACTIVE.value],
        }

    @patch("aiohttp.ClientSession.request")
    async def test_unauthorized_error(self, mock_request):
        """Test handling of 401 Unauthorized errors."""
        # Set up the mock response with 401 status
        mock_response = AsyncMock()
        mock_response.status = 401
        mock_response.content = b"Unauthorized"
        mock_response.raise_for_status = lambda: None
        mock_request.return_value.__aenter__.return_value = mock_response

        # Call the method and check that it raises UnauthorizedException
        with pytest.raises(UnauthorizedException) as exc_info:
            await self.client.get_metering_data(
                "LU-METERING_POINT1",
                ObisCode.ELEC_CONSUMPTION_ACTIVE,
                "2023-01-01T00:00:00Z",
                "2023-01-02T00:00:00Z",
            )

        # Check the error message
        assert "API authentication failed" in str(exc_info.value)

    @patch("aiohttp.ClientSession.request")
    async def test_forbidden_error(self, mock_request):
        """Test handling of 403 Forbidden errors."""
        # Set up the mock response with 403 status
        mock_response = AsyncMock()
        mock_response.status = 403
        mock_response.content = b"Forbidden"
        mock_response.raise_for_status = lambda: None
        mock_request.return_value.__aenter__.return_value = mock_response

        # Call the method and check that it raises ForbiddenException
        with pytest.raises(ForbiddenException) as exc_info:
            await self.client.get_metering_data(
                "LU-METERING_POINT1",
                ObisCode.ELEC_CONSUMPTION_ACTIVE,
                "2023-01-01T00:00:00Z",
                "2023-01-02T00:00:00Z",
            )

        # Check the error message
        assert "geoblocking" in str(exc_info.value)

    @patch("aiohttp.ClientSession.request")
    async def test_error_handling(self, mock_request):
        """Test error handling for other HTTP errors."""
        # Set up the mock response to raise an exception
        mock_request.side_effect = aiohttp.ClientError("404 Client Error")

        # Call the method and check that it raises an exception
        with pytest.raises(aiohttp.ClientError):
            await self.client.get_metering_data(
                "LU-METERING_POINT1",
                ObisCode.ELEC_CONSUMPTION_ACTIVE,
                "2023-01-01T00:00:00Z",
                "2023-01-02T00:00:00Z",
            )

    @patch("aiohttp.ClientSession.request")
    async def test_probe_metering_point_obis_code_valid(self, mock_request):
        """Test probe_metering_point_obis_code with a valid metering point and OBIS code."""
        # Set up the mock response with valid data
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={"unit": "kWh", "aggregatedTimeSeries": []})
        mock_response.raise_for_status = lambda: None
        mock_request.return_value.__aenter__.return_value = mock_response

        # Call the method
        result = await self.client.probe_metering_point_obis_code(
            "LU-METERING_POINT1", ObisCode.ELEC_CONSUMPTION_ACTIVE
        )

        # Check the result
        assert result is True

        # Check that the request was made correctly
        mock_request.assert_called_once()

    @patch("aiohttp.ClientSession.request")
    async def test_probe_metering_point_obis_code_invalid(self, mock_request):
        """Test probe_metering_point_obis_code with an invalid metering point or unsupported OBIS code."""
        # Set up the mock response with null unit
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={"unit": None, "aggregatedTimeSeries": []})
        mock_response.raise_for_status = lambda: None
        mock_request.return_value.__aenter__.return_value = mock_response

        # Call the method
        result = await self.client.probe_metering_point_obis_code(
            "INVALID-METERING-POINT", ObisCode.ELEC_CONSUMPTION_ACTIVE
        )

        # Check the result
        assert result is False

        # Check that the request was made correctly
        mock_request.assert_called_once()

    @patch.object(LenedaClient, "probe_metering_point_obis_code")
    async def test_get_supported_obis_codes(self, mock_probe):
        """Test getting supported OBIS codes for a metering point."""

        # Mock probe_metering_point_obis_code to return True for two codes, False otherwise
        def side_effect(metering_point_code, obis_code):
            return obis_code in [ObisCode.ELEC_CONSUMPTION_ACTIVE, ObisCode.ELEC_PRODUCTION_ACTIVE]

        mock_probe.side_effect = side_effect

        # Call the method
        result = await self.client.get_supported_obis_codes("LU-METERING_POINT1")

        # Check the result
        assert isinstance(result, list)
        assert len(result) == 2  # We expect 2 supported OBIS codes
        assert ObisCode.ELEC_CONSUMPTION_ACTIVE in result
        assert ObisCode.ELEC_PRODUCTION_ACTIVE in result

        # Check that the probe was called for each OBIS code
        assert mock_probe.call_count == len(ObisCode)

    @patch.object(LenedaClient, "probe_metering_point_obis_code", return_value=False)
    async def test_get_supported_obis_codes_none(self, mock_probe):
        """Test getting supported OBIS codes when none are supported."""
        # Call the method
        result = await self.client.get_supported_obis_codes("INVALID-METERING-POINT")

        # Check the result
        assert isinstance(result, list)
        assert len(result) == 0  # No supported OBIS codes

        # Check that the probe was called for each OBIS code
        assert mock_probe.call_count == len(ObisCode)


if __name__ == "__main__":
    unittest.main()
