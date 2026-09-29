from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any


class FarmerKnowledgeType(str, Enum):
    OBSERVATION = "OBSERVATION"
    EVENT = "EVENT"
    CONSTRAINT = "CONSTRAINT"
    PREFERENCE = "PREFERENCE"
    LOCAL_KNOWLEDGE = "LOCAL_KNOWLEDGE"


class KnowledgeValidationStatus(str, Enum):
    UNVERIFIED = "UNVERIFIED"
    CONFIRMED = "CONFIRMED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"


class ConstraintType(str, Enum):
    HARD = "HARD"
    SOFT = "SOFT"


@dataclass
class FarmerKnowledgeItem:
    knowledge_id: str

    knowledge_type: FarmerKnowledgeType

    source_id: str
    source_role: str

    payload: Any

    created_at: datetime

    valid_from: datetime | None = None
    valid_until: datetime | None = None

    spatial_scope: str | None = None

    reported_confidence: float | None = None

    validation_status: KnowledgeValidationStatus = (
        KnowledgeValidationStatus.UNVERIFIED
    )

    affects: list[str] | None = None

    constraint_type: ConstraintType | None = None

    rationale: str | None = None

    metadata: dict[str, Any] | None = None


    def validate(
        self,
    ) -> None:

        if not self.knowledge_id:
            raise ValueError(
                "knowledge_id es obligatorio."
            )

        if not self.source_id:
            raise ValueError(
                "source_id es obligatorio."
            )

        if (
            self.reported_confidence is not None
            and not 0 <= self.reported_confidence <= 1
        ):
            raise ValueError(
                "reported_confidence debe estar "
                "entre 0 y 1."
            )

        if (
            self.valid_from is not None
            and self.valid_until is not None
            and self.valid_until < self.valid_from
        ):
            raise ValueError(
                "valid_until no puede ser anterior "
                "a valid_from."
            )

        if (
            self.knowledge_type
            == FarmerKnowledgeType.CONSTRAINT
            and self.constraint_type is None
        ):
            raise ValueError(
                "Una CONSTRAINT debe indicar "
                "constraint_type."
            )