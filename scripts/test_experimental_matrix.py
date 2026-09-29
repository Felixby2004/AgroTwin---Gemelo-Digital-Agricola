import sys
from pathlib import Path


ROOT_DIR = (
    Path(__file__)
    .resolve()
    .parent
    .parent
)

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(
        0,
        str(ROOT_DIR),
    )


from experiments.case_factory import (
    ExperimentalCaseFactory,
)

from engines.experimental_runner import (
    ExperimentalRunner,
)

from twin.experiment import (
    ExperimentMode,
    ExperimentCondition,
)


factory = ExperimentalCaseFactory()

runner = ExperimentalRunner()


modes = [
    ExperimentMode.B0_MACHINE_ONLY,
    ExperimentMode.B1_UNTYPED_HUMAN,
    ExperimentMode.P_PROVENANCE_AWARE,
]


conditions = [
    ExperimentCondition.COMPLETE,
    ExperimentCondition.MISSING_STALE,
    ExperimentCondition.CONFLICT,
]


results = []


print()
print("EXPERIMENTAL MATRIX B0 / B1 / P")
print("=" * 150)


for condition in conditions:

    case = factory.build(
        condition
    )

    print()
    print(
        "CONDITION:",
        condition.value,
    )

    print("=" * 150)

    for mode in modes:

        result = runner.run(
            mode=mode,

            condition=condition,

            scenarios=case.scenarios,

            evidence=case.evidence,

            farmer_knowledge=(
                case.farmer_knowledge
            ),
        )

        results.append(
            result
        )

        recommendation_mm = None

        if result.recommendation is not None:

            recommendation_mm = (
                result
                .recommendation
                .get(
                    "irrigation_mm"
                )
            )

        print()
        print(
            "MODE:",
            result.mode.value,
        )

        print(
            "Recommendation:",
            recommendation_mm,
        )

        print(
            "Feasible:",
            [
                scenario.irrigation_mm
                for scenario
                in result.feasible_scenarios
            ],
        )

        print(
            "Rejected:",
            [
                scenario.irrigation_mm
                for scenario
                in result.rejected_scenarios
            ],
        )

        print(
            "Conflicts:",
            len(
                result.conflicts
            ),
        )

        print(
            "Transformations:",
            len(
                result.transformations
            ),
        )

        print(
            "Epistemic separation:",
            result
            .epistemic_separation_preserved,
        )

        print(
            "State contamination:",
            result
            .state_contamination_detected,
        )

        print(
            "Processed knowledge:",
            result.processed_knowledge_ids,
        )

        print(
            "Applied knowledge:",
            result.applied_knowledge_ids,
        )

        print(
            "Ignored knowledge:",
            result.ignored_knowledge_ids,
        )

        print("-" * 150)


print()
print("=" * 150)
print(
    "TOTAL RUNS:",
    len(results),
)
print("=" * 150)