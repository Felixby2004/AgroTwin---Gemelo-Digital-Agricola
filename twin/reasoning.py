from dataclasses import (
    dataclass,
    field,
)

from twin.biophysical import (
    BiophysicalScenarioResult,
)

from twin.conflicts import (
    ConflictRecord,
)

from twin.knowledge_effects import (
    KnowledgeEffect,
)

from twin.scenario_transformation import (
    ScenarioTransformation,
)

from engines.constraint_engine import (
    ConstraintEvaluation,
)

from engines.preference_ranker import (
    RankedScenario,
)

from twin.trusted_state import (
    TrustedTwinState,
)

from twin.quality_gate import (
    TwinQualityGateResult,
)

from twin.recommendation import (
    RecommendationResult,
)

from twin.decision_risk import (
    DecisionRiskResult,
)

@dataclass
class ReasoningResult:
    original_scenarios: list[
        BiophysicalScenarioResult
    ]

    feasible_scenarios: list[
        BiophysicalScenarioResult
    ]

    rejected_scenarios: list[
        BiophysicalScenarioResult
    ]

    ranked_scenarios: list[
        RankedScenario
    ]

    knowledge_effects: list[
        KnowledgeEffect
    ]

    conflicts: list[
        ConflictRecord
    ]

    constraint_evaluations: list[
        ConstraintEvaluation
    ]

    transformations: list[
        ScenarioTransformation
    ]

    trusted_state: TrustedTwinState | None = None

    operational_evidence_ids: list[str] = field(
        default_factory=list
    )

    excluded_evidence_ids: list[str] = field(
        default_factory=list
    )

    update_required_variables: list[str] = field(
        default_factory=list
    )

    quality_gate: TwinQualityGateResult | None = None

    recommendation_allowed: bool = True

    recommendation_result: RecommendationResult | None = None

    decision_risk: DecisionRiskResult | None = None