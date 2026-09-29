from twin.experiment import (
    ExperimentCondition,
    ExperimentMode,
    ExperimentalRunResult,
)

from engines.baseline_untyped_human import (
    UntypedHumanBaseline,
)


class NoTypingAblation:

    def __init__(self):

        self.base = (
            UntypedHumanBaseline()
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
            .P_NO_TYPED_KNOWLEDGE
        )

        result.metadata[
            "ablation"
        ] = "NO_TYPED_KNOWLEDGE"

        return result