from datetime import (
    datetime,
)

from enum import Enum
from typing import Any

from pydantic import (
    Field,
    field_validator,
)

from api.schemas.common import (
    APIModel,
)


class SensorVariable(
    str,
    Enum,
):
    SOIL_MOISTURE = "soil_moisture"
    AIR_TEMPERATURE = "air_temperature"
    RELATIVE_HUMIDITY = "relative_humidity"
    RAINFALL = "rainfall"
    FLOW_RATE = "flow_rate"


class SensorOperationalStatus(
    str,
    Enum,
):
    ACTIVE = "ACTIVE"
    STALE = "STALE"
    NO_DATA = "NO_DATA"
    ERROR = "ERROR"
    INACTIVE = "INACTIVE"


class SensorCreate(
    APIModel
):
    sensor_id: str
    parcel_id: str
    name: str
    sensor_type: str
    variables: list[SensorVariable] = Field(
        min_length=1,
    )
    latitude: float | None = Field(
        default=None,
        ge=-90.0,
        le=90.0,
    )
    longitude: float | None = Field(
        default=None,
        ge=-180.0,
        le=180.0,
    )
    manufacturer: str | None = None
    model: str | None = None
    installed_at: datetime | None = None
    is_active: bool = True
    metadata: dict[str, Any] = Field(
        default_factory=dict,
    )

    @field_validator(
        "sensor_id",
        "name",
        "sensor_type",
    )
    @classmethod
    def validate_required_text(
        cls,
        value: str,
    ) -> str:

        value = value.strip()

        if not value:
            raise ValueError(
                "Value cannot be empty."
            )

        return value


class SensorUpdate(
    APIModel
):
    name: str
    sensor_type: str
    variables: list[SensorVariable] = Field(
        min_length=1,
    )
    latitude: float | None = Field(
        default=None,
        ge=-90.0,
        le=90.0,
    )
    longitude: float | None = Field(
        default=None,
        ge=-180.0,
        le=180.0,
    )
    manufacturer: str | None = None
    model: str | None = None
    installed_at: datetime | None = None
    is_active: bool = True
    metadata: dict[str, Any] = Field(
        default_factory=dict,
    )


class SensorRead(
    APIModel
):
    sensor_id: str
    parcel_id: str
    name: str
    sensor_type: str
    variables: list[str]
    latitude: float | None
    longitude: float | None
    manufacturer: str | None
    model: str | None
    installed_at: datetime | None
    is_active: bool
    operational_status: str
    latest_value: Any | None
    latest_unit: str | None
    latest_variable: str | None
    latest_quality_score: float | None
    latest_observed_at: datetime | None
    metadata: dict[str, Any]
    created_at: datetime
    updated_at: datetime


class SensorReadingCreate(
    APIModel
):
    parcel_id: str

    sensor_id: str

    variable: SensorVariable

    value: float

    unit: str

    observed_at: datetime

    quality_score: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
    )

    latitude: float | None = Field(
        default=None,
        ge=-90.0,
        le=90.0,
    )

    longitude: float | None = Field(
        default=None,
        ge=-180.0,
        le=180.0,
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict,
    )


    @field_validator(
        "sensor_id"
    )
    @classmethod
    def validate_sensor_id(
        cls,
        value: str,
    ) -> str:

        value = value.strip()

        if not value:
            raise ValueError(
                "sensor_id cannot be empty."
            )

        return value


class SensorReadingResult(
    APIModel
):
    evidence_id: str

    parcel_id: str

    sensor_id: str

    input_variable: str

    canonical_variable: str

    value: Any

    unit: str

    quality_score: float

    status: str

    observed_at: datetime


class SensorReadingHistoryItem(
    APIModel
):
    evidence_id: str
    variable: str
    value: Any
    unit: str | None
    quality_score: float | None
    status: str
    observed_at: datetime | None


class SensorBatchCreate(
    APIModel
):
    readings: list[
        SensorReadingCreate
    ] = Field(
        min_length=1,
        max_length=500,
    )


class SensorBatchResult(
    APIModel
):
    total: int

    active: int

    stale: int

    readings: list[
        SensorReadingResult
    ]
