from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from sqlalchemy.orm import Session

from api.dependencies import (
    get_db,
)

from api.auth_dependencies import (
    get_current_user,
    check_parcel_permission,
)

from database.models.identity import (
    UserModel,
)

from twin.identity import (
    ParcelPermission,
)

from api.schemas.reasoning import (
    ReasoningRunResponse,
    TrustedVariableRead,
    RankedRecommendationRead,
    ConflictRead,
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

from engines.reasoning_orchestrator import (
    ReasoningOrchestrator,
)

from engines.decision_trace_engine import (
    DecisionTraceEngine,
)

from experiments.case_factory import (
    ExperimentalCaseFactory,
)

from twin.experiment import (
    ExperimentCondition,
)

from database.repositories.decision_trace_repository import (
    DecisionTraceRepository,
)

from database.adapters import (
    EvidenceAdapter,
    FarmerKnowledgeAdapter,
    DecisionTraceAdapter,
)


router = APIRouter(
    prefix="/parcels",
    tags=["reasoning"],
)


orchestrator = ReasoningOrchestrator()

trace_engine = DecisionTraceEngine()

scenario_factory = (
    ExperimentalCaseFactory()
)


@router.post(
    "/{parcel_id}/reasoning",
    response_model=ReasoningRunResponse,
)
def run_parcel_reasoning(
    parcel_id: str,
    current_user: UserModel = Depends(
        get_current_user
    ),
    db: Session = Depends(
        get_db
    ),
):

    # =====================================================
    # 1. PARCEL
    # =====================================================

    parcel_repo = ParcelRepository(
        db
    )

    parcel = parcel_repo.get_by_id(
        parcel_id
    )

    if parcel is None:

        raise HTTPException(
            status_code=404,
            detail="Parcel not found.",
        )


    # =====================================================
    # 1B. AUTHORIZATION
    # =====================================================

    check_parcel_permission(
        db=db,
        current_user=current_user,
        parcel_id=parcel_id,
        permission=(
            ParcelPermission
            .RUN_REASONING
        ),
    )


    # =====================================================
    # 2. EVIDENCE FROM DATABASE
    # =====================================================

    evidence_repo = EvidenceRepository(
        db
    )

    evidence_models = (
        evidence_repo.list_by_parcel(
            parcel_id
        )
    )

    if not evidence_models:

        raise HTTPException(
            status_code=422,
            detail=(
                "Parcel has no machine evidence."
            ),
        )


    evidence = [
        EvidenceAdapter.from_model(
            item
        )
        for item in evidence_models
    ]


    # =====================================================
    # 3. FARMER KNOWLEDGE FROM DATABASE
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
    # Temporalmente reutilizamos nuestros escenarios
    # biofísicos validados.
    # Más adelante vendrán del motor biofísico real
    # asociado a la parcela.
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
    # 5. REASONING
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
    # 6. DECISION TRACE
    # =====================================================

    trace = trace_engine.build_trace(
        reasoning_result=reasoning,
        evidence=evidence,
        farmer_knowledge=(
            farmer_knowledge
        ),
        parcel_id=parcel_id,
    )


    # =====================================================
    # 6B. PERSIST DECISION TRACE
    # =====================================================

    trace_repo = DecisionTraceRepository(
        db
    )

    trace_data = (
        DecisionTraceAdapter
        .to_model_dict(
            trace
        )
    )

    trace_repo.create(
        **trace_data
    )

    db.commit()


    # =====================================================
    # 7. TRUSTED STATE
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
    # 8. CONFLICTS
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
                    conflict.status.value
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
    # 9. RECOMMENDATION
    # =====================================================

    recommendation = (
        reasoning.recommendation_result
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
        recommendation.ranked_scenarios,
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
                    item.agronomic_component
                ),

                marginal_component=(
                    item.marginal_component
                ),

                preference_component=(
                    item.preference_component
                ),

                confidence_factor=(
                    item.confidence_factor
                ),
            )
        )


    # =====================================================
    # 10. RESPONSE
    # =====================================================

    risk = reasoning.decision_risk


    return ReasoningRunResponse(
        condition="PERSISTED_PARCEL",

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
            risk.risk_level.value
        ),

        decision_confidence=(
            risk.decision_confidence
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