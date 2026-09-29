from datetime import datetime
from typing import Any

from api.schemas.common import APIModel


class DataAuditEventRead(
    APIModel
):

    audit_id: str

    parcel_id: str | None

    actor_id: str

    action: str

    allowed: bool

    consent_id: str | None

    purpose: str | None

    data_category: str | None

    created_at: datetime

    details: dict[str, Any]