from dataclasses import dataclass, field
from enum import Enum

from twin.biophysical import (
    BiophysicalScenarioResult,
)

from twin.scenario_decision import (
    ScenarioDecisionMetrics,
)


class RecommendationStatus(
    str,
    Enum,
):

    RECOMMENDED = "RECOMMENDED"

    BLOCKED = "BLOCKED"

    NO_FEASIBLE_SCENARIOS = (
        "NO_FEASIBLE_SCENARIOS"
    )


@dataclass
class ScenarioRecommendationScore:

    scenario: BiophysicalScenarioResult

    metrics: ScenarioDecisionMetrics

    agronomic_component: float

    marginal_component: float

    preference_component: float

    confidence_factor: float

    final_score: float

    reasons: list[str] = field(
        default_factory=list
    )


@dataclass
class RecommendationResult:

    status: RecommendationStatus

    recommended_scenario: (
        BiophysicalScenarioResult
        | None
    )

    ranked_scenarios: list[
        ScenarioRecommendationScore
    ]

    recommendation_allowed: bool

    reason: str

    metadata: dict = field(
        default_factory=dict
    )