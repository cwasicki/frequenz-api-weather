"""
Iterates over historical Germany wind forecast data and prints it to the screen.

Example run:
PYTHONPATH=py python examples/iterate_hist_forecast.py "localhost:50051"

License: MIT
Copyright © 2024 Frequenz Energy-as-a-Service GmbH

"""

import asyncio
import datetime
import sys

from frequenz.client.weather._client import Client
from frequenz.client.weather._types import ForecastData, ForecastFeature, Location

_service_address = sys.argv[1]


async def main(service_address: str) -> None:
    """Iterate over historical Germany wind forecast data and prints it to the screen.

    Args:
        service_address: The address of the service to connect to
            given in a form of a host followed by a colon and a port.
    """
    client = Client(
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
    start = now - datetime.timedelta(days=1000)
    end = now + datetime.timedelta(days=0)

    location_forecast_iterator = client.hist_forecast_iterator(
        features=features, locations=locations, start=start, end=end
    )

    rows: list[ForecastData] = []
    async for forecasts in location_forecast_iterator:
        # You can work directly with the protobuf object forecasts.
        # Here we choose to flatten into a numpy array instead.
        _rows: list[ForecastData] = forecasts.flatten()
        rows.extend(_rows)

    # Optionally, you can construct a pandas dataframe from the data.
    # pylint: disable=import-outside-toplevel, import-error
    import pandas as pd  # type: ignore[import]

    # pylint: enable=import-outside-toplevel, import-error

    df = pd.DataFrame(rows)
    print(df)


asyncio.run(main(_service_address))
