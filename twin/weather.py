from datetime import datetime

from pydantic import BaseModel, Field


class WeatherState(BaseModel):
    timestamp: datetime

    temperature_c: float

    temperature_min_c: float | None = None
    temperature_max_c: float | None = None

    relative_humidity_pct: float = Field(
        ...,
        ge=0,
        le=100,
    )

    rainfall_mm: float = Field(
        default=0,
        ge=0,
    )

    solar_radiation_mj_m2_day: float | None = Field(
        default=None,
        ge=0,
    )

    wind_speed_m_s: float | None = Field(
        default=None,
        ge=0,
    )

    et0_mm_day: float | None = Field(
        default=None,
        ge=0,
    )

    source: str = "manual"

    quality_flag: str | None = None