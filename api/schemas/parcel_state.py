from typing import Any

from api.schemas.common import (
    APIModel,
)


class ParcelSummaryRead(
    APIModel
):
    id: str
    name: str
    crop_type: str | None
    area_ha: float | None


class EvidenceSummaryRead(
    APIModel
):
    total: int
    operational: int
    excluded: int
    update_required: list[str]


class KnowledgeSummaryRead(
    APIModel
):
    total: int
    constraints: int
    preferences: int
    observations: int
    events: int
    local_knowledge: int


class TrustedStateItemRead(
    APIModel
):
    variable: str

    value: Any | None

    unit: str | None

    confidence_score: float | None

    uncertainty_level: str

    requires_update: bool

    selected_evidence_id: str | None


class CurrentRecommendationRead(
    APIModel
):
    status: str

    allowed: bool

    irrigation_mm: float | None

    score: float | None

    reasons: list[str]


class CurrentRiskRead(
    APIModel
):
    level: str

    confidence: float

    requires_human_confirmation: bool

    reasons: list[str]


class LatestTraceRead(
    APIModel
):
    trace_id: str | None

    created_at: str | None

    provisional_recommendation: (
        dict | None
    )

    farmer_response: (
        dict | None
    )

    final_action: (
        dict | None
    )


class ParcelOperationalStateRead(
    APIModel
):
    parcel: ParcelSummaryRead

    quality_gate_status: str

    recommendation_allowed: bool

    evidence: EvidenceSummaryRead

    farmer_knowledge: (
        KnowledgeSummaryRead
    )

    trusted_state: list[
        TrustedStateItemRead
    ]

    conflicts_count: int

    conflicts: list[dict]

    recommendation: (
        CurrentRecommendationRead
    )

    risk: CurrentRiskRead

    latest_trace: LatestTraceRead