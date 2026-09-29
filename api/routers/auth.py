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
)

from api.schemas.auth import (
    UserRegisterRequest,
    UserLoginRequest,
    UserRead,
    TokenResponse,
)


from config.settings import (
    settings,
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

from services.token_service import (
    TokenService,
)


from twin.identity import (
    SystemRole,
    UserStatus,
)


router = APIRouter(
    prefix="/auth",
    tags=[
        "authentication",
    ],
)


password_service = (
    PasswordService()
)

token_service = (
    TokenService()
)


def _user_to_schema(
    user: UserModel,
) -> UserRead:

    return UserRead(
        user_id=user.id,
        email=user.email,
        full_name=user.full_name,
        system_role=(
            user.system_role
        ),
        status=user.status,
        created_at=user.created_at,
        metadata=(
            user.metadata_json
            or {}
        ),
    )


@router.post(
    "/register",
    response_model=UserRead,
)
def register(
    payload: UserRegisterRequest,
    db: Session = Depends(
        get_db
    ),
):

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


    repo = UserRepository(
        db
    )


    existing = (
        repo.get_by_email(
            email
        )
    )


    if existing is not None:

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

    except ValueError as exc:

        raise HTTPException(
            status_code=422,
            detail=str(
                exc
            ),
        )


    try:

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
                SystemRole.USER.value
            ),

            status=(
                UserStatus.ACTIVE.value
            ),

            created_at=(
                datetime.now(
                    timezone.utc
                )
            ),

            metadata={},
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


    return (
        _user_to_schema(
            user
        )
    )


@router.post(
    "/login",
    response_model=TokenResponse,
)
def login(
    payload: UserLoginRequest,
    db: Session = Depends(
        get_db
    ),
):

    email = (
        payload.email
        .strip()
        .lower()
    )


    repo = UserRepository(
        db
    )

    user = (
        repo.get_by_email(
            email
        )
    )


    if user is None:

        raise HTTPException(
            status_code=401,
            detail=(
                "Invalid email or password."
            ),
        )


    valid_password = (
        password_service
        .verify_password(
            payload.password,
            user.password_hash,
        )
    )


    if not valid_password:

        raise HTTPException(
            status_code=401,
            detail=(
                "Invalid email or password."
            ),
        )


    if (
        user.status
        != UserStatus.ACTIVE.value
    ):

        raise HTTPException(
            status_code=403,
            detail=(
                "User account is disabled."
            ),
        )


    access_token = (
        token_service
        .create_access_token(
            user_id=user.id,
            email=user.email,
            system_role=(
                user.system_role
            ),
        )
    )


    return TokenResponse(
        access_token=(
            access_token
        ),

        token_type="bearer",

        expires_in_minutes=(
            settings
            .jwt_access_token_minutes
        ),

        user=(
            _user_to_schema(
                user
            )
        ),
    )


@router.get(
    "/me",
    response_model=UserRead,
)
def me(
    current_user: UserModel = Depends(
        get_current_user
    ),
):

    return (
        _user_to_schema(
            current_user
        )
    )