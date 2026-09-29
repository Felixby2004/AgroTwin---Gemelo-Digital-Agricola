from dataclasses import dataclass
from enum import Enum
from typing import Any


class KnowledgeEffectType(str, Enum):
    ADD_CONTEXT = "ADD_CONTEXT"
    REQUEST_VALIDATION = "REQUEST_VALIDATION"
    ADD_CONFIRMED_EVENT = "ADD_CONFIRMED_EVENT"
    RECOMPUTE_STATE = "RECOMPUTE_STATE"
    FILTER_ACTIONS = "FILTER_ACTIONS"
    MODIFY_RANKING = "MODIFY_RANKING"
    BRANCH_SCENARIO = "BRANCH_SCENARIO"
    NO_COMPUTATIONAL_EFFECT = "NO_COMPUTATIONAL_EFFECT"


@dataclass
class KnowledgeEffect:
    knowledge_id: str

    effect_type: KnowledgeEffectType

    target: str | None = None
    parameters: dict[str, Any] | None = None

    reason: str | None = None