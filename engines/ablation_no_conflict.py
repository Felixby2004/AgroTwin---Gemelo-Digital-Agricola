from twin.experiment import (
    ExperimentCondition,
    ExperimentMode,
    ExperimentalRunResult,
)

from engines.provenance_aware_experiment import (
    ProvenanceAwareExperiment,
)


class NoConflictAblation:

    def __init__(self):

        self.base = (
            ProvenanceAwareExperiment()
        )


    def run(
        self,
        scenarios,
        evidence,
        farmer_knowledge,
        condition: ExperimentCondition,
    ) -> ExperimentalRunResult:

        result = self.base.run(
            scenarios=scenarios,
            evidence=evidence,
            farmer_knowledge=farmer_knowledge,
            condition=condition,
        )

        result.mode = (
            ExperimentMode
            .P_NO_CONFLICT_ENGINE
        )

        # Ablación:
        # desaparece detección explícita
        # de conflicto.
        result.conflicts = []

        result.metadata[
            "ablation"
        ] = "NO_CONFLICT_ENGINE"

        return result