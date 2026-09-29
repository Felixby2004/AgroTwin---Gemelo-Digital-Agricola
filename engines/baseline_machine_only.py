from twin.biophysical import (
    BiophysicalScenarioResult,
)

from twin.experiment import (
    ExperimentCondition,
    ExperimentMode,
    ExperimentalRunResult,
)


class MachineOnlyBaseline:

    def run(
        self,
        scenarios,
        condition,
        farmer_knowledge=None,
    ) -> ExperimentalRunResult:

        farmer_knowledge = (
            farmer_knowledge or []
        )

        # -------------------------------------------------
        # B0 ignora completamente conocimiento humano.
        #
        # Ranking base:
        # mayor yield_ratio primero.
        # -------------------------------------------------

        ranked = sorted(
            scenarios,
            key=lambda scenario: (
                scenario.yield_ratio
                if scenario.yield_ratio
                is not None
                else float("-inf")
            ),
            reverse=True,
        )

        ranking = []

        for position, scenario in enumerate(
            ranked,
            start=1,
        ):

            ranking.append(
                {
                    "rank": position,
                    "irrigation_mm":
                        scenario.irrigation_mm,
                    "yield_ratio":
                        scenario.yield_ratio,
                    "reason":
                        "Machine-only agronomic ranking",
                }
            )

        recommendation = None

        if ranked:

            recommendation = {
                "irrigation_mm":
                    ranked[0].irrigation_mm,

                "yield_ratio":
                    ranked[0].yield_ratio,

                "source":
                    ExperimentMode
                    .B0_MACHINE_ONLY
                    .value,
            }

        return ExperimentalRunResult(
            mode=(
                ExperimentMode
                .B0_MACHINE_ONLY
            ),

            condition=condition,

            original_scenarios=list(
                scenarios
            ),

            feasible_scenarios=list(
                scenarios
            ),

            rejected_scenarios=[],

            ranking=ranking,

            recommendation=(
                recommendation
            ),

            epistemic_separation_preserved=True,

            state_contamination_detected=False,

            metadata={
                "human_input_used": False,
            },

            ignored_knowledge_ids=[
                item.knowledge_id
                for item in farmer_knowledge
            ],
        )