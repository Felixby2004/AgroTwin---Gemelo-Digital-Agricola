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

from engines.reasoning_orchestrator import (
    ReasoningOrchestrator,
)

from twin.experiment import (
    ExperimentCondition,
)


factory = ExperimentalCaseFactory()

orchestrator = (
    ReasoningOrchestrator()
)


conditions = [
    ExperimentCondition.COMPLETE,
    ExperimentCondition.MISSING_STALE,
    ExperimentCondition.CONFLICT,
]


print()
print(
    "REASONING QUALITY GATE TEST"
)

print("=" * 120)


for condition in conditions:

    case = factory.build(
        condition
    )

    result = orchestrator.run(
        scenarios=case.scenarios,
        evidence=case.evidence,
        farmer_knowledge=(
            case.farmer_knowledge
        ),
    )

    print(
        condition.value,
        "| status=",
        result.quality_gate.status.value,
        "| recommendation_allowed=",
        result.recommendation_allowed,
        "| updates=",
        result.update_required_variables,
        "| conflicts=",
        len(result.conflicts),
    )


print("=" * 120)

print(
    "TOTAL:",
    len(conditions),
)