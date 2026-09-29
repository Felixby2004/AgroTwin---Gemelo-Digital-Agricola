from dataclasses import dataclass
from enum import Enum


class UncertaintyLevel(str, Enum):

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    UNKNOWN = "UNKNOWN"


@dataclass
class StateConfidence:

    variable: str

    confidence_score: float | None

    uncertainty_level: UncertaintyLevel

    supporting_evidence_count: int

    current_state_evidence_count: int

    degraded_evidence_count: int

    excluded_evidence_count: int

    requires_update: bool

    rationale: list[str]