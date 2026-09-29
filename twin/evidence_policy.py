from dataclasses import dataclass
from enum import Enum


class EvidenceUsePolicy(str, Enum):

    USE_NORMALLY = "USE_NORMALLY"

    USE_WITH_CAUTION = "USE_WITH_CAUTION"

    REQUEST_UPDATE = "REQUEST_UPDATE"

    EXCLUDE = "EXCLUDE"


@dataclass
class EvidencePolicyDecision:

    evidence_id: str

    policy: EvidenceUsePolicy

    usable_for_reasoning: bool

    usable_as_current_state: bool

    requires_update: bool

    confidence_weight: float

    reason: str