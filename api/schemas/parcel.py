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

    # Se conserva por compatibilidad con
    # integraciones antiguas.
    #
    # El área nunca se recibe manualmente:
    # será calculada a partir de la geometría.
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


class ParcelRead(
    APIModel
):

    id: str

    name: str

    crop_type: str | None

    # Read-only desde el punto de vista
    # de la API de parcelas.
    area_ha: float | None

    created_at: datetime