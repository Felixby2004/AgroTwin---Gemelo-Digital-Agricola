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

from engines.twin_quality_gate_engine import (
    TwinQualityGateEngine,
)

from twin.experiment import (
    ExperimentCondition,
)


factory = ExperimentalCaseFactory()

orchestrator = (
    ReasoningOrchestrator()
)

quality_gate = (
    TwinQualityGateEngine()
)


conditions = [
    ExperimentCondition.COMPLETE,
    ExperimentCondition.MISSING_STALE,
    ExperimentCondition.CONFLICT,
]


print()
print(
    "TWIN QUALITY GATE TEST"
)

print("=" * 150)


for condition in conditions:

    case = factory.build(
        condition
    )

    reasoning = orchestrator.run(
        scenarios=case.scenarios,
        evidence=case.evidence,
        farmer_knowledge=(
            case.farmer_knowledge
        ),
    )

    gate = quality_gate.evaluate(
        reasoning.trusted_state
    )

    print()

    print(
        "CONDITION:",
        condition.value
    )

    print(
        "STATUS:",
        gate.status.value
    )

    print(
        "RECOMMENDATION ALLOWED:",
        gate.recommendation_allowed
    )

    print(
        "DEGRADED:",
        gate.degraded_variables
    )

    print(
        "MISSING CURRENT STATE:",
        gate
        .missing_current_state_variables
    )

    print(
        "UPDATE REQUIRED:",
        gate.update_required_variables
    )

    print(
        "BLOCKING:",
        gate.blocking_reasons
    )

    print(
        "WARNINGS:",
        gate.warnings
    )

    print("-" * 150)


print(
    "TOTAL CONDITIONS:",
    len(conditions),
)