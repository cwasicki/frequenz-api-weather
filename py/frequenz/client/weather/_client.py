# License: MIT
# Copyright © 2023 Frequenz Energy-as-a-Service GmbH

"""The Weather Forecast API client."""

from __future__ import annotations

from datetime import datetime

from frequenz.api.weather import weather_pb2, weather_pb2_grpc
from frequenz.channels import Receiver
from frequenz.client.base.channel import ChannelOptions
from frequenz.client.base.client import BaseApiClient
from frequenz.client.base.exception import ClientNotConnected
from frequenz.client.base.streaming import GrpcStreamBroadcaster

from ._historical_forecast_iterator import HistoricalForecastIterator
from ._types import ForecastFeature, Forecasts, Location


class Client(BaseApiClient[weather_pb2_grpc.WeatherForecastServiceStub]):
    """Weather forecast client."""

    def __init__(
        self,
        server_url: str,
        *,
        connect: bool = True,
        channel_defaults: ChannelOptions = ChannelOptions(),
    ) -> None:
        """Initialize the client.

        Args:
            server_url: The URL of the server to connect to.
            connect: Whether to connect to the server as soon as a client instance is
                created. If `False`, the client will not connect to the server until
                [connect()][frequenz.client.base.client.BaseApiClient.connect] is
                called.
            channel_defaults: Default options for the gRPC channel.
        """
        super().__init__(
            server_url,
            weather_pb2_grpc.WeatherForecastServiceStub,
            connect=connect,
            channel_defaults=channel_defaults,
        )
        self._streams: dict[
            tuple[Location | ForecastFeature, ...],
            GrpcStreamBroadcaster[
                weather_pb2.ReceiveLiveWeatherForecastResponse, Forecasts
            ],
        ] = {}

    @property
    def stub(self) -> weather_pb2_grpc.WeatherForecastServiceAsyncStub:
        """The gRPC stub for the API."""
        if self.channel is None or self._stub is None:
            raise ClientNotConnected(server_url=self.server_url, operation="stub")
        # This type: ignore is needed because we need to cast the sync stub to
        # the async stub, but we can't use cast because the async stub doesn't
        # actually exists to the eyes of the interpreter, it only exists for the
        # type-checker, so it can only be used for type hints.
        return self._stub  # type: ignore

    async def stream_live_forecast(
        self,
        locations: list[Location],
        features: list[ForecastFeature],
    ) -> Receiver[Forecasts]:
        """Stream live weather forecast data.

        Args:
            locations: locations to stream data for.
            features: features to stream data for.

        Returns:
            A channel receiver for weather forecast data.
        """
        stream_key = tuple(tuple(locations) + tuple(features))

        if stream_key not in self._streams:
            self._streams[stream_key] = GrpcStreamBroadcaster(
                f"weather-forecast-{stream_key}",
                lambda: self.stub.ReceiveLiveWeatherForecast(
                    weather_pb2.ReceiveLiveWeatherForecastRequest(
                        locations=(location.to_pb() for location in locations),
                        features=(feature.value for feature in features),
                    )
                ),
                Forecasts.from_pb,
            )
        return self._streams[stream_key].new_receiver()

    def hist_forecast_iterator(
        self,
        locations: list[Location],
        features: list[ForecastFeature],
        start: datetime,
        end: datetime,
    ) -> HistoricalForecastIterator:
        """Stream historical weather forecast data.

        Args:
            locations: locations to stream data for.
            features: features to stream data for.
            start: start of the time range to stream data for.
            end: end of the time range to stream data for.

        Returns:
            A channel receiver for weather forecast data.
        """
        return HistoricalForecastIterator(self.stub, locations, features, start, end)
