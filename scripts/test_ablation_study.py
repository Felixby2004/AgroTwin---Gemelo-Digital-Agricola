import sys
from pathlib import Path

import pandas as pd


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

from engines.experimental_metrics_engine import (
    ExperimentalMetricsEngine,
)

from twin.experiment import (
    ExperimentMode,
    ExperimentCondition,
)


factory = ExperimentalCaseFactory()

runner = ExperimentalRunner()

metrics_engine = (
    ExperimentalMetricsEngine()
)


modes = [
    ExperimentMode.P_PROVENANCE_AWARE,

    ExperimentMode.P_NO_PROVENANCE,

    ExperimentMode.P_NO_CONFLICT_ENGINE,

    ExperimentMode.P_NO_TYPED_KNOWLEDGE,
]


conditions = [
    ExperimentCondition.COMPLETE,
    ExperimentCondition.MISSING_STALE,
    ExperimentCondition.CONFLICT,
]


rows = []


for condition in conditions:

    case = factory.build(
        condition
    )

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

        metrics = (
            metrics_engine.calculate(
                result=result,
                farmer_knowledge=(
                    case.farmer_knowledge
                ),
            )
        )

        rows.append(
            {
                "mode":
                    metrics.mode,

                "condition":
                    metrics.condition,

                "provenance":
                    metrics
                    .provenance_completeness,

                "trace":
                    metrics
                    .trace_completeness,

                "typing":
                    metrics
                    .typing_correctness,

                "epistemic":
                    metrics
                    .epistemic_separation_score,

                "contamination":
                    metrics
                    .state_contamination_rate,

                "conflict_recall":
                    metrics
                    .conflict_recall,

                "knowledge_traceability":
                    metrics
                    .applied_knowledge_traceability_rate,

                "constraint_violation":
                    metrics
                    .recommendation_constraint_violation,

                "recommendation_mm":
                    metrics
                    .recommendation_irrigation_mm,
            }
        )


df = pd.DataFrame(
    rows
)


print()
print("ABLATION STUDY")
print("=" * 180)

print(
    df.to_string(
        index=False
    )
)

print("=" * 180)

print(
    "TOTAL ABLATION RUNS:",
    len(df),
)