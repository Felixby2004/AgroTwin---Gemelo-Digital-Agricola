from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from twin.biophysical import (
    BiophysicalScenarioResult,
)

from twin.conflicts import (
    ConflictRecord,
)

from twin.scenario_transformation import (
    ScenarioTransformation,
)

from twin.knowledge_effects import (
    KnowledgeEffect,
)

class ExperimentMode(str, Enum):
    B0_MACHINE_ONLY = "B0_MACHINE_ONLY"
    B1_UNTYPED_HUMAN = "B1_UNTYPED_HUMAN"
    P_PROVENANCE_AWARE = "P_PROVENANCE_AWARE"

    P_NO_PROVENANCE = "P_NO_PROVENANCE"
    P_NO_CONFLICT_ENGINE = "P_NO_CONFLICT_ENGINE"
    P_NO_TYPED_KNOWLEDGE = "P_NO_TYPED_KNOWLEDGE"


class ExperimentCondition(str, Enum):
    COMPLETE = "COMPLETE"
    MISSING_STALE = "MISSING_STALE"
    CONFLICT = "CONFLICT"


@dataclass
class ExperimentalRunResult:
    mode: ExperimentMode

    condition: ExperimentCondition

    original_scenarios: list[
        BiophysicalScenarioResult
    ]

    feasible_scenarios: list[
        BiophysicalScenarioResult
    ]

    rejected_scenarios: list[
        BiophysicalScenarioResult
    ]

    ranking: list[
        dict[str, Any]
    ]

    recommendation: (
        dict[str, Any] | None
    )

    conflicts: list[
        ConflictRecord
    ] = field(
        default_factory=list
    )

    transformations: list[
        ScenarioTransformation
    ] = field(
        default_factory=list
    )

    ignored_knowledge_ids: list[str] = field(
        default_factory=list
    )

    applied_knowledge_ids: list[str] = field(
        default_factory=list
    )

    epistemic_separation_preserved: bool = True

    state_contamination_detected: bool = False

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    processed_knowledge_ids: list[str] = field(
        default_factory=list
    )

    knowledge_effects: list[
        KnowledgeEffect
    ] = field(
        default_factory=list
    )