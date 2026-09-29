from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class OutcomeStatus(str, Enum):
    PENDING = "PENDING"
    OBSERVED = "OBSERVED"
    PARTIAL = "PARTIAL"
    FAILED = "FAILED"


@dataclass
class DecisionOutcome:
    outcome_id: str

    trace_id: str

    status: OutcomeStatus

    recorded_at: datetime

    executed_action: dict[str, Any] | None = None

    observations: dict[str, Any] = field(
        default_factory=dict
    )

    resulting_evidence_ids: list[str] = field(
        default_factory=list
    )

    deviation_from_final_action: (
        dict[str, Any] | None
    ) = None

    rationale: str | None = None

    metadata: dict[str, Any] | None = None