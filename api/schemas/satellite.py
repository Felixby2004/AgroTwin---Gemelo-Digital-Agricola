from datetime import datetime

from pydantic import (
    Field,
    model_validator,
)

from api.schemas.common import (
    APIModel,
)


class Sentinel2ObservationCreate(
    APIModel
):

    parcel_id: str

    scene_id: str

    acquired_at: datetime

    # Sentinel-2 spectral bands.
    # They can arrive as normalized reflectance
    # values or equivalent consistent values.

    b04_red: float = Field(
        ge=0.0,
    )

    b08_nir: float = Field(
        ge=0.0,
    )

    b11_swir: float = Field(
        ge=0.0,
    )

    cloud_cover_pct: float = Field(
        ge=0.0,
        le=100.0,
    )

    source_url: str | None = None

    processing_level: str = "L2A"

    metadata: dict = {}


    @model_validator(
        mode="after"
    )
    def validate_bands(
        self,
    ):

        if (
            self.b08_nir
            + self.b04_red
            == 0
        ):
            raise ValueError(
                "NDVI cannot be calculated "
                "because B08 + B04 = 0."
            )

        if (
            self.b08_nir
            + self.b11_swir
            == 0
        ):
            raise ValueError(
                "NDMI cannot be calculated "
                "because B08 + B11 = 0."
            )

        return self


class VegetationIndexRead(
    APIModel
):

    evidence_id: str

    variable: str

    value: float

    unit: str

    status: str

    quality_score: float


class Sentinel2ObservationResult(
    APIModel
):

    parcel_id: str

    scene_id: str

    acquired_at: datetime

    cloud_cover_pct: float

    ndvi: VegetationIndexRead

    ndmi: VegetationIndexRead