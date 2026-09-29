from datetime import datetime
from typing import Any

from pydantic import Field

from api.schemas.common import APIModel


class DataConsentCreate(APIModel):

    parcel_id: str

    subject_id: str

    purposes: list[str]

    permissions: list[str]

    allowed_data_categories: list[str]

    valid_until: datetime | None = None

    metadata: dict[str, Any] = Field(
        default_factory=dict,
    )


class DataConsentRead(APIModel):

    consent_id: str

    parcel_id: str

    subject_id: str

    purposes: list[str]

    permissions: list[str]

    allowed_data_categories: list[str]

    created_at: datetime

    valid_until: datetime | None

    status: str

    metadata: dict[str, Any]


class DataConsentStatusUpdate(APIModel):

    status: str


class DataAccessCheckRequest(APIModel):

    actor_id: str

    parcel_id: str

    permission: str

    purpose: str

    data_category: str


class DataAccessCheckResult(APIModel):

    allowed: bool

    reason: str

    consent_id: str | None

    metadata: dict[str, Any]


class ParcelExportRequest(APIModel):

    actor_id: str

    purpose: str = "EXPORT"

    include_geometry: bool = True

    include_evidence: bool = True

    include_farmer_knowledge: bool = True

    include_decision_traces: bool = True


class ParcelExportResult(APIModel):

    parcel_id: str

    generated_at: datetime

    format: str

    data: dict[str, Any]