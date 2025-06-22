"""
Leneda API client for accessing energy consumption and production data.

This module provides a client for the Leneda API, which allows access to
energy consumption and production data for electricity and gas.
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Any, Awaitable, Callable, Dict, List, Optional, Union

import aiohttp
from aiohttp import ClientResponseError, ClientTimeout

from .exceptions import ForbiddenException, MeteringPointNotFoundException, UnauthorizedException
from .models import (
    AggregatedMeteringData,
    AuthenticationProbeResult,
    MeteringData,
)
from .obis_codes import ObisCode

# Set up logging
logger = logging.getLogger("leneda.client")


class LenedaClient:
    """Client for the Leneda API."""

    BASE_URL = "https://api.leneda.lu/api"
    DEFAULT_TIMEOUT = ClientTimeout(total=30)  # 30 seconds total timeout

    def __init__(
        self,
        api_key: str,
        energy_id: str,
        debug: bool = False,
        timeout: Optional[ClientTimeout] = None,
    ):
        """
        Initialize the Leneda API client.

        Args:
            api_key: Your Leneda API key
            energy_id: Your Energy ID
            debug: Enable debug logging
            timeout: Optional timeout settings for requests
        """
        self.api_key = api_key
        self.energy_id = energy_id
        self.timeout = timeout or self.DEFAULT_TIMEOUT

        # Set up headers for API requests
        self.headers = {
            "X-API-KEY": api_key,
            "X-ENERGY-ID": energy_id,
            "Content-Type": "application/json",
        }

        # Set up debug logging if requested
        if debug:
            logging.getLogger("leneda").setLevel(logging.DEBUG)
            logger.setLevel(logging.DEBUG)
            logger.debug("Debug logging enabled for Leneda client")

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[dict] = None,
        json_data: Optional[dict] = None,
    ) -> dict:
        """
        Make a request to the Leneda API.

        Args:
            method: The HTTP method to use
            endpoint: The API endpoint to call
            params: Optional query parameters
            json_data: Optional JSON data to send in the request body

        Returns:
            The JSON response from the API

        Raises:
            UnauthorizedException: If the API returns a 401 status code
            ForbiddenException: If the API returns a 403 status code
            aiohttp.ClientError: For other request errors
            json.JSONDecodeError: If the response cannot be parsed as JSON
        """
        url = f"{self.BASE_URL}/{endpoint}"

        # Log the request details
        logger.debug(f"Making {method} request to {url}")
        if params:
            logger.debug(f"Query parameters: {params}")
        if json_data:
            logger.debug(f"Request data: {json.dumps(json_data, indent=2)}")

        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.request(
                    method=method, url=url, headers=self.headers, params=params, json=json_data
                ) as response:
                    # Check for HTTP errors
                    if response.status == 401:
                        raise UnauthorizedException(
                            "API authentication failed. Please check your API key and energy ID."
                        )
                    if response.status == 403:
                        raise ForbiddenException(
                            "Access forbidden. This may be due to Leneda's geoblocking or other access restrictions."
                        )
                    response.raise_for_status()

                    # Parse the response
                    if response.content:
                        response_data: dict = await response.json()
                        logger.debug(f"Response status: {response.status}")
                        logger.debug(f"Response data: {json.dumps(response_data, indent=2)}")
                        return response_data
                    else:
                        logger.debug(f"Response status: {response.status} (no content)")
                        return {}

        except aiohttp.ClientError as e:
            # Handle HTTP errors
            logger.error(f"HTTP error: {e}")
            raise

        except json.JSONDecodeError as e:
            # Handle JSON parsing errors
            logger.error(f"JSON decode error: {e}")
            raise

    async def _make_metering_request(
        self, request_callable: Callable[..., Awaitable[dict[Any, Any]]], *args: Any, **kwargs: Any
    ) -> dict[Any, Any]:
        """
        Make a request to a metering data endpoint with 404 error handling.

        This wrapper around any request callable specifically handles 404 errors for metering data
        endpoints by raising MeteringPointNotFoundException.

        Args:
            request_callable: The callable to execute (e.g., self._make_request)
            *args: Arguments to pass to the callable
            **kwargs: Keyword arguments to pass to the callable

        Returns:
            The JSON response from the API

        Raises:
            MeteringPointNotFoundException: If the API returns a 404 status code
            UnauthorizedException: If the API returns a 401 status code
            ForbiddenException: If the API returns a 403 status code
            aiohttp.ClientError: For other request errors
            json.JSONDecodeError: If the response cannot be parsed as JSON
        """
        try:
            return await request_callable(*args, **kwargs)
        except aiohttp.ClientResponseError as e:
            if e.status == 404:
                raise MeteringPointNotFoundException(
                    "Metering point not found. The requested metering point may not exist or you may not have access to it."
                )
            raise

    async def get_metering_data(
        self,
        metering_point_code: str,
        obis_code: ObisCode,
        start_date_time: Union[str, datetime],
        end_date_time: Union[str, datetime],
    ) -> MeteringData:
        """
        Get time series data for a specific metering point and OBIS code.

        Args:
            metering_point_code: The metering point code
            obis_code: The OBIS code (from ElectricityConsumption, ElectricityProduction, or GasConsumption)
            start_date_time: Start date and time (ISO format string or datetime object)
            end_date_time: End date and time (ISO format string or datetime object)

        Returns:
            MeteringData object containing the time series data
        """
        # Convert datetime objects to ISO format strings if needed
        if isinstance(start_date_time, datetime):
            start_date_time = start_date_time.strftime("%Y-%m-%dT%H:%M:%SZ")
        if isinstance(end_date_time, datetime):
            end_date_time = end_date_time.strftime("%Y-%m-%dT%H:%M:%SZ")

        # Set up the endpoint and parameters
        endpoint = f"metering-points/{metering_point_code}/time-series"
        params = {
            "obisCode": obis_code.value,  # Use enum value for API request
            "startDateTime": start_date_time,
            "endDateTime": end_date_time,
        }

        # Make the request
        response_data = await self._make_metering_request(
            self._make_request, method="GET", endpoint=endpoint, params=params
        )

        # Parse the response into a MeteringData object
        return MeteringData.from_dict(response_data)

    async def get_aggregated_metering_data(
        self,
        metering_point_code: str,
        obis_code: ObisCode,
        start_date: Union[str, datetime],
        end_date: Union[str, datetime],
        aggregation_level: str = "Day",
        transformation_mode: str = "Accumulation",
    ) -> AggregatedMeteringData:
        """
        Get aggregated time series data for a specific metering point and OBIS code.

        Args:
            metering_point_code: The metering point code
            obis_code: The OBIS code (from ElectricityConsumption, ElectricityProduction, or GasConsumption)
            start_date: Start date (ISO format string or datetime object)
            end_date: End date (ISO format string or datetime object)
            aggregation_level: Aggregation level (Hour, Day, Week, Month, Infinite)
            transformation_mode: Transformation mode (Accumulation)

        Returns:
            AggregatedMeteringData object containing the aggregated time series data
        """
        # Convert datetime objects to ISO format strings if needed
        if isinstance(start_date, datetime):
            start_date = start_date.strftime("%Y-%m-%d")
        if isinstance(end_date, datetime):
            end_date = end_date.strftime("%Y-%m-%d")

        # Set up the endpoint and parameters
        endpoint = f"metering-points/{metering_point_code}/time-series/aggregated"
        params = {
            "obisCode": obis_code.value,  # Use enum value for API request
            "startDate": start_date,
            "endDate": end_date,
            "aggregationLevel": aggregation_level,
            "transformationMode": transformation_mode,
        }

        # Make the request
        response_data = await self._make_metering_request(
            self._make_request, method="GET", endpoint=endpoint, params=params
        )

        # Parse the response into an AggregatedMeteringData object
        return AggregatedMeteringData.from_dict(response_data)

    async def request_metering_data_access(
        self,
        from_energy_id: str,
        from_name: str,
        metering_point_codes: List[str],
        obis_codes: List[ObisCode],
    ) -> Dict[str, Any]:
        """
        Request access to metering data for a specific metering point.

        Args:
            from_energy_id: The energy ID of the requester
            from_name: The name of the requester
            metering_point_codes: The metering point codes to access
            obis_point_codes: The OBIS point codes to access (from ElectricityConsumption, ElectricityProduction, or GasConsumption)

        Returns:
            Response data from the API
        """
        # Set up the endpoint and data
        endpoint = "metering-data-access-request"
        data = {
            "from": from_energy_id,
            "fromName": from_name,
            "meteringPointCodes": metering_point_codes,
            "obisCodes": [code.value for code in obis_codes],  # Use enum values for API request
        }

        # Make the request
        response_data = await self._make_request(method="POST", endpoint=endpoint, json_data=data)

        return response_data

    async def probe_metering_point_obis_code(
        self, metering_point_code: str, obis_code: ObisCode
    ) -> bool:
        """
        Probe if a metering point provides data for a specific OBIS code.

        NOTE: This method is essentially a best guess since the Leneda API does not provide a way to check
        if a metering point provides data for a specific OBIS code or whether a metering point code is valid

        This method checks if a metering point provides data for the specified OBIS code by making a request
        for aggregated metering data. If the unit property in the response is null, it indicates that either:
        - The metering point is invalid, or
        - The metering point does not provide data for the specified OBIS code

        Args:
            metering_point_code: The metering point code to probe
            obis_code: The OBIS code to check for data availability

        Returns:
            bool: True if the metering point provides data for the specified OBIS code, False otherwise

        Raises:
            UnauthorizedException: If the API returns a 401 status code
            ForbiddenException: If the API returns a 403 status code
            aiohttp.ClientError: For other request errors
        """
        # Use arbitrary time window
        end_date = datetime.now()
        start_date = end_date - timedelta(weeks=4)

        # Try to get aggregated data for the specified OBIS code
        result = await self.get_aggregated_metering_data(
            metering_point_code=metering_point_code,
            obis_code=obis_code,
            start_date=start_date,
            end_date=end_date,
            aggregation_level="Month",
            transformation_mode="Accumulation",
        )

        # Return True if we got data (unit is not None), False otherwise
        return result.unit is not None

    async def get_supported_obis_codes(self, metering_point_code: str) -> List[ObisCode]:
        """
        Get all OBIS codes that are supported by a given metering point.

        NOTE: Please see the documentation of the probe_metering_point_obis_code method about best guess
        behaviour. If this method returns an empty list, chances are high that the metering point code
        is invalid or that the Energy ID has no access to it.

        This method probes each OBIS code defined in the ObisCode enum to determine
        which ones are supported by the specified metering point.

        Args:
            metering_point_code: The metering point code to check

        Returns:
            List[ObisCode]: A list of OBIS codes that are supported by the metering point

        Raises:
            UnauthorizedException: If the API returns a 401 status code
            ForbiddenException: If the API returns a 403 status code
            aiohttp.ClientError: For other request errors
        """
        supported_codes = []
        for obis_code in ObisCode:
            if await self.probe_metering_point_obis_code(metering_point_code, obis_code):
                supported_codes.append(obis_code)
        return supported_codes

    async def probe_credentials(self) -> AuthenticationProbeResult:
        """
        Probe if credentials are valid.

        NOTE: This is an experimental function, as the Leneda API does not provide a native way to verify credentials only.
        Use with caution, may break or yield unexpected results.

        This method attempts to verify authentication by making a request to the metering data access endpoint
        with invalid parameters. If the API returns a 400 status code, it indicates that authentication is successful
        but the request parameters are invalid. If it returns a 401 status code, authentication has failed.

        We make a request with invalid parameters because we don't want to actually lodge a metering data access request,
        we just want to verify that the credentials are valid.

        Returns:
            AuthenticationProbeResult: SUCCESS if authentication is valid, FAILURE if authentication failed,
            or UNKNOWN if the result cannot be determined

        Raises:
            ForbiddenException: If the API returns a 403 status code
        """
        try:
            await self.request_metering_data_access("", "", [], [])
        except UnauthorizedException:
            return AuthenticationProbeResult.FAILURE
        except ClientResponseError as e:
            # We expect a 400 response if authentication is successful and our request is invalid
            if e.status == 400:
                # Update the config entry with new token
                return AuthenticationProbeResult.SUCCESS
            return AuthenticationProbeResult.UNKNOWN
        except ForbiddenException:
            raise
        except Exception:
            return AuthenticationProbeResult.UNKNOWN

        return AuthenticationProbeResult.UNKNOWN
