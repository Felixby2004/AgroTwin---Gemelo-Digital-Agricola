from datetime import datetime
from typing import Any, Literal

from pydantic import (
    Field,
    model_validator,
)

from api.schemas.common import (
    APIModel,
)


class DecisionTraceRead(
    APIModel
):

    trace_id: str

    created_at: datetime

    parcel_id: str | None

    evidence_ids: list[str]

    knowledge_ids: list[str]

    conflict_ids: list[str]

    transformation_ids: list[str]

    feasible_scenarios: list[Any]

    rejected_scenarios: list[Any]

    ranking: list[Any]

    provisional_recommendation: dict | None

    farmer_response: dict | None

    final_action: dict | None = None

    outcome: dict | None

    metadata: dict


class FarmerDecisionResponseCreate(
    APIModel
):

    response_type: Literal[
        "ACCEPT",
        "MODIFY",
        "REJECT",
    ]

    modified_action: dict[str, Any] | None = None

    rationale: str | None = Field(
            default=None,
            max_length=2000,
        )


    @model_validator(
        mode="after"
    )
    def validate_response(
        self,
    ):

        if (
            self.response_type
            == "MODIFY"
            and
            self.modified_action
            is None
        ):

            raise ValueError(
                "MODIFY requiere "
                "modified_action."
            )


        if (
            self.response_type
            in {
                "ACCEPT",
                "REJECT",
            }
            and
            self.modified_action
            is not None
        ):

            raise ValueError(
                f"{self.response_type} "
                "no debe incluir "
                "modified_action."
            )


        if (
            self.response_type
            == "REJECT"
            and
            (
                self.rationale
                is None
                or
                not self.rationale.strip()
            )
        ):

            raise ValueError(
                "REJECT requiere "
                "una justificación."
            )


        return self