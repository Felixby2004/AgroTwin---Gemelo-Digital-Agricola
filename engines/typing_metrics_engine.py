from twin.farmer_knowledge import (
    FarmerKnowledgeItem,
    FarmerKnowledgeType,
)

from twin.knowledge_effects import (
    KnowledgeEffect,
    KnowledgeEffectType,
)

from twin.typing_metrics import (
    TypingMetrics,
)


class TypingMetricsEngine:

    EXPECTED_EFFECTS = {
        FarmerKnowledgeType.OBSERVATION: {
            KnowledgeEffectType.ADD_CONTEXT,
            KnowledgeEffectType.REQUEST_VALIDATION,
        },

        FarmerKnowledgeType.EVENT: {
            KnowledgeEffectType.REQUEST_VALIDATION,
            KnowledgeEffectType.ADD_CONFIRMED_EVENT,
            KnowledgeEffectType.RECOMPUTE_STATE,
        },

        FarmerKnowledgeType.CONSTRAINT: {
            KnowledgeEffectType.FILTER_ACTIONS,
            KnowledgeEffectType.REQUEST_VALIDATION,
        },

        FarmerKnowledgeType.PREFERENCE: {
            KnowledgeEffectType.MODIFY_RANKING,
            KnowledgeEffectType.REQUEST_VALIDATION,
        },

        FarmerKnowledgeType.LOCAL_KNOWLEDGE: {
            KnowledgeEffectType.BRANCH_SCENARIO,
            KnowledgeEffectType.REQUEST_VALIDATION,
        },
    }


    def calculate(
        self,
        farmer_knowledge: list[
            FarmerKnowledgeItem
        ],
        knowledge_effects: list[
            KnowledgeEffect
        ],
    ) -> TypingMetrics:

        if not farmer_knowledge:

            return TypingMetrics(
                expected_typed_items=0,
                correctly_typed_items=0,
                incorrectly_typed_items=0,
                typing_correctness=None,
            )

        effects_by_knowledge = {}

        for effect in knowledge_effects:

            effects_by_knowledge.setdefault(
                effect.knowledge_id,
                set(),
            ).add(
                effect.effect_type
            )

        correct = 0
        incorrect = 0

        for item in farmer_knowledge:

            expected_effects = (
                self.EXPECTED_EFFECTS.get(
                    item.knowledge_type,
                    set(),
                )
            )

            actual_effects = (
                effects_by_knowledge.get(
                    item.knowledge_id,
                    set(),
                )
            )

            if (
                actual_effects
                and actual_effects.issubset(
                    expected_effects
                )
            ):

                correct += 1

            else:

                incorrect += 1

        total = len(
            farmer_knowledge
        )

        return TypingMetrics(
            expected_typed_items=total,

            correctly_typed_items=correct,

            incorrectly_typed_items=incorrect,

            typing_correctness=(
                correct / total
            ),
        )