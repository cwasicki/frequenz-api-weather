# License: MIT
# Copyright © 2024 Frequenz Energy-as-a-Service GmbH

"""The Historical Forecast Iterator."""

from __future__ import annotations

from collections.abc import AsyncIterator
from datetime import datetime

from frequenz.api.common.v1.pagination import pagination_params_pb2
from frequenz.api.weather import weather_pb2, weather_pb2_grpc
from google.protobuf import timestamp_pb2

from ._types import ForecastFeature, HistoricalForecasts, Location

DEFAULT_PAGE_SIZE = 20
EMPTY_PAGE_TOKEN = ""


# pylint: disable=too-many-instance-attributes
class HistoricalForecastIterator(AsyncIterator[HistoricalForecasts]):
    """An iterator over historical weather forecasts."""

    def __init__(  # pylint: disable=too-many-arguments
        self,
        stub: weather_pb2_grpc.WeatherForecastServiceAsyncStub,
        locations: list[Location],
        features: list[ForecastFeature],
        start: datetime,
        end: datetime,
        page_size: int = DEFAULT_PAGE_SIZE,
    ) -> None:
        """Initialize the iterator.

        Args:
            stub: The gRPC stub to use for communication with the API.
            locations: Locations to get historical weather forecasts for.
            features: Features to get historical weather forecasts for.
            start: Start of the time range to get historical weather forecasts for.
            end: End of the time range to get historical weather forecasts for.
            page_size: The number of historical weather forecasts to get per page.
        """
        self._stub = stub
        self.locations = locations
        self.features = features

        self.start_ts = timestamp_pb2.Timestamp()
        self.start_ts.FromDatetime(start)
        self.end_ts = timestamp_pb2.Timestamp()
        self.end_ts.FromDatetime(end)

        self.location_forecasts: list[weather_pb2.LocationForecast] = []
        self.page_token: str | None = None
        self.page_size = page_size

    def __aiter__(self) -> "HistoricalForecastIterator":
        """Return the iterator.

        Returns:
            The iterator.
        """
        return self

    async def __anext__(self) -> HistoricalForecasts:
        """Get the next historical weather forecast.

        Returns:
            The next historical weather forecast.

        Raises:
            StopAsyncIteration: If there are no more historical weather forecasts.
        """
        if self.page_token == EMPTY_PAGE_TOKEN:
            raise StopAsyncIteration

        pagination_params = pagination_params_pb2.PaginationParams()
        pagination_params.page_size = self.page_size
        if self.page_token is not None:
            pagination_params.page_token = self.page_token

        response: weather_pb2.GetHistoricalWeatherForecastResponse = (
            await self._stub.GetHistoricalWeatherForecast(
                weather_pb2.GetHistoricalWeatherForecastRequest(
                    locations=(location.to_pb() for location in self.locations),
                    features=(feature.value for feature in self.features),
                    start_ts=self.start_ts,
                    end_ts=self.end_ts,
                    pagination_params=pagination_params,
                )
            )
        )

        if (
            response.pagination_info is None
            or response.pagination_info.next_page_token is None
        ):
            raise StopAsyncIteration

        self.page_token = response.pagination_info.next_page_token
        if len(response.location_forecasts) == 0:
            raise StopAsyncIteration

        return HistoricalForecasts.from_pb(response)
