from dataclasses import dataclass
from enum import Enum


class DecisionRiskLevel(str, Enum):
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    BLOCKED = "BLOCKED"


@dataclass
class DecisionRiskResult:
    risk_level: DecisionRiskLevel
    decision_confidence: float
    requires_human_confirmation: bool
    reasons: list[str]