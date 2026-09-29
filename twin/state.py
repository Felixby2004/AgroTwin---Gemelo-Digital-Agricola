from datetime import datetime

from pydantic import BaseModel, Field, model_validator

from twin.crop import Crop
from twin.parcel import Parcel
from twin.soil import Soil
from twin.weather import WeatherState


class TwinState(BaseModel):
    timestamp: datetime

    parcel: Parcel
    soil: Soil
    crop: Crop
    weather: WeatherState

    soil_moisture: float = Field(
        ...,
        ge=0,
        le=1,
        description="Contenido volumétrico actual de agua del suelo",
    )

    previous_soil_moisture: float | None = Field(
        default=None,
        ge=0,
        le=1,
    )

    last_irrigation_mm: float = Field(
        default=0,
        ge=0,
    )

    days_since_irrigation: int | None = Field(
        default=None,
        ge=0,
    )

    ndvi: float | None = Field(
        default=None,
        ge=-1,
        le=1,
    )

    etc_mm_day: float | None = Field(
        default=None,
        ge=0,
    )

    root_zone_depletion_mm: float | None = Field(
        default=None,
        ge=0,
    )

    water_stress_index: float | None = Field(
        default=None,
        ge=0,
        le=1,
    )

    @model_validator(mode="after")
    def validate_soil_moisture(self):
        if self.soil.saturation is not None:
            if self.soil_moisture > self.soil.saturation:
                raise ValueError(
                    "soil_moisture no puede superar la saturación del suelo."
                )

        return self

    @property
    def available_water_fraction(self) -> float:
        """
        Fracción de agua disponible entre punto de marchitez
        y capacidad de campo.

        0 = punto de marchitez
        1 = capacidad de campo
        """
        denominator = (
            self.soil.field_capacity
            - self.soil.wilting_point
        )

        if denominator <= 0:
            return 0.0

        value = (
            self.soil_moisture
            - self.soil.wilting_point
        ) / denominator

        return max(0.0, min(1.0, value))

    @property
    def soil_moisture_pct(self) -> float:
        return self.soil_moisture * 100