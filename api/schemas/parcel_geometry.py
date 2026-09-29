from typing import Any

from pydantic import (
    BaseModel,
    Field,
)


class ParcelGeometryUpdate(
    BaseModel
):

    geometry: dict[
        str,
        Any,
    ] = Field(
        ...,
        description=(
            "GeoJSON Polygon "
            "in EPSG:4326."
        ),
    )


class ParcelGeometryRead(
    BaseModel
):

    parcel_id: str

    geometry: dict[
        str,
        Any,
    ]