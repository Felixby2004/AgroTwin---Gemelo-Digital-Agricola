from datetime import datetime
from typing import Any

from pydantic import Field

from api.schemas.common import (
    APIModel,
)


class ParcelMembershipCreate(
    APIModel
):

    user_id: str

    role: str

    metadata: dict[
        str,
        Any
    ] = Field(
        default_factory=dict
    )


class ParcelMembershipRead(
    APIModel
):

    membership_id: str

    parcel_id: str

    user_id: str

    role: str

    created_at: datetime

    metadata: dict[
        str,
        Any
    ]


class ParcelClaimResult(
    APIModel
):

    parcel_id: str

    user_id: str

    role: str

    message: str


class ParcelPermissionsRead(
    APIModel
):

    parcel_id: str

    user_id: str

    system_role: str

    parcel_role: str | None

    permissions: list[str]


class ParcelMembershipUpdate(
    APIModel
):

    role: str
