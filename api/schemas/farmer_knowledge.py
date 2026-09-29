from datetime import datetime
from typing import Any

from pydantic import Field

from api.schemas.common import (
    APIModel,
)


class FarmerKnowledgeCreate(
    APIModel
):

    knowledge_id: str

    parcel_id: str | None = None

    knowledge_type: str

    source_id: str

    source_role: str

    payload: dict

    created_at: datetime

    valid_from: datetime | None = None

    valid_until: datetime | None = None

    spatial_scope: Any | None = None

    reported_confidence: float | None = None

    validation_status: str

    affects: list[str] = Field(
        default_factory=list
    )

    constraint_type: str | None = None

    rationale: str | None = None

    metadata: dict = Field(
        default_factory=dict
    )


class FarmerKnowledgeRead(
    APIModel
):

    knowledge_id: str

    parcel_id: str | None = None

    knowledge_type: str

    source_id: str

    source_role: str

    payload: dict

    created_at: datetime

    valid_from: datetime | None = None

    valid_until: datetime | None = None

    spatial_scope: Any | None = None

    reported_confidence: float | None = None

    validation_status: str

    affects: list[str] = Field(
        default_factory=list
    )

    constraint_type: str | None = None

    rationale: str | None = None

    metadata: dict = Field(
        default_factory=dict
    )