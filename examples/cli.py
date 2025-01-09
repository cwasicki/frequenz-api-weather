# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""CLI tool to iterate over historical weather forecast data and print it in CSV format."""

import argparse
import asyncio
from datetime import datetime, timedelta

from frequenz.client.base.channel import ChannelOptions, KeepAliveOptions, SslOptions
from frequenz.client.weather._client import Client
from frequenz.client.weather._types import ForecastFeature, Location


def main() -> None:
    """Parse arguments and run the client."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--url",
        type=str,
        help="URL of the Weather service",
    )
    parser.add_argument(
        "--feature",
        type=str,
        nargs="+",
        choices=[e.name for e in ForecastFeature],
        help="Feature names",
        required=True,
    )
    parser.add_argument(
        "--location",
        type=lambda s: tuple(map(float, s.split(","))),  # One-liner lambda
        required=True,
        help='Location in lat,lon format (e.g., "37.7749,-122.4194")',
    )
    parser.add_argument(
        "--start",
        type=datetime.fromisoformat,
        help="Start datetime in YYYY-MM-DDTHH:MM:SS format",
        required=True,
    )
    parser.add_argument(
        "--end",
        type=datetime.fromisoformat,
        help="End datetime in YYYY-MM-DDTHH:MM:SS format",
        required=True,
    )
    args = parser.parse_args()
    asyncio.run(
        run(
            service_address=args.url,
            location=args.location,
            feature_names=args.feature,
            start=args.start,
            end=args.end,
        )
    )


async def run(
    *,
    service_address: str,
    location: tuple[float, float],
    feature_names: list[str],
    start: datetime,
    end: datetime,
) -> None:
    """Run the client.

    Args:
        service_address: service address
        location: location in lat, lon format
        feature_names: feature names
        start: start datetime
        end: end datetime
    """
    client = Client(
        service_address,
        channel_defaults=ChannelOptions(
            ssl=SslOptions(
                enabled=False,
            ),
            keep_alive=KeepAliveOptions(
                enabled=True,
                timeout=timedelta(minutes=5),
                interval=timedelta(seconds=20),
            ),
        ),
    )

    features = [ForecastFeature[feature_name] for feature_name in feature_names]
    locations = [
        Location(
            latitude=location[0],
            longitude=location[1],
            country_code="",
        ),
    ]

    location_forecast_iterator = client.hist_forecast_iterator(
        features=features, locations=locations, start=start, end=end
    )

    print("creation_ts,validity_ts,latitude,longitude,feature,value")
    async for forecasts in location_forecast_iterator:
        for fc in forecasts.flatten():
            row = (
                fc.creation_ts,
                fc.validity_ts,
                fc.latitude,
                fc.longitude,
                fc.feature,
                fc.value,
            )
            print(",".join(str(e) for e in row))


if __name__ == "__main__":
    main()
