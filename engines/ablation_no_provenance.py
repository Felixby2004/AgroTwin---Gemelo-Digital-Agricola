from twin.biophysical import (
    BiophysicalScenarioResult,
)

from twin.evidence import (
    MachineEvidence,
)

from twin.farmer_knowledge import (
    FarmerKnowledgeItem,
)

from twin.experiment import (
    ExperimentCondition,
    ExperimentMode,
    ExperimentalRunResult,
)

from engines.reasoning_orchestrator import (
    ReasoningOrchestrator,
)


class NoProvenanceAblation:

    def __init__(self):

        self.orchestrator = (
            ReasoningOrchestrator()
        )


    def run(
        self,
        scenarios: list[
            BiophysicalScenarioResult
        ],
        evidence: list[
            MachineEvidence
        ],
        farmer_knowledge: list[
            FarmerKnowledgeItem
        ],
        condition: ExperimentCondition,
    ) -> ExperimentalRunResult:

        reasoning = (
            self.orchestrator.run(
                scenarios=scenarios,
                evidence=evidence,
                farmer_knowledge=(
                    farmer_knowledge
                ),
            )
        )

        ranking = []

        for position, item in enumerate(
            reasoning.ranked_scenarios,
            start=1,
        ):

            ranking.append(
                {
                    "rank": position,

                    "irrigation_mm":
                        item.scenario.irrigation_mm,

                    "score":
                        item.score,
                }
            )

        recommendation = None

        if reasoning.ranked_scenarios:

            best = (
                reasoning
                .ranked_scenarios[0]
            )

            recommendation = {
                "irrigation_mm":
                    best.scenario.irrigation_mm,

                "score":
                    best.score,

                "source":
                    ExperimentMode
                    .P_NO_PROVENANCE
                    .value,
            }

        return ExperimentalRunResult(
            mode=(
                ExperimentMode
                .P_NO_PROVENANCE
            ),

            condition=condition,

            original_scenarios=list(
                scenarios
            ),

            feasible_scenarios=(
                reasoning.feasible_scenarios
            ),

            rejected_scenarios=(
                reasoning.rejected_scenarios
            ),

            ranking=ranking,

            recommendation=(
                recommendation
            ),

            # Intencionalmente eliminamos
            # provenance-linked structures
            conflicts=(
                reasoning.conflicts
            ),

            transformations=[],

            knowledge_effects=(
                reasoning.knowledge_effects
            ),

            processed_knowledge_ids=[
                item.knowledge_id
                for item
                in farmer_knowledge
            ],

            applied_knowledge_ids=[
                item.knowledge_id
                for item
                in farmer_knowledge
                if item.knowledge_type.value
                in {
                    "CONSTRAINT",
                    "PREFERENCE",
                }
            ],

            ignored_knowledge_ids=[],

            epistemic_separation_preserved=True,

            state_contamination_detected=False,

            metadata={
                "human_input_typed": True,

                "provenance_enabled": False,

                "ablation":
                    "NO_PROVENANCE",
            },
        )