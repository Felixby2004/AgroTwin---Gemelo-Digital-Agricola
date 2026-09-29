from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any

from twin.provenance import ProvenanceRecord


class EvidenceStatus(str, Enum):
    ACTIVE = "ACTIVE"
    STALE = "STALE"
    INVALID = "INVALID"
    SUPERSEDED = "SUPERSEDED"


@dataclass
class MachineEvidence:
    evidence_id: str

    variable: str
    value: Any

    unit: str | None

    observed_at: datetime | None

    provenance: ProvenanceRecord

    status: EvidenceStatus = EvidenceStatus.ACTIVE

    quality_score: float | None = None
    uncertainty: float | None = None

    metadata: dict[str, Any] | None = None