from api.schemas.common import (
    APIModel,
)


class ScenarioScoreRead(
    APIModel
):

    irrigation_mm: float

    final_score: float

    agronomic_component: float

    marginal_component: float

    preference_component: float

    confidence_factor: float

    reasons: list[str]


class RecommendationRead(
    APIModel
):

    status: str

    recommendation_allowed: bool

    recommended_irrigation_mm: float | None

    reason: str

    ranked_scenarios: list[
        ScenarioScoreRead
    ]


class DecisionRiskRead(
    APIModel
):

    risk_level: str

    decision_confidence: float

    requires_human_confirmation: bool

    reasons: list[str]