from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any


class ConflictType(str, Enum):
    HUMAN_VS_MACHINE = "HUMAN_VS_MACHINE"
    HUMAN_VS_HUMAN = "HUMAN_VS_HUMAN"
    MACHINE_VS_MACHINE = "MACHINE_VS_MACHINE"
    CONSTRAINT_VIOLATION = "CONSTRAINT_VIOLATION"
    TEMPORAL_CONFLICT = "TEMPORAL_CONFLICT"
    SPATIAL_CONFLICT = "SPATIAL_CONFLICT"


class ConflictStatus(str, Enum):
    OPEN = "OPEN"
    VALIDATION_REQUIRED = "VALIDATION_REQUIRED"
    RESOLVED = "RESOLVED"
    ACCEPTED_AS_UNCERTAINTY = "ACCEPTED_AS_UNCERTAINTY"


class ConflictAction(str, Enum):
    PRESERVE_BOTH = "PRESERVE_BOTH"
    REQUEST_VALIDATION = "REQUEST_VALIDATION"
    RECOMPUTE_STATE = "RECOMPUTE_STATE"
    BRANCH_SCENARIOS = "BRANCH_SCENARIOS"
    REMOVE_INFEASIBLE_ACTION = "REMOVE_INFEASIBLE_ACTION"
    RERANK_SCENARIOS = "RERANK_SCENARIOS"


@dataclass
class ConflictRecord:
    conflict_id: str

    conflict_type: ConflictType
    status: ConflictStatus

    left_item_id: str
    right_item_id: str

    variable: str | None = None

    spatial_overlap: bool = False
    temporal_overlap: bool = False

    description: str | None = None

    recommended_actions: list[ConflictAction] | None = None

    detected_at: datetime | None = None
    resolved_at: datetime | None = None

    metadata: dict[str, Any] | None = None