import asyncio
from frequenz.client.weather._client import Client
from frequenz.client.weather._types import ForecastFeature, Location
import grpc.aio as grpcaio



async def main():
    target="localhost:50051"

    client = Client(
        grpcaio.insecure_channel(target),  # or secure channel with credentials
        target,
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

    stream = await client.stream_live_forecast(
        features=features,
        locations=locations,
    )

    async for fc in stream:
        print(fc)
        print(fc.to_ndarray_vlf())
        print(fc.to_ndarray_vlf(
            features=[ForecastFeature.U_WIND_COMPONENT_100_METRE],
        ))

asyncio.run(main())
