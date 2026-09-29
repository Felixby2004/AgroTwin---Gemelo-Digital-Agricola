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

from engines.decision_risk_engine import (
    DecisionRiskEngine,
)

from twin.experiment import (
    ExperimentCondition,
)


factory = ExperimentalCaseFactory()

orchestrator = ReasoningOrchestrator()

risk_engine = DecisionRiskEngine()


conditions = [
    ExperimentCondition.COMPLETE,
    ExperimentCondition.MISSING_STALE,
    ExperimentCondition.CONFLICT,
]


print()
print("DECISION RISK TEST")
print("=" * 120)


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

    soil_water = (
        reasoning.trusted_state.get(
            "soil_water_state"
        )
    )

    confidence = (
        soil_water.confidence.confidence_score
        if soil_water is not None
        else None
    )

    risk = risk_engine.evaluate(
        quality_gate=reasoning.quality_gate,
        twin_confidence=confidence,
        conflict_count=len(
            reasoning.conflicts
        ),
    )

    print(
        condition.value,
        "| risk=",
        risk.risk_level.value,
        "| confidence=",
        risk.decision_confidence,
        "| confirmation=",
        risk.requires_human_confirmation,
        "| reasons=",
        risk.reasons,
    )


print("=" * 120)
print("TOTAL:", len(conditions))