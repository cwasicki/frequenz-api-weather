"""Test the types module."""

from _pytest.logging import LogCaptureFixture

from datetime import timedelta
from google.protobuf.timestamp_pb2 import Timestamp
from frequenz.api.weather import weather_pb2
from frequenz.api.common.v1.location_pb2 import Location as LocationProto
from frequenz.client.weather._types import (
    ForecastFeature,
    Location,
    Forecasts,
)
import numpy as np

class TestForecastFeatureType:
    """Testing the ForecastFeature type."""

    def test_from_pb_valid(self) -> None:
        """Test if the method works correctly when a valid value is passed."""
        # Teste, ob die Methode korrekt arbeitet, wenn ein gültiger Wert übergeben wird
        forecast_feature_pb_value = (
            weather_pb2.ForecastFeature.FORECAST_FEATURE_U_WIND_COMPONENT_100_METRE
        )
        result = ForecastFeature.from_pb(forecast_feature_pb_value)
        assert result == ForecastFeature.U_WIND_COMPONENT_100_METRE

    def test_from_pb_unknown(self) -> None:
        """Test if the method returns UNSPECIFIED when an unknown value is passed."""
        # Teste, ob die Methode UNSPECIFIED zurückgibt, wenn ein unbekannter Wert übergeben wird
        unknown_pb_value = 999999999  # Ein beliebiger unbekannter Wert
        result = ForecastFeature.from_pb(unknown_pb_value)  # type: ignore
        assert result == ForecastFeature.UNSPECIFIED

    def test_from_pb_warning_logged(self, caplog: LogCaptureFixture) -> None:
        """Test if a warning is logged when an unknown value is passed.

        Args:
            caplog: pytest fixture to capture log messages.

        """
        # Teste, ob ein Warnhinweis protokolliert wird, wenn ein unbekannter Wert übergeben wird
        unknown_pb_value = 999999999  # Ein beliebiger unbekannter Wert
        ForecastFeature.from_pb(unknown_pb_value)  # type: ignore
        assert "Unknown forecast feature" in caplog.text

    def test_from_pb_valid_enum(self) -> None:
        """Test if the method works correctly when an enum value is passed."""
        # Teste, ob die Methode korrekt arbeitet, wenn ein Enum-Wert übergeben wird
        forecast_feature_enum_value = ForecastFeature.V_WIND_COMPONENT_100_METRE.value
        result = ForecastFeature.from_pb(forecast_feature_enum_value)
        assert result == ForecastFeature.V_WIND_COMPONENT_100_METRE


class TestLocation:
    """Testing the Location type."""

    def test_from_pb(self) -> None:
        """Test if the inititlization method from proto works correctly."""
        # Erstellen Sie ein Protobuf-Objekt
        location_proto = LocationProto(latitude=42.0, longitude=18.0, country_code="US")
        result = Location.from_pb(location_proto)

        # Überprüfen Sie, ob die Methode korrekt funktioniert
        assert result.latitude == 42.0
        assert result.longitude == 18.0
        assert result.country_code == "US"

    def test_to_pb(self) -> None:
        """Test if the to_pb method works correctly."""
        # Erstellen Sie ein Location-Objekt
        location = Location(latitude=37.0, longitude=-122.0, country_code="CA")
        result = location.to_pb()

        # Überprüfen Sie, ob die Methode korrekt funktioniert
        assert result.latitude == 37.0
        assert result.longitude == -122.0
        assert result.country_code == "CA"

    def test_round_trip(self) -> None:
        """Test if the round trip from Location to proto and back works correctly."""
        # Überprüfen Sie, ob die Umwandlung von Location zu Protobuf und zurück korrekt funktioniert
        original_location = Location(latitude=37.0, longitude=-122.0, country_code="CA")
        location_proto = original_location.to_pb()
        result_location = Location.from_pb(location_proto)

        assert result_location.latitude == original_location.latitude
        assert result_location.longitude == original_location.longitude
        assert result_location.country_code == original_location.country_code


class TestForecasts:
    """Testing the Forecasts type.

    Attributes:
        forecasts_proto: example ReceiveLiveWeatherForecastResponse proto object
        num_times: number of times in the example proto object
        num_locations: number of locations in the example proto object
        num_features: number of features in the example proto object

    """

    def __init__(self) -> None:
        """Initialize the test class."""
        self.forecasts_proto = self.setup_method()
        self.num_times = 3
        self.num_locations = 2
        self.num_features = 3

    def setup_method(self) -> weather_pb2.ReceiveLiveWeatherForecastResponse:
        """Create a example ReceiveLiveWeatherForecastResponse proto object.

        Returns: ReceiveLiveWeatherForecastResponse proto object
        """
        # Create a list of FeatureForecast objects (replace with actual FeatureForecast objects)
        feature_forecasts_list = []
        some_feature_values = [
            weather_pb2.ForecastFeature.FORECAST_FEATURE_U_WIND_COMPONENT_100_METRE,
            weather_pb2.ForecastFeature.FORECAST_FEATURE_V_WIND_COMPONENT_100_METRE,
            weather_pb2.ForecastFeature.FORECAST_FEATURE_SURFACE_SOLAR_RADIATION_DOWNWARDS,
        ]
        some_float_values = [100, 200, 300]

        for feature, value in zip(some_feature_values, some_float_values):
            forecast = weather_pb2.LocationForecast.Forecasts.FeatureForecast(
                feature=feature, value=value
            )
            feature_forecasts_list.append(forecast)

        many_forecasts = []

        # adding different valid_ts into valid_ts_list

        valid_ts1 = Timestamp()
        valid_ts1.FromJsonString("2024-01-01T01:00:00Z")

        valid_ts2 = Timestamp()
        valid_ts2.FromJsonString("2024-01-01T02:00:00Z")

        valid_ts3 = Timestamp()
        valid_ts3.FromJsonString("2024-01-01T03:00:00Z")

        valid_ts_list = [valid_ts1, valid_ts2, valid_ts3]

        # adding same forecast for different valid_ts into many_forecasts

        for valid_ts in valid_ts_list:
            full_features_forecasts = weather_pb2.LocationForecast.Forecasts(
                valid_at_ts=valid_ts, features=feature_forecasts_list
            )
            many_forecasts.append(full_features_forecasts)

        some_locations_forecasts = []

        some_creation_ts = Timestamp()
        some_creation_ts.FromJsonString("2024-01-01T00:00:00Z")

        # adding different locations into locations_list
        locations = [
            LocationProto(latitude=42.0, longitude=18.0, country_code="US"),
            LocationProto(latitude=43.0, longitude=19.0, country_code="CA"),
        ]

        for location in locations:
            location_forecast = weather_pb2.LocationForecast(
                forecasts=many_forecasts,
                location=location,
                creation_ts=some_creation_ts,
            )
            some_locations_forecasts.append(location_forecast)

        # creating a ReceiveLiveWeatherForecastResponse proto object
        forecasts_proto = weather_pb2.ReceiveLiveWeatherForecastResponse(
            location_forecasts=some_locations_forecasts
        )

        return forecasts_proto

    def test_from_pb(self) -> None:
        """Test if the inititlization method from proto works correctly."""
        # creating a Forecasts object
        forecasts = Forecasts.from_pb(self.forecasts_proto)

        assert forecasts is not None

        # forecast is created from the example proto object

    def test_to_ndarray_vlf_with_no_parameters(self) -> None:
        """Test if the to_ndarray method works correctly when no filter parameters are passed."""
        # create an example Forecasts object
        forecasts = Forecasts.from_pb(self.forecasts_proto)

        # checks if output is a numpy array
        array = forecasts.to_ndarray_vlf_refined()
        assert isinstance(
            array, np.ndarray
        )  # Stellen Sie sicher, dass ein Numpy-Array zurückgegeben wurde

        assert array.shape == (
            self.num_times,
            self.num_locations,
            self.num_features,
        )
        assert array[0, 0, 0] == 100

    def test_to_ndarray_vlf_with_some_parameters(self) -> None:
        """Test if the to_ndarray method works correctly when some filter parameters are passed."""
        # Erstellen Sie ein Beispiel für ein Forecasts-Objekt
        forecasts = Forecasts.from_pb(self.forecasts_proto)

        # Führen Sie die Methode mit optionalen Parametern aus
        validity_times = [timedelta(hours=6), timedelta(hours=3)]
        locations = [Location(latitude=42.0, longitude=18.0, country_code="US")]
        features = [
            ForecastFeature.V_WIND_COMPONENT_100_METRE,
            ForecastFeature.U_WIND_COMPONENT_100_METRE,
        ]

        array = forecasts.to_ndarray_vlf_refined(
            validity_times=validity_times, locations=locations, features=features
        )

        # Überprüfen Sie, ob das Ergebnis den Erwartungen entspricht
        assert isinstance(array, np.ndarray)
        assert array.shape == (len(validity_times), len(locations), len(features))
        assert array[0, 0, 0] == 200

    def test_to_ndarray_vlf_with_all_parameters(self) -> None:
        """Test if the to_ndarray method works correctly when all filter parameters are passed."""
        # Erstellen Sie ein Beispiel für ein Forecasts-Objekt
        forecasts = Forecasts.from_pb(self.forecasts_proto)

        # Führen Sie die Methode mit optionalen Parametern aus
        validity_times = [timedelta(hours=3), timedelta(hours=6)]
        locations = [
            Location(latitude=42.0, longitude=18.0, country_code="US"),
            Location(latitude=43.0, longitude=19.0, country_code="CA"),
        ]

        features = [
            ForecastFeature.U_WIND_COMPONENT_100_METRE,
            ForecastFeature.V_WIND_COMPONENT_100_METRE,
            ForecastFeature.SURFACE_SOLAR_RADIATION_DOWNWARDS,
        ]

        array = forecasts.to_ndarray_vlf_refined(
            validity_times=validity_times, locations=locations, features=features
        )

        # Überprüfen Sie, ob das Ergebnis den Erwartungen entspricht
        assert isinstance(array, np.ndarray)
        assert array.shape == (len(validity_times), len(locations), len(features))

    def test_to_ndarray_vlf_with_missing_parameters(self) -> None:
        """Test if the to_ndarray method works correctly when some filter parameters are missing"""
        # Erstellen Sie ein Beispiel für ein Forecasts-Objekt
        forecasts = Forecasts.from_pb(self.forecasts_proto)

        # Führen Sie die Methode mit optionalen Parametern aus
        validity_times = [timedelta(hours=3), timedelta(hours=6), timedelta(days=1)]
        locations = [
            Location(latitude=50.0, longitude=18.0, country_code="US"),
            Location(latitude=43.0, longitude=19.0, country_code="CA"),
        ]

        features = [
            ForecastFeature.U_WIND_COMPONENT_100_METRE,
            ForecastFeature.V_WIND_COMPONENT_100_METRE,
            ForecastFeature.SURFACE_SOLAR_RADIATION_DOWNWARDS,
            ForecastFeature.SURFACE_NET_SOLAR_RADIATION,
        ]

        array = forecasts.to_ndarray_vlf_refined(
            validity_times=validity_times, locations=locations, features=features
        )

        # Überprüfen Sie, ob das Ergebnis den Erwartungen entspricht
        assert isinstance(array, np.ndarray)
        assert array.shape == (
            len(validity_times) - 1,
            len(locations) - 1,
            len(features) - 1,
        )
