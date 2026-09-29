from typing import Any

from pydantic import (
    Field,
    model_validator,
)

from api.schemas.common import (
    APIModel,
)


class FarmerResponseRequest(
    APIModel
):
    response_type: str

    modified_action: (
        dict[str, Any]
        | None
    ) = None

    rationale: str | None = None

    @model_validator(
        mode="after"
    )
    def validate_response(
        self,
    ):

        allowed = {
            "ACCEPT",
            "MODIFY",
            "REJECT",
        }

        response_type = (
            self.response_type.upper()
        )

        if response_type not in allowed:

            raise ValueError(
                "response_type must be "
                "ACCEPT, MODIFY or REJECT."
            )

        self.response_type = (
            response_type
        )

        if (
            response_type == "MODIFY"
            and
            self.modified_action
            is None
        ):
            raise ValueError(
                "modified_action is required "
                "when response_type=MODIFY."
            )

        if (
            response_type != "MODIFY"
            and
            self.modified_action
            is not None
        ):
            raise ValueError(
                "modified_action is only "
                "allowed for MODIFY."
            )

        return self


class FarmerResponseResult(
    APIModel
):
    trace_id: str

    response_type: str

    accepted: bool

    modified_action: (
        dict[str, Any]
        | None
    )

    final_action: (
        dict[str, Any]
        | None
    )

    rationale: str | None

    provisional_recommendation: (
        dict[str, Any]
        | None
    )

    message: str