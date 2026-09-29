from typing import Any

from api.schemas.common import (
    APIModel,
)


class ReasoningRunRequest(
    APIModel
):
    condition: str


class TrustedVariableRead(
    APIModel
):
    variable: str

    value: Any | None

    unit: str | None

    confidence_score: float | None

    uncertainty_level: str

    requires_update: bool

    selected_evidence_id: str | None


class RankedRecommendationRead(
    APIModel
):
    rank: int

    irrigation_mm: float

    final_score: float

    agronomic_component: float

    marginal_component: float

    preference_component: float

    confidence_factor: float


class ConflictRead(
    APIModel
):
    conflict_id: str

    conflict_type: str

    status: str

    left_item_id: str

    right_item_id: str


class ReasoningRunResponse(
    APIModel
):
    condition: str

    quality_gate_status: str

    recommendation_allowed: bool

    recommendation_status: str

    recommended_irrigation_mm: float | None

    decision_risk: str

    decision_confidence: float

    requires_human_confirmation: bool

    operational_evidence_ids: list[str]

    excluded_evidence_ids: list[str]

    update_required_variables: list[str]

    trusted_state: list[
        TrustedVariableRead
    ]

    conflicts: list[
        ConflictRead
    ]

    ranking: list[
        RankedRecommendationRead
    ]

    provisional_recommendation: (
        dict | None
    )