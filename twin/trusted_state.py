from dataclasses import dataclass, field
from typing import Any

from twin.state_confidence import (
    StateConfidence,
)


@dataclass
class TrustedStateVariable:

    variable: str

    value: Any

    unit: str | None

    source_evidence_ids: list[str]

    confidence: StateConfidence

    metadata: dict = field(
        default_factory=dict
    )


@dataclass
class TrustedTwinState:

    variables: dict[
        str,
        TrustedStateVariable
    ]

    excluded_evidence_ids: list[str]

    update_required_variables: list[str]

    metadata: dict = field(
        default_factory=dict
    )


    def get(
        self,
        variable: str,
    ) -> TrustedStateVariable | None:

        return self.variables.get(
            variable
        )