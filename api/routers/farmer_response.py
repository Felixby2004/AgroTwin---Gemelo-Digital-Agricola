from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from sqlalchemy.orm import Session


from api.dependencies import (
    get_db,
)

from api.schemas.farmer_response import (
    FarmerResponseRequest,
    FarmerResponseResult,
)


from database.repositories.decision_trace_repository import (
    DecisionTraceRepository,
)

from database.repositories.farmer_knowledge_repository import (
    FarmerKnowledgeRepository,
)

from database.adapters.decision_trace_adapter import (
    DecisionTraceAdapter,
)

from database.adapters.farmer_knowledge_adapter import (
    FarmerKnowledgeAdapter,
)


from engines.farmer_response_engine import (
    FarmerResponseEngine,
)


from twin.decision_trace import (
    DecisionResponseType,
)


router = APIRouter(
    prefix="/decision-traces",
    tags=[
        "decision-traces",
        "human-in-the-loop",
    ],
)


response_engine = (
    FarmerResponseEngine()
)


@router.post(
    "/{trace_id}/response",
    response_model=(
        FarmerResponseResult
    ),
)
def register_farmer_response(
    trace_id: str,
    payload: FarmerResponseRequest,
    db: Session = Depends(
        get_db
    ),
):

    # =====================================================
    # 1. LOAD TRACE
    # =====================================================

    trace_repo = (
        DecisionTraceRepository(
            db
        )
    )

    trace_model = (
        trace_repo.get_by_id(
            trace_id
        )
    )

    if trace_model is None:

        raise HTTPException(
            status_code=404,
            detail=(
                "Decision trace not found."
            ),
        )


    # =====================================================
    # 2. RECONSTRUCT DOMAIN TRACE
    # =====================================================

    trace = (
        DecisionTraceAdapter
        .to_domain(
            trace_model
        )
    )


    # =====================================================
    # 3. LOAD FARMER KNOWLEDGE
    #
    # Required because MODIFY must respect
    # confirmed HARD constraints.
    # =====================================================

    farmer_knowledge = []

    if trace_model.parcel_id:

        knowledge_repo = (
            FarmerKnowledgeRepository(
                db
            )
        )

        knowledge_models = (
            knowledge_repo
            .list_by_parcel(
                trace_model.parcel_id
            )
        )

        farmer_knowledge = [
            FarmerKnowledgeAdapter
            .from_model(
                item
            )
            for item
            in knowledge_models
        ]


    # =====================================================
    # 4. RESPONSE TYPE
    # =====================================================

    try:

        response_type = (
            DecisionResponseType(
                payload.response_type
            )
        )

    except ValueError:

        raise HTTPException(
            status_code=422,
            detail=(
                "Invalid response type."
            ),
        )


    # =====================================================
    # 5. REGISTER THROUGH DOMAIN ENGINE
    # =====================================================

    try:

        updated_trace = (
            response_engine
            .register_response(
                trace=trace,

                response_type=(
                    response_type
                ),

                modified_action=(
                    payload.modified_action
                ),

                rationale=(
                    payload.rationale
                ),

                farmer_knowledge=(
                    farmer_knowledge
                ),
            )
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=422,
            detail=str(exc),
        )


    # =====================================================
    # 6. DETERMINE FINAL ACTION
    # =====================================================

    if (
        response_type
        == DecisionResponseType.ACCEPT
    ):

        provisional = (
            updated_trace
            .provisional_recommendation
            or {}
        )

        irrigation_mm = (
            provisional.get(
                "irrigation_mm"
            )
        )

        final_action = (
            {
                "irrigation_mm":
                    irrigation_mm
            }
            if irrigation_mm
            is not None
            else None
        )


    elif (
        response_type
        == DecisionResponseType.MODIFY
    ):

        final_action = (
            payload.modified_action
        )


    elif (
        response_type
        == DecisionResponseType.REJECT
    ):

        final_action = None


    else:

        final_action = None


    # =====================================================
    # 7. PERSIST VALID RESPONSE
    # =====================================================

    trace_repo.update_from_trace(
        model=trace_model,
        trace=updated_trace,
        final_action=final_action,
    )

    db.commit()

    db.refresh(
        trace_model
    )


    # =====================================================
    # 8. RESPONSE
    # =====================================================

    return FarmerResponseResult(
        trace_id=(
            updated_trace.trace_id
        ),

        response_type=(
            payload.response_type
        ),

        accepted=True,

        modified_action=(
            payload.modified_action
        ),

        final_action=(
            final_action
        ),

        rationale=(
            payload.rationale
        ),

        provisional_recommendation=(
            updated_trace
            .provisional_recommendation
        ),

        message=(
            "Farmer response "
            "registered successfully."
        ),
    )