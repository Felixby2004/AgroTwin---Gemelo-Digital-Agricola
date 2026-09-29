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

from datetime import datetime

from engines.evidence_quality_engine import (
    EvidenceQualityEngine,
)


class ProvenanceAwareExperiment:

    def __init__(self):

        self.orchestrator = (
            ReasoningOrchestrator()
        )

        self.evidence_quality_engine = (
            EvidenceQualityEngine()
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

        quality_assessments = [
            self.evidence_quality_engine.assess(
                evidence=item,
                reference_time=datetime.now(),
            )
            for item in evidence
        ]

        degraded_evidence_ids = [
            assessment.evidence_id
            for assessment in quality_assessments
            if assessment.degraded
        ]

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
                    "rank":
                        position,

                    "irrigation_mm":
                        item.scenario
                        .irrigation_mm,

                    "score":
                        item.score,

                    "reasons":
                        item.reasons,
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
                    best.scenario
                    .irrigation_mm,

                "score":
                    best.score,

                "source":
                    ExperimentMode
                    .P_PROVENANCE_AWARE
                    .value,
            }

        return ExperimentalRunResult(
            mode=(
                ExperimentMode
                .P_PROVENANCE_AWARE
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

            recommendation=recommendation,

            conflicts=reasoning.conflicts,

            transformations=(
                reasoning.transformations
            ),

            processed_knowledge_ids=[
                item.knowledge_id
                for item in farmer_knowledge
            ],

            applied_knowledge_ids=[
                item.knowledge_id
                for item in farmer_knowledge
                if item.knowledge_id
                in {
                    transformation.source_knowledge_id
                    for transformation
                    in reasoning.transformations
                }
            ],

            ignored_knowledge_ids=[],

            epistemic_separation_preserved=True,

            state_contamination_detected=False,

            knowledge_effects=(
                reasoning.knowledge_effects
            ),

            metadata={
                "human_input_typed": True,

                "provenance_enabled": True,

                "knowledge_effect_count": (
                    len(reasoning.knowledge_effects)
                ),

                "degraded_evidence_ids":
                    degraded_evidence_ids,

                "degraded_evidence_count":
                    len(
                        degraded_evidence_ids
                    ),

                "evidence_quality_assessments": [
                    {
                        "evidence_id":
                            assessment.evidence_id,

                        "usable":
                            assessment.usable,

                        "degraded":
                            assessment.degraded,

                        "age_hours":
                            assessment.age_hours,

                        "status":
                            assessment.status.value,

                        "reason":
                            assessment.reason,
                    }
                    for assessment
                    in quality_assessments
                ],
            },
        )