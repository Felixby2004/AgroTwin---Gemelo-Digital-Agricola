from dataclasses import dataclass, field
from enum import Enum


class TwinReadinessStatus(
    str,
    Enum,
):

    READY = "READY"

    DEGRADED = "DEGRADED"

    INSUFFICIENT_DATA = (
        "INSUFFICIENT_DATA"
    )

    BLOCKED = "BLOCKED"


@dataclass
class TwinQualityGateResult:

    status: TwinReadinessStatus

    recommendation_allowed: bool

    degraded_variables: list[str]

    missing_current_state_variables: list[str]

    update_required_variables: list[str]

    blocking_reasons: list[str]

    warnings: list[str]

    metadata: dict = field(
        default_factory=dict
    )