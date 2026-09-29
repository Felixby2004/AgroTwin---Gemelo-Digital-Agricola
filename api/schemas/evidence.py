from datetime import datetime

from typing import Any

from api.schemas.common import (
    APIModel,
)


class ProvenanceSchema(
    APIModel
):

    source_type: str

    source_name: str | None = None

    source_id: str | None = None

    source_version: str | None = None

    generated_at: datetime | None = None

    valid_at: datetime | None = None

    spatial_scope: Any | None = None

    transformation: str | None = None

    parent_ids: list[str] = []

    metadata: dict = {}


class MachineEvidenceCreate(
    APIModel
):

    evidence_id: str

    parcel_id: str | None = None

    variable: str

    value: Any

    unit: str | None = None

    observed_at: datetime | None = None

    status: str

    quality_score: float | None = None

    uncertainty: Any | None = None

    provenance: ProvenanceSchema

    metadata: dict = {}


class MachineEvidenceRead(
    MachineEvidenceCreate
):

    pass