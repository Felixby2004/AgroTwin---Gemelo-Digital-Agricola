from datetime import datetime

from pydantic import (
    Field,
)

from api.schemas.common import (
    APIModel,
)


class Sentinel2SearchRequest(
    APIModel
):

    bbox: list[float]

    start_date: datetime

    end_date: datetime

    max_cloud_cover: float = Field(
        default=30.0,
        ge=0.0,
        le=100.0,
    )

    limit: int = Field(
        default=10,
        ge=1,
        le=100,
    )


class Sentinel2SceneRead(
    APIModel
):

    scene_id: str

    collection: str | None

    datetime: str | None

    cloud_cover_pct: (
        float
        | None
    )

    bbox: (
        list[float]
        | None
    )

    geometry: dict | None


class Sentinel2SearchResult(
    APIModel
):

    count: int

    scenes: list[
        Sentinel2SceneRead
    ]


class Sentinel2IndicesRequest(
    APIModel
):

    parcel_id: str

    start_date: datetime

    end_date: datetime

    max_cloud_cover: float = Field(
        default=30.0,
        ge=0.0,
        le=100.0,
    )

    resolution_m: float = Field(
        default=10.0,
        gt=0.0,
        le=100.0,
    )

class Sentinel2IndexStatistics(
    APIModel
):

    mean: float

    minimum: float | None

    maximum: float | None

    standard_deviation: float | None

    evidence_id: str


class Sentinel2IndicesResult(
    APIModel
):

    parcel_id: str

    interval: dict

    ndvi: Sentinel2IndexStatistics

    ndmi: Sentinel2IndexStatistics

    sample_count: int

    no_data_count: int

    valid_fraction: float

    source_type: str = "EXTERNAL"