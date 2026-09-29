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

from database.repositories.decision_trace_repository import (
    DecisionTraceRepository,
)

from database.adapters.decision_trace_adapter import (
    DecisionTraceAdapter,
)

from engines.farmer_response_engine import (
    FarmerResponseEngine,
)

from twin.identity import (
    ParcelPermission,
)

from api.schemas.decision_trace import (
    DecisionTraceRead,
    FarmerDecisionResponseCreate,
)

from database.repositories.farmer_knowledge_repository import (
    FarmerKnowledgeRepository,
)

from database.adapters.farmer_knowledge_adapter import (
    FarmerKnowledgeAdapter,
)

from twin.decision_trace import (
    DecisionResponseType,
)

router = APIRouter(
    tags=[
        "decision-traces",
    ],
)

# =========================================================
# GET TRACE
# =========================================================

@router.get(
    "/decision-traces/{trace_id}",
)
def get_decision_trace(
    trace_id: str,
    current_user: UserModel = Depends(
        get_current_user
    ),
    db: Session = Depends(
        get_db
    ),
):

    repo = (
        DecisionTraceRepository(
            db
        )
    )


    model = (
        repo.get_by_id(
            trace_id
        )
    )


    if model is None:

        raise HTTPException(
            status_code=404,
            detail=(
                "Decision trace not found."
            ),
        )


    # =====================================================
    # AUTHORIZATION
    # =====================================================

    check_parcel_permission(
        db=db,
        current_user=current_user,
        parcel_id=model.parcel_id,
        permission=(
            ParcelPermission.VIEW
        ),
    )


    return (
        DecisionTraceAdapter
        .from_model(
            model
        )
    )


# =========================================================
# LIST TRACES BY PARCEL
# =========================================================

@router.get(
    "/parcels/{parcel_id}/decision-traces",
)
def list_decision_traces(
    parcel_id: str,
    current_user: UserModel = Depends(
        get_current_user
    ),
    db: Session = Depends(
        get_db
    ),
):

    # =====================================================
    # AUTHORIZATION
    # =====================================================

    check_parcel_permission(
        db=db,
        current_user=current_user,
        parcel_id=parcel_id,
        permission=(
            ParcelPermission.VIEW
        ),
    )


    repo = (
        DecisionTraceRepository(
            db
        )
    )


    models = (
        repo.list_by_parcel(
            parcel_id
        )
    )


    return [
        DecisionTraceAdapter
        .from_model(
            model
        )

        for model in models
    ]


# =========================================================
# REGISTER FARMER RESPONSE
# =========================================================

@router.post(
    "/decision-traces/{trace_id}/response",
    response_model=DecisionTraceRead,
)
def register_farmer_response(
    trace_id: str,

    payload:
        FarmerDecisionResponseCreate,

    current_user:
        UserModel = Depends(
            get_current_user
        ),

    db:
        Session = Depends(
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


    model = (
        trace_repo
        .get_by_id(
            trace_id
        )
    )


    if model is None:

        raise HTTPException(
            status_code=404,
            detail=(
                "Decision trace "
                "not found."
            ),
        )


    if model.parcel_id is None:

        raise HTTPException(
            status_code=422,
            detail=(
                "Decision trace "
                "has no parcel."
            ),
        )


    # =====================================================
    # 2. AUTHORIZATION
    # =====================================================

    check_parcel_permission(
        db=db,

        current_user=
            current_user,

        parcel_id=
            model.parcel_id,

        permission=(
            ParcelPermission
            .MANAGE_KNOWLEDGE
        ),
    )


    # =====================================================
    # 3. PREVENT DOUBLE RESPONSE
    # =====================================================

    if (
        model.farmer_response
        is not None
    ):

        raise HTTPException(
            status_code=409,
            detail=(
                "This decision trace "
                "already has a farmer "
                "response."
            ),
        )


    # =====================================================
    # 4. DATABASE -> DOMAIN TRACE
    # =====================================================

    trace = (
        DecisionTraceAdapter
        .to_domain(
            model
        )
    )


    # =====================================================
    # 5. LOAD FARMER KNOWLEDGE
    # =====================================================

    knowledge_repo = (
        FarmerKnowledgeRepository(
            db
        )
    )


    knowledge_models = (
        knowledge_repo
        .list_by_parcel(
            model.parcel_id
        )
    )


    farmer_knowledge = [
        FarmerKnowledgeAdapter
        .from_model(
            knowledge_model
        )

        for knowledge_model
        in knowledge_models
    ]


    # =====================================================
    # 6. REGISTER RESPONSE
    # =====================================================

    response_engine = (
        FarmerResponseEngine()
    )


    try:

        updated_trace = (
            response_engine
            .register_response(
                trace=trace,

                response_type=(
                    DecisionResponseType(
                        payload
                        .response_type
                    )
                ),

                modified_action=(
                    payload
                    .modified_action
                ),

                rationale=(
                    payload
                    .rationale
                ),

                farmer_knowledge=(
                    farmer_knowledge
                ),
            )
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=422,
            detail=str(
                exc
            ),
        ) from exc


    # =====================================================
    # 7. FINAL ACTION
    # =====================================================

    final_action = (
        updated_trace
        .get_final_action()
    )


    # =====================================================
    # 8. PERSIST RESPONSE
    # =====================================================

    try:

        trace_repo.update_from_trace(
            model=model,

            trace=(
                updated_trace
            ),

            final_action=(
                final_action
            ),
        )


        db.commit()


        db.refresh(
            model
        )


    except Exception:

        db.rollback()

        raise


    # =====================================================
    # 9. RESPONSE
    # =====================================================

    return (
        DecisionTraceAdapter
        .from_model(
            model
        )
    )