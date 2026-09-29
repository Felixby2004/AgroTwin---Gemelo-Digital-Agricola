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
print("INTEGRATED RECOMMENDATION TEST")
print("=" * 140)


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

    recommendation = (
        result.recommendation_result
    )

    risk = (
        result.decision_risk
    )

    irrigation = None

    if (
        recommendation
        and
        recommendation.recommended_scenario
        is not None
    ):

        irrigation = (
            recommendation
            .recommended_scenario
            .irrigation_mm
        )

    print(
        condition.value,
        "| recommendation_status=",
        recommendation.status.value,
        "| irrigation=",
        irrigation,
        "| risk=",
        risk.risk_level.value,
        "| confirmation=",
        risk.requires_human_confirmation,
        "| conflicts=",
        len(result.conflicts),
    )


print("=" * 140)

print(
    "TOTAL:",
    len(conditions),
)