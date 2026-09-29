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

from database.repositories.parcel_repository import (
    ParcelRepository,
)

from database.repositories.farmer_knowledge_repository import (
    FarmerKnowledgeRepository,
)

from database.adapters.farmer_knowledge_adapter import (
    FarmerKnowledgeAdapter,
)

from api.schemas.farmer_knowledge import (
    FarmerKnowledgeCreate,
    FarmerKnowledgeRead,
)

from twin.identity import (
    ParcelPermission,
)


router = APIRouter(
    tags=[
        "farmer-knowledge",
    ],
)


@router.post(
    "/farmer-knowledge",
    response_model=FarmerKnowledgeRead,
)
def create_farmer_knowledge(
    payload: FarmerKnowledgeCreate,
    current_user: UserModel = Depends(
        get_current_user
    ),
    db: Session = Depends(
        get_db
    ),
):

    # =====================================================
    # 1. VALIDATE PARCEL
    # =====================================================

    parcel_repo = ParcelRepository(
        db
    )

    parcel = parcel_repo.get_by_id(
        payload.parcel_id
    )

    if parcel is None:

        raise HTTPException(
            status_code=404,
            detail="Parcel not found.",
        )


    # =====================================================
    # 2. AUTHORIZATION
    # =====================================================

    check_parcel_permission(
        db=db,
        current_user=current_user,
        parcel_id=payload.parcel_id,
        permission=(
            ParcelPermission
            .MANAGE_KNOWLEDGE
        ),
    )


    # =====================================================
    # 3. DOMAIN OBJECT
    # =====================================================

    try:

        knowledge = (
            FarmerKnowledgeAdapter
            .from_create_schema(
                payload
            )
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=422,
            detail=str(
                exc
            ),
        )


    # =====================================================
    # 4. PERSIST
    # =====================================================

    repo = FarmerKnowledgeRepository(
        db
    )

    model_data = (
        FarmerKnowledgeAdapter
        .to_model_dict(
            knowledge,
            parcel_id=(
                payload.parcel_id
            ),
        )
    )

    try:

        model = repo.create(
            **model_data
        )

        db.commit()

        db.refresh(
            model
        )

    except Exception:

        db.rollback()

        raise


    # =====================================================
    # 5. RESPONSE
    # =====================================================

    return (
        FarmerKnowledgeAdapter
        .to_read_schema(
            model
        )
    )
