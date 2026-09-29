from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any


class TransformationType(str, Enum):
    ACTION_REMOVED = "ACTION_REMOVED"
    ACTION_RERANKED = "ACTION_RERANKED"
    SCENARIO_BRANCHED = "SCENARIO_BRANCHED"
    STATE_RECOMPUTED = "STATE_RECOMPUTED"
    CONTEXT_ADDED = "CONTEXT_ADDED"


@dataclass
class ScenarioTransformation:
    transformation_id: str

    transformation_type: TransformationType

    source_knowledge_id: str

    affected_scenario: str | None = None

    before_value: Any | None = None
    after_value: Any | None = None

    reason: str | None = None

    created_at: datetime | None = None

    metadata: dict[str, Any] | None = None