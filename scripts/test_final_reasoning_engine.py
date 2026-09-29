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


conditions = [
    ExperimentCondition.COMPLETE,
    ExperimentCondition.MISSING_STALE,
    ExperimentCondition.CONFLICT,
]


print()
print(
    "FINAL REASONING ENGINE TEST"
)

print("=" * 160)


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


    recommendation = (
        reasoning
        .recommendation_result
    )

    risk = (
        reasoning
        .decision_risk
    )


    irrigation = None

    if (
        recommendation is not None
        and
        recommendation
        .recommended_scenario
        is not None
    ):

        irrigation = (
            recommendation
            .recommended_scenario
            .irrigation_mm
        )


    print()
    print(
        "CONDITION:",
        condition.value
    )

    print(
        "QUALITY GATE:",
        reasoning
        .quality_gate
        .status
        .value
    )

    print(
        "RECOMMENDATION ALLOWED:",
        reasoning
        .recommendation_allowed
    )

    print(
        "RECOMMENDATION STATUS:",
        recommendation
        .status
        .value
    )

    print(
        "IRRIGATION:",
        irrigation
    )

    print(
        "RISK:",
        risk
        .risk_level
        .value
    )

    print(
        "HUMAN CONFIRMATION:",
        risk
        .requires_human_confirmation
    )

    print(
        "CONFLICTS:",
        len(
            reasoning.conflicts
        )
    )

    print(
        "UPDATE REQUIRED:",
        reasoning
        .update_required_variables
    )


    # =====================================================
    # DECISION TRACE
    # =====================================================

    trace = trace_engine.build_trace(
        reasoning_result=reasoning,

        evidence=case.evidence,

        farmer_knowledge=(
            case.farmer_knowledge
        ),

        parcel_id=(
            "PARCEL-001"
        ),
    )


    print(
        "TRACE RECOMMENDATION:",
        trace
        .provisional_recommendation
    )


    # =====================================================
    # SOLO PROBAR RESPUESTA HUMANA SI HAY RECOMENDACIÓN
    # =====================================================

    if (
        trace
        .provisional_recommendation
        is not None
    ):

        trace_accept = deepcopy(
            trace
        )

        response_engine.register_response(
            trace=trace_accept,

            response_type=(
                DecisionResponseType.ACCEPT
            ),

            rationale=(
                "Integrated final test."
            ),

            farmer_knowledge=(
                case.farmer_knowledge
            ),
        )

        print(
            "FINAL ACTION AFTER ACCEPT:",
            trace_accept
            .get_final_action()
        )

    else:

        print(
            "FINAL ACTION AFTER ACCEPT:",
            None
        )

        print(
            "RESPONSE SKIPPED: "
            "NO OPERATIONAL RECOMMENDATION"
        )


    print(
        "-" * 160
    )


print(
    "TOTAL CONDITIONS:",
    len(conditions),
)