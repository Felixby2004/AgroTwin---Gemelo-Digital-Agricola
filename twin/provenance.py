from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any


class EvidenceSourceType(str, Enum):
    MEASURED = "MEASURED"
    EXTERNAL = "EXTERNAL"
    MODEL_DERIVED = "MODEL_DERIVED"
    SYNTHETIC = "SYNTHETIC"


@dataclass
class ProvenanceRecord:
    source_type: EvidenceSourceType

    source_name: str
    source_id: str | None = None
    source_version: str | None = None

    generated_at: datetime | None = None
    valid_at: datetime | None = None

    spatial_scope: str | None = None

    transformation: str | None = None
    parent_ids: list[str] | None = None

    metadata: dict[str, Any] | None = None