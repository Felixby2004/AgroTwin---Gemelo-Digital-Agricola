from typing import (
    Any,
)

from pydantic import (
    BaseModel,
)


class ParcelMapFeatureProperties(
    BaseModel
):

    parcel_id: str

    name: str

    crop_type: str | None = None

    area_ha: float | None = None


class ParcelMapFeature(
    BaseModel
):

    type: str = "Feature"

    geometry: dict[
        str,
        Any,
    ]

    properties: (
        ParcelMapFeatureProperties
    )


class ParcelMapFeatureCollection(
    BaseModel
):

    type: str = (
        "FeatureCollection"
    )

    features: list[
        ParcelMapFeature
    ]