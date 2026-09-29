from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from sqlalchemy.orm import Session


from api.dependencies import (
    get_db,
)

from api.schemas.parcel_state import (
    ParcelSummaryRead,
    EvidenceSummaryRead,
    KnowledgeSummaryRead,
    TrustedStateItemRead,
    CurrentRecommendationRead,
    CurrentRiskRead,
    LatestTraceRead,
    ParcelOperationalStateRead,
)


from database.repositories.parcel_repository import (
    ParcelRepository,
)

from database.repositories.evidence_repository import (
    EvidenceRepository,
)

from database.repositories.farmer_knowledge_repository import (
    FarmerKnowledgeRepository,
)

from database.repositories.decision_trace_repository import (
    DecisionTraceRepository,
)


from database.adapters import (
    EvidenceAdapter,
    FarmerKnowledgeAdapter,
    DecisionTraceAdapter,
)


from engines.reasoning_orchestrator import (
    ReasoningOrchestrator,
)


from experiments.case_factory import (
    ExperimentalCaseFactory,
)

from twin.experiment import (
    ExperimentCondition,
)


router = APIRouter(
    prefix="/parcels",
    tags=["parcel-state"],
)


orchestrator = (
    ReasoningOrchestrator()
)

scenario_factory = (
    ExperimentalCaseFactory()
)


@router.get(
    "/{parcel_id}/state",
    response_model=(
        ParcelOperationalStateRead
    ),
)
def get_parcel_operational_state(
    parcel_id: str,
    db: Session = Depends(
        get_db
    ),
):

    # =====================================================
    # 1. PARCEL
    # =====================================================

    parcel_repo = (
        ParcelRepository(
            db
        )
    )

    parcel = (
        parcel_repo.get_by_id(
            parcel_id
        )
    )

    if parcel is None:

        raise HTTPException(
            status_code=404,
            detail="Parcel not found.",
        )


    # =====================================================
    # 2. MACHINE EVIDENCE
    # =====================================================

    evidence_repo = (
        EvidenceRepository(
            db
        )
    )

    evidence_models = (
        evidence_repo.list_by_parcel(
            parcel_id
        )
    )

    evidence = [
        EvidenceAdapter.from_model(
            item
        )
        for item in evidence_models
    ]


    # =====================================================
    # 3. FARMER KNOWLEDGE
    # =====================================================

    knowledge_repo = (
        FarmerKnowledgeRepository(
            db
        )
    )

    knowledge_models = (
        knowledge_repo.list_by_parcel(
            parcel_id
        )
    )

    farmer_knowledge = [
        FarmerKnowledgeAdapter
        .from_model(
            item
        )
        for item in knowledge_models
    ]


    # =====================================================
    # 4. SCENARIOS
    #
    # Sigue siendo temporal hasta conectar
    # el generador biofísico por parcela.
    # =====================================================

    scenario_case = (
        scenario_factory.build(
            ExperimentCondition.COMPLETE
        )
    )

    scenarios = (
        scenario_case.scenarios
    )


    # =====================================================
    # 5. CURRENT REASONING STATE
    #
    # No persiste trace.
    # Es una lectura/reconstrucción del estado actual.
    # =====================================================

    reasoning = (
        orchestrator.run(
            scenarios=scenarios,

            evidence=evidence,

            farmer_knowledge=(
                farmer_knowledge
            ),
        )
    )


    # =====================================================
    # 6. TRUSTED TWIN STATE
    # =====================================================

    trusted_state = []

    for variable, item in (
        reasoning
        .trusted_state
        .variables
        .items()
    ):

        trusted_state.append(
            TrustedStateItemRead(
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
    # 7. FARMER KNOWLEDGE SUMMARY
    # =====================================================

    knowledge_counts = {
        "CONSTRAINT": 0,
        "PREFERENCE": 0,
        "OBSERVATION": 0,
        "EVENT": 0,
        "LOCAL_KNOWLEDGE": 0,
    }

    for item in farmer_knowledge:

        knowledge_type = (
            item.knowledge_type.value
        )

        if (
            knowledge_type
            in knowledge_counts
        ):
            knowledge_counts[
                knowledge_type
            ] += 1


    # =====================================================
    # 8. CONFLICTS
    # =====================================================

    conflicts = []

    for conflict in (
        reasoning.conflicts
    ):

        conflicts.append(
            {
                "conflict_id":
                    conflict.conflict_id,

                "conflict_type":
                    conflict
                    .conflict_type
                    .value,

                "status":
                    conflict.status.value,

                "left_item_id":
                    conflict.left_item_id,

                "right_item_id":
                    conflict.right_item_id,
            }
        )


    # =====================================================
    # 9. CURRENT RECOMMENDATION
    # =====================================================

    recommendation = (
        reasoning
        .recommendation_result
    )

    recommended_irrigation = None

    recommendation_score = None

    recommendation_reasons = []


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


    if (
        recommendation
        .ranked_scenarios
    ):

        top = (
            recommendation
            .ranked_scenarios[0]
        )

        recommendation_score = (
            top.final_score
        )

        recommendation_reasons = (
            top.reasons
        )


    # =====================================================
    # 10. RISK
    # =====================================================

    risk = (
        reasoning.decision_risk
    )


    # =====================================================
    # 11. LATEST DECISION TRACE
    # =====================================================

    trace_repo = (
        DecisionTraceRepository(
            db
        )
    )

    trace_models = (
        trace_repo.list_by_parcel(
            parcel_id
        )
    )

    latest_trace = None


    if trace_models:

        latest_model = (
            trace_models[0]
        )

        latest_data = (
            DecisionTraceAdapter
            .from_model(
                latest_model
            )
        )

        latest_trace = (
            LatestTraceRead(
                trace_id=(
                    latest_data[
                        "trace_id"
                    ]
                ),

                created_at=(
                    latest_data[
                        "created_at"
                    ].isoformat()
                    if latest_data[
                        "created_at"
                    ]
                    is not None
                    else None
                ),

                provisional_recommendation=(
                    latest_data.get(
                        "provisional_recommendation"
                    )
                ),

                farmer_response=(
                    latest_data.get(
                        "farmer_response"
                    )
                ),

                final_action=(
                    latest_data.get(
                        "final_action"
                    )
                ),
            )
        )

    else:

        latest_trace = (
            LatestTraceRead(
                trace_id=None,
                created_at=None,
                provisional_recommendation=None,
                farmer_response=None,
                final_action=None,
            )
        )


    # =====================================================
    # 12. RESPONSE
    # =====================================================

    return ParcelOperationalStateRead(

        parcel=ParcelSummaryRead(
            id=parcel.id,
            name=parcel.name,
            crop_type=parcel.crop_type,
            area_ha=parcel.area_ha,
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


        evidence=(
            EvidenceSummaryRead(
                total=len(
                    evidence
                ),

                operational=len(
                    reasoning
                    .operational_evidence_ids
                ),

                excluded=len(
                    reasoning
                    .excluded_evidence_ids
                ),

                update_required=(
                    reasoning
                    .update_required_variables
                ),
            )
        ),


        farmer_knowledge=(
            KnowledgeSummaryRead(
                total=len(
                    farmer_knowledge
                ),

                constraints=(
                    knowledge_counts[
                        "CONSTRAINT"
                    ]
                ),

                preferences=(
                    knowledge_counts[
                        "PREFERENCE"
                    ]
                ),

                observations=(
                    knowledge_counts[
                        "OBSERVATION"
                    ]
                ),

                events=(
                    knowledge_counts[
                        "EVENT"
                    ]
                ),

                local_knowledge=(
                    knowledge_counts[
                        "LOCAL_KNOWLEDGE"
                    ]
                ),
            )
        ),


        trusted_state=(
            trusted_state
        ),


        conflicts_count=len(
            conflicts
        ),


        conflicts=conflicts,


        recommendation=(
            CurrentRecommendationRead(
                status=(
                    recommendation
                    .status
                    .value
                ),

                allowed=(
                    reasoning
                    .recommendation_allowed
                ),

                irrigation_mm=(
                    recommended_irrigation
                ),

                score=(
                    recommendation_score
                ),

                reasons=(
                    recommendation_reasons
                ),
            )
        ),


        risk=(
            CurrentRiskRead(
                level=(
                    risk
                    .risk_level
                    .value
                ),

                confidence=(
                    risk
                    .decision_confidence
                ),

                requires_human_confirmation=(
                    risk
                    .requires_human_confirmation
                ),

                reasons=(
                    risk.reasons
                ),
            )
        ),


        latest_trace=(
            latest_trace
        ),
    )