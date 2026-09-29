from datetime import datetime

from pydantic import (
    Field,
)

from api.schemas.common import (
    APIModel,
)


class ParcelCreate(
    APIModel
):

    name: str = Field(
        min_length=1,
        max_length=200,
    )

    crop_type: str | None = Field(
        default=None,
        max_length=100,
    )

    area_ha: float | None = Field(
        default=None,
        gt=0,
    )

    geometry_wkt: str | None = None


class ParcelUpdate(
    APIModel
):

    name: str = Field(
        min_length=1,
        max_length=200,
    )

    crop_type: str | None = Field(
        default=None,
        max_length=100,
    )

    area_ha: float | None = Field(
        default=None,
        gt=0,
    )


class ParcelRead(
    APIModel
):

    id: str

    name: str

    crop_type: str | None

    area_ha: float | None

    created_at: datetime
