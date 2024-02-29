"""
Streams historical Germany wind forecast data.

Example run:
PYTHONPATH=py python examples/stream_hist_forecast.py "localhost:50051"

License: MIT
Copyright © 2024 Frequenz Energy-as-a-Service GmbH

"""

import asyncio
import datetime
import sys

import grpc.aio as grpcaio
from frequenz.client.weather._client import Client
from frequenz.client.weather._types import ForecastFeature, Location

service_address = sys.argv[1]


async def main(service_address):

    client = Client(
        grpcaio.insecure_channel(service_address),  # or secure channel with credentials
        service_address,
    )

    features = [
        ForecastFeature.V_WIND_COMPONENT_100_METRE,
        ForecastFeature.U_WIND_COMPONENT_100_METRE,
    ]

    locations = [
        Location(
            latitude=52.5,
            longitude=13.4,
            country_code="DE",
        ),
    ]

    now = datetime.datetime.utcnow()
    start = now - datetime.timedelta(days=30)
    end = now + datetime.timedelta(days=7)

    stream = await client.stream_hist_forecast(
        features=features, locations=locations, start=start, end=end
    )

    async for fc in stream:
        print(fc)
        print(fc.to_ndarray_vlf())
        print(
            fc.to_ndarray_vlf(
                features=[ForecastFeature.U_WIND_COMPONENT_100_METRE],
            )
        )


asyncio.run(main(service_address))
