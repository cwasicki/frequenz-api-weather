from __future__ import annotations  # required for constructor type hinting
import numpy as np
import datetime as dt
from dataclasses import dataclass
import enum
import logging
from frequenz.api.weather import weather_pb2
from frequenz.api.common.v1 import location_pb2

# Set up logging
_logger = logging.getLogger(__name__)


class ForecastFeature(enum.Enum):
    """Weather forecast features available through the API."""

    UNSPECIFIED = weather_pb2.ForecastFeature.FORECAST_FEATURE_UNSPECIFIED
    """Unspecified forecast feature."""

    U_WIND_COMPONENT_100_METRE = (
        weather_pb2.ForecastFeature.FORECAST_FEATURE_U_WIND_COMPONENT_100_METRE
    )
    """Eastward wind component at 100m altitude."""

    V_WIND_COMPONENT_100_METRE = (
        weather_pb2.ForecastFeature.FORECAST_FEATURE_V_WIND_COMPONENT_100_METRE
    )
    """Northward wind component at 100m altitude."""

    SURFACE_SOLAR_RADIATION_DOWNWARDS = (
        weather_pb2.ForecastFeature.FORECAST_FEATURE_SURFACE_SOLAR_RADIATION_DOWNWARDS
    )
    """Surface solar radiation downwards."""

    SURFACE_NET_SOLAR_RADIATION = (
        weather_pb2.ForecastFeature.FORECAST_FEATURE_SURFACE_NET_SOLAR_RADIATION
    )
    """Surface net solar radiation."""

    @classmethod
    def from_pb(
        cls, forecast_feature: weather_pb2.ForecastFeature.ValueType
    ) -> ForecastFeature:
        """Convert a protobuf ForecastFeature value to ForecastFeature enum.

        Args:
            forecast_feature: protobuf forecast feature to convert.

        Returns:
            Enum value corresponding to the protobuf message.
        """
        if not any(t.value == forecast_feature for t in ForecastFeature):
            _logger.warning(
                "Unknown forecast feature %s. Returning UNSPECIFIED.", forecast_feature
            )
            return cls.UNSPECIFIED

        return ForecastFeature(forecast_feature)


@dataclass(frozen=True)
class Location:

    """Location data.

    Attributes:
        latitude: latitude of the location.
        longitude: longitude of the location.
        altitude: altitude of the location.
    """

    # TODO : find right import for location

    latitude: float
    longitude: float
    country_code: str

    @classmethod
    def from_pb(cls, location: location_pb2.Location) -> Location:
        """Convert a protobuf Location message to Location object.

        Args:
            location: protobuf location to convert.

        Returns:
            Location object corresponding to the protobuf message.
        """
        return cls(
            latitude=location.latitude,
            longitude=location.longitude,
            country_code=location.country_code,
        )

    def to_pb(self) -> location_pb2.Location:
        """Convert a Location object to protobuf Location message.

        Returns:
            Protobuf message corresponding to the Location object.
        """
        return location_pb2.Location(
            latitude=self.latitude,
            longitude=self.longitude,
            country_code=self.country_code,
        )


@dataclass(frozen=True)
class Forecasts:
    """Weather forecast data."""

    _forecasts_pb: weather_pb2.ReceiveLiveWeatherForecastResponse

    @classmethod
    def from_pb(
        cls, forecasts: weather_pb2.ReceiveLiveWeatherForecastResponse
    ) -> Forecasts:
        """Convert a protobuf Forecast message to Forecast object."""
        return cls(_forecasts_pb=forecasts)

    def to_ndarray_vlf(
        self,
        validity_times: list[dt.timedelta] | None = None,
        locations: list[Location] | None = None,
        features: list[ForecastFeature] | None = None,
    ) -> np.ndarray:
        """Convert a Forecast object to numpy array."""
        num_times = len(self._forecasts_pb.location_forecasts[0].forecasts)
        num_locations = len(self._forecasts_pb.location_forecasts)
        num_features = len(
            self._forecasts_pb.location_forecasts[0].forecasts[0].features
        )

        array = np.zeros((num_times, num_locations, num_features))

        # iterate through all locations
        for l_index, location_forecast in enumerate(
            self._forecasts_pb.location_forecasts
        ):
            creation_ts = location_forecast.creation_ts.ToDatetime()

            # check if location is in locations
            if (
                locations
                and Location.from_pb(location_forecast.location) not in locations
            ):
                continue

            # iterate through all forecasts (all times) for a location
            for t_index, forecast in enumerate(location_forecast.forecasts):
                validity_ts = forecast.valid_at_ts.ToDatetime()

                # check if is in validity times
                if validity_times and (validity_ts - creation_ts) in validity_times:
                    continue

                # iterate through all features for a forecast valid at a certain time for one location
                for f_index, feature_forecast in enumerate(forecast.features):
                    feature = ForecastFeature.from_pb(feature_forecast.feature)
                    if features and feature not in features:
                        continue

                    array[t_index, l_index, f_index] = feature_forecast.value

                if array[t_index, l_index, :].sum() == 0:
                    _logger.warning(
                        "Forecast at %s for location %s is empty. Skipping.",
                        validity_ts,
                        location_forecast.location,
                    )

        return array

    def to_ndarray_vlf_refined(
        self,
        validity_times: list[dt.timedelta] | None = None,
        locations: list[Location] | None = None,
        features: list[ForecastFeature] | None = None,
    ) -> np.ndarray:
        """Convert a Forecast object to numpy array and use NaN to mark irrelevant data."""

        # Check entry types
        if validity_times is not None and not all(
            isinstance(t, dt.timedelta) for t in validity_times
        ):
            raise ValueError(
                "validity_times must be a list of datetime.timedelta objects"
            )
        if locations is not None and not all(
            isinstance(loc, Location) for loc in locations
        ):
            raise ValueError("locations must be a list of Location objects")
        if features is not None and not all(
            isinstance(feat, ForecastFeature) for feat in features
        ):
            raise ValueError("features must be a list of ForecastFeatureType objects")

        # check for empty forecasts data
        if (
            not hasattr(self, "_forecasts_pb")
            or not self._forecasts_pb.location_forecasts
        ):
            raise ValueError("Forecast data is missing or invalid")

        try:
            num_times = len(self._forecasts_pb.location_forecasts[0].forecasts)
            num_locations = len(self._forecasts_pb.location_forecasts)
            num_features = len(
                self._forecasts_pb.location_forecasts[0].forecasts[0].features
            )

            # TODO: check

            # Look for the proto indexes of the filtered times, locations and features
            location_indexes = []
            validity_times_indexes = []
            feature_indexes = []

            # get the creation timestamp for calculating the validity timedeltas
            creation_ts = self._forecasts_pb.location_forecasts[
                0
            ].creation_ts.ToDatetime()

            # get the location indexes of the proto for the filtered locations
            if locations:
                for location in locations:
                    for l_index, location_forecast in enumerate(
                        self._forecasts_pb.location_forecasts
                    ):
                        if location == Location.from_pb(location_forecast.location):
                            location_indexes.append(l_index)
                            break
            else:
                location_indexes = list(range(num_locations))

            # get the val indexes of the proto for the filtered validity times
            if validity_times:
                for req_validitiy_time in validity_times:
                    for t_index, val_time in enumerate(
                        self._forecasts_pb.location_forecasts[0].forecasts
                    ):
                        if req_validitiy_time == (
                            val_time.valid_at_ts.ToDatetime() - creation_ts
                        ):
                            validity_times_indexes.append(t_index)
                            break
            else:
                validity_times_indexes = list(range(num_times))

            # get the feature indexes of the proto for the filtered features
            if features:
                for req_feature in features:
                    for f_index, feature in enumerate(
                        self._forecasts_pb.location_forecasts[0].forecasts[0].features
                    ):
                        if req_feature == ForecastFeature.from_pb(feature.feature):
                            feature_indexes.append(f_index)
                            break
            else:
                feature_indexes = list(range(num_features))

            array = np.full(
                (
                    len(validity_times_indexes),
                    len(location_indexes),
                    len(feature_indexes),
                ),
                np.nan,
            )

            for l_index in location_indexes:
                for t_index in validity_times_indexes:
                    for f_index in feature_indexes:
                        array[t_index, l_index, f_index] = (
                            self._forecasts_pb.location_forecasts[l_index]
                            .forecasts[t_index]
                            .features[f_index]
                            .value
                        )

            # Check if the array shape matches the number of filtered times, locations and features
            if array.shape[0] != len(validity_times_indexes):
                print(
                    f"Warning:  The count of validity times in the array({array.shape[0]}) does not match the expected time filter count ({validity_times_indexes}."
                )
            if array.shape[1] != len(location_indexes):
                print(
                    f"Warning:  The count of location in the array ({array.shape[1]}) does not match the expected location filter count ({location_indexes})."
                )
            if array.shape[2] != len(feature_indexes):
                print(
                    f"Warning: The count of features ({array.shape[2]}) does not match the feature filter count ({feature_indexes})."
                )

        # catch all exceptions
        except Exception as e:
            raise RuntimeError(f"Error processing forecast data: {e}")

        return array
