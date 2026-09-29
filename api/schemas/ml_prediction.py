from pydantic import (
    BaseModel,
    ConfigDict,
)


class SoilMoisturePredictionInput(
    BaseModel
):

    model_config = ConfigDict(
        extra="forbid",
    )

    soil_moisture: float

    soil_moisture_lag_1h: float | None = None
    soil_moisture_lag_3h: float | None = None
    soil_moisture_lag_6h: float | None = None
    soil_moisture_lag_12h: float | None = None
    soil_moisture_lag_24h: float | None = None

    soil_moisture_change_1h: float | None = None
    soil_moisture_change_6h: float | None = None
    soil_moisture_change_12h: float | None = None
    soil_moisture_change_previous_24h: float | None = None

    air_temperature: float | None = None
    rainfall: float | None = None
    solar_radiation: float | None = None
    relative_humidity: float | None = None
    soil_temperature: float | None = None

    rainfall_6h: float | None = None
    rainfall_24h: float | None = None
    rainfall_48h: float | None = None

    temperature_6h_mean: float | None = None
    solar_6h_mean: float | None = None
    humidity_6h_mean: float | None = None

    hour_sin: float | None = None
    hour_cos: float | None = None
    doy_sin: float | None = None
    doy_cos: float | None = None