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

from engines.baseline_machine_only import (
    MachineOnlyBaseline,
)

from engines.baseline_untyped_human import (
    UntypedHumanBaseline,
)

from engines.provenance_aware_experiment import (
    ProvenanceAwareExperiment,
)

from engines.ablation_no_provenance import (
    NoProvenanceAblation,
)

from engines.ablation_no_conflict import (
    NoConflictAblation,
)

from engines.ablation_no_typing import (
    NoTypingAblation,
)


class ExperimentalRunner:

    def __init__(self):

        self.machine_only = (
            MachineOnlyBaseline()
        )

        self.untyped = (
            UntypedHumanBaseline()
        )

        self.provenance_aware = (
            ProvenanceAwareExperiment()
        )

        self.no_provenance = (
            NoProvenanceAblation()
        )

        self.no_conflict = (
            NoConflictAblation()
        )

        self.no_typing = (
            NoTypingAblation()
        )


    def run(
        self,
        mode: ExperimentMode,
        condition: ExperimentCondition,
        scenarios: list[
            BiophysicalScenarioResult
        ],
        evidence: list[
            MachineEvidence
        ],
        farmer_knowledge: list[
            FarmerKnowledgeItem
        ],
    ) -> ExperimentalRunResult:

        if (
            mode
            == ExperimentMode
            .B0_MACHINE_ONLY
        ):

            return self.machine_only.run(
                scenarios=scenarios,
                condition=condition,
                farmer_knowledge=farmer_knowledge,
            )

        if (
            mode
            == ExperimentMode
            .B1_UNTYPED_HUMAN
        ):

            return self.untyped.run(
                scenarios=scenarios,
                evidence=evidence,
                farmer_knowledge=(
                    farmer_knowledge
                ),
                condition=condition,
            )

        if (
            mode
            == ExperimentMode
            .P_PROVENANCE_AWARE
        ):

            return (
                self.provenance_aware
                .run(
                    scenarios=scenarios,
                    evidence=evidence,
                    farmer_knowledge=(
                        farmer_knowledge
                    ),
                    condition=condition,
                )
            )

        if (
            mode
            == ExperimentMode.P_NO_PROVENANCE
        ):

            return self.no_provenance.run(
                scenarios=scenarios,
                evidence=evidence,
                farmer_knowledge=farmer_knowledge,
                condition=condition,
            )


        if (
            mode
            == ExperimentMode.P_NO_CONFLICT_ENGINE
        ):

            return self.no_conflict.run(
                scenarios=scenarios,
                evidence=evidence,
                farmer_knowledge=farmer_knowledge,
                condition=condition,
            )


        if (
            mode
            == ExperimentMode.P_NO_TYPED_KNOWLEDGE
        ):

            return self.no_typing.run(
                scenarios=scenarios,
                evidence=evidence,
                farmer_knowledge=farmer_knowledge,
                condition=condition,
            )

        raise ValueError(
            f"Modo experimental "
            f"no soportado: {mode}"
        )
        