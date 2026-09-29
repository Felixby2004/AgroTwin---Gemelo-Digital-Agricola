from datetime import (
    datetime,
    timezone,
)

from uuid import uuid4

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from sqlalchemy.exc import (
    IntegrityError,
)

from sqlalchemy.orm import Session


from api.dependencies import (
    get_db,
)

from api.auth_dependencies import (
    get_current_user,
    check_parcel_permission,
)

from api.schemas.membership import (
    ParcelMembershipCreate,
    ParcelMembershipRead,
    ParcelClaimResult,
    ParcelPermissionsRead,
    ParcelMembershipUpdate,
)


from database.models.identity import (
    UserModel,
)

from database.repositories.parcel_repository import (
    ParcelRepository,
)

from database.repositories.user_repository import (
    UserRepository,
)

from database.repositories.parcel_membership_repository import (
    ParcelMembershipRepository,
)


from twin.identity import (
    SystemRole,
    ParcelRole,
    ParcelPermission,
)

from engines.authorization_engine import (
    AuthorizationEngine,
)


router = APIRouter(
    tags=[
        "parcel-memberships",
    ],
)


authorization_engine = (
    AuthorizationEngine()
)


def _membership_to_schema(
    model,
) -> ParcelMembershipRead:

    return ParcelMembershipRead(
        membership_id=model.id,
        parcel_id=model.parcel_id,
        user_id=model.user_id,
        role=model.role,
        created_at=model.created_at,
        metadata=(
            model.metadata_json
            or {}
        ),
    )


# =========================================================
# CLAIM LEGACY / UNOWNED PARCEL
# =========================================================

@router.post(
    "/parcels/{parcel_id}/claim",
    response_model=ParcelClaimResult,
)
def claim_parcel(
    parcel_id: str,
    current_user: UserModel = Depends(
        get_current_user
    ),
    db: Session = Depends(
        get_db
    ),
):

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
            detail=(
                "Parcel not found."
            ),
        )


    membership_repo = (
        ParcelMembershipRepository(
            db
        )
    )


    existing_members = (
        membership_repo
        .list_by_parcel(
            parcel_id
        )
    )


    if existing_members:

        raise HTTPException(
            status_code=409,
            detail=(
                "Parcel already has "
                "registered members."
            ),
        )


    try:

        membership_repo.create(
            membership_id=(
                "MEM-"
                + uuid4()
                .hex[:12]
                .upper()
            ),

            parcel_id=parcel_id,

            user_id=(
                current_user.id
            ),

            role=(
                ParcelRole.OWNER.value
            ),

            created_at=(
                datetime.now(
                    timezone.utc
                )
            ),

            metadata={
                "source":
                    "LEGACY_PARCEL_CLAIM"
            },
        )


        db.commit()


    except IntegrityError:

        db.rollback()

        raise HTTPException(
            status_code=409,
            detail=(
                "Parcel could not "
                "be claimed."
            ),
        )


    except Exception:

        db.rollback()

        raise


    return ParcelClaimResult(
        parcel_id=parcel_id,
        user_id=current_user.id,
        role=(
            ParcelRole.OWNER.value
        ),
        message=(
            "Parcel ownership "
            "successfully claimed."
        ),
    )




# =========================================================
# CURRENT USER PERMISSIONS FOR PARCEL
# =========================================================

@router.get(
    "/parcels/{parcel_id}/my-permissions",
    response_model=ParcelPermissionsRead,
)
def get_my_parcel_permissions(
    parcel_id: str,
    current_user: UserModel = Depends(
        get_current_user
    ),
    db: Session = Depends(
        get_db
    ),
):

    parcel_repo = (
        ParcelRepository(
            db
        )
    )

    if (
        parcel_repo.get_by_id(
            parcel_id
        )
        is None
    ):

        raise HTTPException(
            status_code=404,
            detail=(
                "Parcel not found."
            ),
        )


    try:

        system_role = SystemRole(
            current_user.system_role
        )

    except ValueError:

        raise HTTPException(
            status_code=403,
            detail=(
                "Invalid system role."
            ),
        )


    parcel_role = None


    if (
        system_role
        != SystemRole.ADMIN
    ):

        membership_repo = (
            ParcelMembershipRepository(
                db
            )
        )

        membership = (
            membership_repo
            .get_for_user_and_parcel(
                user_id=(
                    current_user.id
                ),
                parcel_id=(
                    parcel_id
                ),
            )
        )


        if membership is not None:

            try:

                parcel_role = ParcelRole(
                    membership.role
                )

            except ValueError:

                parcel_role = None


    permissions = (
        authorization_engine
        .get_parcel_permissions(
            system_role=system_role,
            parcel_role=parcel_role,
        )
    )


    permission_order = {
        item: index
        for index, item
        in enumerate(
            ParcelPermission
        )
    }


    return ParcelPermissionsRead(
        parcel_id=parcel_id,
        user_id=current_user.id,
        system_role=(
            system_role.value
        ),
        parcel_role=(
            parcel_role.value
            if parcel_role
            is not None
            else None
        ),
        permissions=[
            item.value
            for item
            in sorted(
                permissions,
                key=lambda item:
                    permission_order[item],
            )
        ],
    )


# =========================================================
# ADD MEMBER
# =========================================================

@router.post(
    "/parcels/{parcel_id}/members",
    response_model=(
        ParcelMembershipRead
    ),
)
def add_parcel_member(
    parcel_id: str,
    payload: ParcelMembershipCreate,
    current_user: UserModel = Depends(
        get_current_user
    ),
    db: Session = Depends(
        get_db
    ),
):

    # -----------------------------------------------------
    # Authorization
    # -----------------------------------------------------

    check_parcel_permission(
        db=db,
        current_user=(
            current_user
        ),
        parcel_id=parcel_id,
        permission=(
            ParcelPermission
            .MANAGE_MEMBERS
        ),
    )


    # -----------------------------------------------------
    # Parcel
    # -----------------------------------------------------

    parcel_repo = (
        ParcelRepository(
            db
        )
    )

    if (
        parcel_repo.get_by_id(
            parcel_id
        )
        is None
    ):

        raise HTTPException(
            status_code=404,
            detail=(
                "Parcel not found."
            ),
        )


    # -----------------------------------------------------
    # User
    # -----------------------------------------------------

    user_repo = (
        UserRepository(
            db
        )
    )

    target_user = (
        user_repo.get_by_id(
            payload.user_id
        )
    )


    if target_user is None:

        raise HTTPException(
            status_code=404,
            detail=(
                "User not found."
            ),
        )


    # -----------------------------------------------------
    # Role
    # -----------------------------------------------------

    try:

        role = ParcelRole(
            payload.role
        )

    except ValueError:

        raise HTTPException(
            status_code=422,
            detail=(
                "role must be OWNER, "
                "FARMER, AGRONOMIST "
                "or VIEWER."
            ),
        )


    membership_repo = (
        ParcelMembershipRepository(
            db
        )
    )


    existing = (
        membership_repo
        .get_for_user_and_parcel(
            user_id=(
                payload.user_id
            ),
            parcel_id=(
                parcel_id
            ),
        )
    )


    if existing is not None:

        raise HTTPException(
            status_code=409,
            detail=(
                "User is already "
                "a member of this parcel."
            ),
        )


    try:

        membership = (
            membership_repo.create(
                membership_id=(
                    "MEM-"
                    + uuid4()
                    .hex[:12]
                    .upper()
                ),

                parcel_id=parcel_id,

                user_id=(
                    payload.user_id
                ),

                role=(
                    role.value
                ),

                created_at=(
                    datetime.now(
                        timezone.utc
                    )
                ),

                metadata=(
                    payload.metadata
                ),
            )
        )


        db.commit()

        db.refresh(
            membership
        )


    except IntegrityError:

        db.rollback()

        raise HTTPException(
            status_code=409,
            detail=(
                "Membership already exists."
            ),
        )


    except Exception:

        db.rollback()

        raise


    return (
        _membership_to_schema(
            membership
        )
    )


# =========================================================
# LIST PARCEL MEMBERS
# =========================================================

@router.get(
    "/parcels/{parcel_id}/members",
    response_model=list[
        ParcelMembershipRead
    ],
)
def list_parcel_members(
    parcel_id: str,
    current_user: UserModel = Depends(
        get_current_user
    ),
    db: Session = Depends(
        get_db
    ),
):

    check_parcel_permission(
        db=db,
        current_user=current_user,
        parcel_id=parcel_id,
        permission=(
            ParcelPermission.VIEW
        ),
    )


    repo = (
        ParcelMembershipRepository(
            db
        )
    )

    models = (
        repo.list_by_parcel(
            parcel_id
        )
    )


    return [
        _membership_to_schema(
            item
        )
        for item
        in models
    ]


# =========================================================
# UPDATE MEMBER ROLE
# =========================================================

@router.put(
    "/parcels/{parcel_id}/members/{user_id}",
    response_model=ParcelMembershipRead,
)
def update_parcel_member_role(
    parcel_id: str,
    user_id: str,
    payload: ParcelMembershipUpdate,
    current_user: UserModel = Depends(
        get_current_user
    ),
    db: Session = Depends(
        get_db
    ),
):

    check_parcel_permission(
        db=db,
        current_user=current_user,
        parcel_id=parcel_id,
        permission=(
            ParcelPermission
            .MANAGE_MEMBERS
        ),
    )


    try:

        role = ParcelRole(
            payload.role
        )

    except ValueError:

        raise HTTPException(
            status_code=422,
            detail=(
                "role must be OWNER, "
                "FARMER, AGRONOMIST "
                "or VIEWER."
            ),
        )


    repo = ParcelMembershipRepository(
        db
    )

    membership = (
        repo.get_for_user_and_parcel(
            user_id=user_id,
            parcel_id=parcel_id,
        )
    )


    if membership is None:

        raise HTTPException(
            status_code=404,
            detail=(
                "Parcel membership "
                "not found."
            ),
        )


    # Avoid accidentally removing the last owner.
    if (
        membership.role
        == ParcelRole.OWNER.value
        and role
        != ParcelRole.OWNER
    ):

        owners = [
            item
            for item
            in repo.list_by_parcel(
                parcel_id
            )
            if item.role
            == ParcelRole.OWNER.value
        ]

        if len(owners) <= 1:

            raise HTTPException(
                status_code=422,
                detail=(
                    "The last OWNER "
                    "cannot be changed "
                    "to another role."
                ),
            )


    repo.update_role(
        membership,
        role=role.value,
    )

    db.commit()

    db.refresh(
        membership
    )

    return _membership_to_schema(
        membership
    )


# =========================================================
# REMOVE MEMBER
# =========================================================

@router.delete(
    "/parcels/{parcel_id}/members/{user_id}",
    status_code=204,
)
def remove_parcel_member(
    parcel_id: str,
    user_id: str,
    current_user: UserModel = Depends(
        get_current_user
    ),
    db: Session = Depends(
        get_db
    ),
):

    check_parcel_permission(
        db=db,
        current_user=current_user,
        parcel_id=parcel_id,
        permission=(
            ParcelPermission
            .MANAGE_MEMBERS
        ),
    )


    repo = ParcelMembershipRepository(
        db
    )

    membership = (
        repo.get_for_user_and_parcel(
            user_id=user_id,
            parcel_id=parcel_id,
        )
    )


    if membership is None:

        raise HTTPException(
            status_code=404,
            detail=(
                "Parcel membership "
                "not found."
            ),
        )


    if (
        membership.role
        == ParcelRole.OWNER.value
    ):

        owners = [
            item
            for item
            in repo.list_by_parcel(
                parcel_id
            )
            if item.role
            == ParcelRole.OWNER.value
        ]

        if len(owners) <= 1:

            raise HTTPException(
                status_code=422,
                detail=(
                    "The last OWNER "
                    "cannot be removed."
                ),
            )


    repo.delete(
        membership
    )

    db.commit()

    return None
