from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class DecisionResponseType(str, Enum):
    ACCEPT = "ACCEPT"
    MODIFY = "MODIFY"
    REJECT = "REJECT"
    PENDING = "PENDING"


@dataclass
class DecisionResponse:
    response_type: DecisionResponseType

    responded_at: datetime | None = None

    modified_action: dict[str, Any] | None = None

    rationale: str | None = None

    metadata: dict[str, Any] | None = None


@dataclass
class HumanTwinDecisionTrace:
    trace_id: str

    created_at: datetime

    parcel_id: str | None = None

    evidence_ids: list[str] = field(
        default_factory=list
    )

    knowledge_ids: list[str] = field(
        default_factory=list
    )

    conflict_ids: list[str] = field(
        default_factory=list
    )

    transformation_ids: list[str] = field(
        default_factory=list
    )

    feasible_scenarios: list[
        dict[str, Any]
    ] = field(
        default_factory=list
    )

    rejected_scenarios: list[
        dict[str, Any]
    ] = field(
        default_factory=list
    )

    ranking: list[
        dict[str, Any]
    ] = field(
        default_factory=list
    )

    provisional_recommendation: (
        dict[str, Any] | None
    ) = None

    farmer_response: (
        DecisionResponse | None
    ) = None

    outcome: dict[str, Any] | None = None

    metadata: dict[str, Any] | None = None

    def get_final_action(
        self,
    ) -> dict[str, Any] | None:

        if self.farmer_response is None:
            return None

        if (
            self.farmer_response.response_type
            == DecisionResponseType.ACCEPT
        ):
            return self.provisional_recommendation

        if (
            self.farmer_response.response_type
            == DecisionResponseType.MODIFY
        ):
            return (
                self.farmer_response
                .modified_action
            )

        if (
            self.farmer_response.response_type
            == DecisionResponseType.REJECT
        ):
            return None

        return None