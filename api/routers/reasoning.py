from fastapi import (
    APIRouter,
    HTTPException,
)

from api.schemas.reasoning import (
    ReasoningRunRequest,
    ReasoningRunResponse,
    TrustedVariableRead,
    RankedRecommendationRead,
    ConflictRead,
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

from twin.experiment import (
    ExperimentCondition,
)


router = APIRouter(
    prefix="/reasoning",
    tags=["reasoning"],
)


factory = (
    ExperimentalCaseFactory()
)

orchestrator = (
    ReasoningOrchestrator()
)

trace_engine = (
    DecisionTraceEngine()
)


@router.post(
    "/run",
    response_model=(
        ReasoningRunResponse
    ),
)
def run_reasoning(
    payload: ReasoningRunRequest,
):

    # =====================================================
    # 1. CONDITION
    # =====================================================

    try:

        condition = (
            ExperimentCondition(
                payload.condition
            )
        )

    except ValueError:

        allowed = [
            item.value
            for item
            in ExperimentCondition
        ]

        raise HTTPException(
            status_code=422,
            detail={
                "message":
                    "Invalid condition.",

                "allowed":
                    allowed,
            },
        )


    # =====================================================
    # 2. BUILD CASE
    # =====================================================

    case = factory.build(
        condition
    )


    # =====================================================
    # 3. RUN COMPLETE REASONING ENGINE
    # =====================================================

    reasoning = (
        orchestrator.run(
            scenarios=case.scenarios,

            evidence=case.evidence,

            farmer_knowledge=(
                case.farmer_knowledge
            ),
        )
    )


    # =====================================================
    # 4. DECISION TRACE
    # =====================================================

    trace = (
        trace_engine.build_trace(
            reasoning_result=reasoning,

            evidence=case.evidence,

            farmer_knowledge=(
                case.farmer_knowledge
            ),

            parcel_id=(
                "API-DEMO-PARCEL"
            ),
        )
    )


    # =====================================================
    # 5. TRUSTED STATE
    # =====================================================

    trusted_variables = []


    for variable, item in (
        reasoning
        .trusted_state
        .variables
        .items()
    ):

        trusted_variables.append(
            TrustedVariableRead(
                variable=variable,

                value=item.value,

                unit=item.unit,

                confidence_score=(
                    item.confidence
                    .confidence_score
                ),

                uncertainty_level=(
                    item.confidence
                    .uncertainty_level
                    .value
                ),

                requires_update=(
                    item.confidence
                    .requires_update
                ),

                selected_evidence_id=(
                    item.metadata.get(
                        "selected_evidence_id"
                    )
                ),
            )
        )


    # =====================================================
    # 6. CONFLICTS
    # =====================================================

    conflicts = []


    for conflict in (
        reasoning.conflicts
    ):

        conflicts.append(
            ConflictRead(
                conflict_id=(
                    conflict.conflict_id
                ),

                conflict_type=(
                    conflict
                    .conflict_type
                    .value
                ),

                status=(
                    conflict
                    .status
                    .value
                ),

                left_item_id=(
                    conflict.left_item_id
                ),

                right_item_id=(
                    conflict.right_item_id
                ),
            )
        )


    # =====================================================
    # 7. RECOMMENDATION
    # =====================================================

    recommendation = (
        reasoning
        .recommendation_result
    )

    recommended_irrigation = None


    if (
        recommendation
        .recommended_scenario
        is not None
    ):

        recommended_irrigation = (
            recommendation
            .recommended_scenario
            .irrigation_mm
        )


    ranking = []


    for rank, item in enumerate(
        recommendation
        .ranked_scenarios,
        start=1,
    ):

        ranking.append(
            RankedRecommendationRead(
                rank=rank,

                irrigation_mm=(
                    item.scenario
                    .irrigation_mm
                ),

                final_score=(
                    item.final_score
                ),

                agronomic_component=(
                    item
                    .agronomic_component
                ),

                marginal_component=(
                    item
                    .marginal_component
                ),

                preference_component=(
                    item
                    .preference_component
                ),

                confidence_factor=(
                    item
                    .confidence_factor
                ),
            )
        )


    # =====================================================
    # 8. RISK
    # =====================================================

    risk = (
        reasoning.decision_risk
    )


    # =====================================================
    # 9. RESPONSE
    # =====================================================

    return ReasoningRunResponse(
        condition=(
            condition.value
        ),

        quality_gate_status=(
            reasoning
            .quality_gate
            .status
            .value
        ),

        recommendation_allowed=(
            reasoning
            .recommendation_allowed
        ),

        recommendation_status=(
            recommendation
            .status
            .value
        ),

        recommended_irrigation_mm=(
            recommended_irrigation
        ),

        decision_risk=(
            risk
            .risk_level
            .value
        ),

        decision_confidence=(
            risk
            .decision_confidence
        ),

        requires_human_confirmation=(
            risk
            .requires_human_confirmation
        ),

        operational_evidence_ids=(
            reasoning
            .operational_evidence_ids
        ),

        excluded_evidence_ids=(
            reasoning
            .excluded_evidence_ids
        ),

        update_required_variables=(
            reasoning
            .update_required_variables
        ),

        trusted_state=(
            trusted_variables
        ),

        conflicts=conflicts,

        ranking=ranking,

        provisional_recommendation=(
            trace
            .provisional_recommendation
        ),
    )