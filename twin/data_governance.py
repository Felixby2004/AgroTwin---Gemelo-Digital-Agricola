from dataclasses import (
    dataclass,
    field,
)

from datetime import datetime
from enum import Enum
from typing import Any


class DataPurpose(
    str,
    Enum,
):
    DIGITAL_TWIN_OPERATION = (
        "DIGITAL_TWIN_OPERATION"
    )

    RECOMMENDATION = (
        "RECOMMENDATION"
    )

    RESEARCH = (
        "RESEARCH"
    )

    EXPORT = (
        "EXPORT"
    )

    SHARING = (
        "SHARING"
    )


class DataPermission(
    str,
    Enum,
):
    READ = "READ"

    WRITE = "WRITE"

    PROCESS = "PROCESS"

    EXPORT = "EXPORT"

    SHARE = "SHARE"

    DELETE = "DELETE"


class ConsentStatus(
    str,
    Enum,
):
    ACTIVE = "ACTIVE"

    REVOKED = "REVOKED"

    EXPIRED = "EXPIRED"


@dataclass
class DataConsent:

    consent_id: str

    parcel_id: str

    subject_id: str

    purposes: list[
        DataPurpose
    ]

    permissions: list[
        DataPermission
    ]

    allowed_data_categories: list[
        str
    ]

    created_at: datetime

    valid_until: datetime | None = None

    status: ConsentStatus = (
        ConsentStatus.ACTIVE
    )

    metadata: dict[
        str,
        Any
    ] = field(
        default_factory=dict
    )


    def is_active(
        self,
        now: datetime,
    ) -> bool:

        if (
            self.status
            != ConsentStatus.ACTIVE
        ):
            return False


        if (
            self.valid_until
            is not None
            and
            now
            > self.valid_until
        ):
            return False


        return True



@dataclass
class DataAccessRequest:

    actor_id: str

    parcel_id: str

    permission: DataPermission

    purpose: DataPurpose

    data_category: str


@dataclass
class DataAccessDecision:

    allowed: bool

    reason: str

    consent_id: str | None = None

    metadata: dict[
        str,
        Any
    ] = field(
        default_factory=dict
    )