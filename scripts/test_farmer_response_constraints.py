import sys
from pathlib import Path
from copy import deepcopy


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

from engines.decision_trace_engine import (
    DecisionTraceEngine,
)

from engines.farmer_response_engine import (
    FarmerResponseEngine,
)

from twin.experiment import (
    ExperimentCondition,
)

from twin.decision_trace import (
    DecisionResponseType,
)


factory = ExperimentalCaseFactory()

orchestrator = (
    ReasoningOrchestrator()
)

trace_engine = (
    DecisionTraceEngine()
)

response_engine = (
    FarmerResponseEngine()
)


case = factory.build(
    ExperimentCondition.COMPLETE
)


reasoning = orchestrator.run(
    scenarios=case.scenarios,
    evidence=case.evidence,
    farmer_knowledge=(
        case.farmer_knowledge
    ),
)


trace = trace_engine.build_trace(
    reasoning_result=reasoning,
    evidence=case.evidence,
    farmer_knowledge=(
        case.farmer_knowledge
    ),
    parcel_id="PARCEL-001",
)


print()
print(
    "FARMER RESPONSE CONSTRAINT TEST"
)
print("=" * 120)


# =========================================================
# ACCEPT
# =========================================================

trace_accept = deepcopy(
    trace
)

response_engine.register_response(
    trace=trace_accept,
    response_type=(
        DecisionResponseType.ACCEPT
    ),
    rationale="Accepted recommendation.",
    farmer_knowledge=(
        case.farmer_knowledge
    ),
)

print(
    "ACCEPT:",
    trace_accept.get_final_action()
)


# =========================================================
# MODIFY VALID
# =========================================================

trace_valid = deepcopy(
    trace
)

response_engine.register_response(
    trace=trace_valid,
    response_type=(
        DecisionResponseType.MODIFY
    ),
    modified_action={
        "irrigation_mm": 10.0,
    },
    rationale="Reduced irrigation.",
    farmer_knowledge=(
        case.farmer_knowledge
    ),
)

print(
    "MODIFY VALID:",
    trace_valid.get_final_action()
)


# =========================================================
# MODIFY INVALID
# =========================================================

trace_invalid = deepcopy(
    trace
)

try:

    response_engine.register_response(
        trace=trace_invalid,
        response_type=(
            DecisionResponseType.MODIFY
        ),
        modified_action={
            "irrigation_mm": 50.0,
        },
        rationale="Attempt above hard limit.",
        farmer_knowledge=(
            case.farmer_knowledge
        ),
    )

    print(
        "MODIFY INVALID: ERROR - "
        "constraint violation was accepted"
    )

except ValueError as exc:

    print(
        "MODIFY INVALID: BLOCKED"
    )

    print(
        "REASON:",
        str(exc)
    )


# =========================================================
# REJECT
# =========================================================

trace_reject = deepcopy(
    trace
)

response_engine.register_response(
    trace=trace_reject,
    response_type=(
        DecisionResponseType.REJECT
    ),
    rationale="Farmer rejects recommendation.",
    farmer_knowledge=(
        case.farmer_knowledge
    ),
)

print(
    "REJECT:",
    trace_reject.get_final_action()
)


print("=" * 120)