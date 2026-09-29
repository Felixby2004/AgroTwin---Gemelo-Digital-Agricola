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


from api.auth_dependencies import (
    get_current_user,
)

from api.dependencies import (
    get_db,
)

from api.schemas.auth import (
    UserRead,
)

from api.schemas.users import (
    UserAdminCreateRequest,
    UserAdminUpdateRequest,
    UserProfileUpdateRequest,
)

from database.models.identity import (
    UserModel,
)

from database.repositories.user_repository import (
    UserRepository,
)

from services.password_service import (
    PasswordService,
)

from twin.identity import (
    SystemRole,
    UserStatus,
)


router = APIRouter(
    prefix="/users",
    tags=[
        "users",
    ],
)


password_service = (
    PasswordService()
)


def _user_to_schema(
    user: UserModel,
) -> UserRead:

    return UserRead(
        user_id=user.id,
        email=user.email,
        full_name=user.full_name,
        system_role=user.system_role,
        status=user.status,
        created_at=user.created_at,
        metadata=(
            user.metadata_json
            or {}
        ),
    )


def _require_admin(
    current_user: UserModel,
) -> None:

    if (
        current_user.system_role
        != SystemRole.ADMIN.value
    ):

        raise HTTPException(
            status_code=403,
            detail=(
                "Administrator role required."
            ),
        )


@router.get(
    "/me/profile",
    response_model=UserRead,
)
def get_my_profile(
    current_user: UserModel = Depends(
        get_current_user
    ),
):

    return _user_to_schema(
        current_user
    )


@router.put(
    "/me/profile",
    response_model=UserRead,
)
def update_my_profile(
    payload: UserProfileUpdateRequest,
    db: Session = Depends(
        get_db
    ),
    current_user: UserModel = Depends(
        get_current_user
    ),
):

    repo = UserRepository(
        db
    )

    repo.update_profile(
        current_user,
        full_name=(
            payload.full_name
        ),
        metadata=(
            payload.metadata
        ),
    )

    db.commit()

    db.refresh(
        current_user
    )

    return _user_to_schema(
        current_user
    )


@router.get(
    "",
    response_model=list[
        UserRead
    ],
)
def list_users(
    db: Session = Depends(
        get_db
    ),
    current_user: UserModel = Depends(
        get_current_user
    ),
):

    _require_admin(
        current_user
    )

    repo = UserRepository(
        db
    )

    return [
        _user_to_schema(
            user
        )
        for user
        in repo.list_all()
    ]


@router.post(
    "",
    response_model=UserRead,
)
def create_user(
    payload: UserAdminCreateRequest,
    db: Session = Depends(
        get_db
    ),
    current_user: UserModel = Depends(
        get_current_user
    ),
):

    _require_admin(
        current_user
    )

    repo = UserRepository(
        db
    )

    email = (
        payload.email
        .strip()
        .lower()
    )

    if "@" not in email:

        raise HTTPException(
            status_code=422,
            detail=(
                "Invalid email address."
            ),
        )

    if (
        repo.get_by_email(
            email
        )
        is not None
    ):

        raise HTTPException(
            status_code=409,
            detail=(
                "Email is already registered."
            ),
        )

    try:

        password_hash = (
            password_service
            .hash_password(
                payload.password
            )
        )

        user = repo.create(
            user_id=(
                "USER-"
                + uuid4()
                .hex[:12]
                .upper()
            ),
            email=email,
            full_name=(
                payload.full_name
                .strip()
            ),
            password_hash=(
                password_hash
            ),
            system_role=(
                payload.system_role
            ),
            status=(
                UserStatus.ACTIVE.value
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

        db.commit()

        db.refresh(
            user
        )

    except IntegrityError:

        db.rollback()

        raise HTTPException(
            status_code=409,
            detail=(
                "Email is already registered."
            ),
        )

    except Exception:

        db.rollback()

        raise

    return _user_to_schema(
        user
    )


@router.put(
    "/{user_id}",
    response_model=UserRead,
)
def update_user(
    user_id: str,
    payload: UserAdminUpdateRequest,
    db: Session = Depends(
        get_db
    ),
    current_user: UserModel = Depends(
        get_current_user
    ),
):

    _require_admin(
        current_user
    )

    repo = UserRepository(
        db
    )

    user = repo.get_by_id(
        user_id
    )

    if user is None:

        raise HTTPException(
            status_code=404,
            detail=(
                "User not found."
            ),
        )

    if (
        user.id
        == current_user.id
        and payload.status
        == UserStatus.DISABLED.value
    ):

        raise HTTPException(
            status_code=422,
            detail=(
                "An administrator cannot disable "
                "their own active session."
            ),
        )

    if (
        user.id
        == current_user.id
        and payload.system_role
        is not None
        and payload.system_role
        != SystemRole.ADMIN.value
    ):

        raise HTTPException(
            status_code=422,
            detail=(
                "An administrator cannot remove "
                "their own ADMIN role."
            ),
        )

    repo.update_admin_fields(
        user,
        full_name=(
            payload.full_name
        ),
        system_role=(
            payload.system_role
        ),
        status=(
            payload.status
        ),
        metadata=(
            payload.metadata
        ),
    )

    db.commit()

    db.refresh(
        user
    )

    return _user_to_schema(
        user
    )
