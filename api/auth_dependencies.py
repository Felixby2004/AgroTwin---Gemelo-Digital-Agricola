from fastapi import (
    Depends,
    HTTPException,
    status,
)

from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
)

from sqlalchemy.orm import Session


from api.dependencies import (
    get_db,
)

from database.models.identity import (
    UserModel,
)

from database.repositories.user_repository import (
    UserRepository,
)

from database.repositories.parcel_membership_repository import (
    ParcelMembershipRepository,
)

from engines.authorization_engine import (
    AuthorizationEngine,
)

from services.token_service import (
    TokenService,
)

from twin.identity import (
    SystemRole,
    UserStatus,
    ParcelRole,
    ParcelPermission,
)


bearer_scheme = HTTPBearer(
    auto_error=False,
)

token_service = TokenService()

authorization_engine = (
    AuthorizationEngine()
)


def get_current_user(
    credentials: HTTPAuthorizationCredentials
    | None = Depends(
        bearer_scheme
    ),
    db: Session = Depends(
        get_db
    ),
) -> UserModel:

    if credentials is None:

        raise HTTPException(
            status_code=(
                status.HTTP_401_UNAUTHORIZED
            ),
            detail=(
                "Authentication required."
            ),
            headers={
                "WWW-Authenticate":
                    "Bearer"
            },
        )


    token = credentials.credentials


    try:

        payload = (
            token_service
            .decode_access_token(
                token
            )
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=(
                status.HTTP_401_UNAUTHORIZED
            ),
            detail=str(
                exc
            ),
            headers={
                "WWW-Authenticate":
                    "Bearer"
            },
        )


    user_id = payload.get(
        "sub"
    )


    repo = UserRepository(
        db
    )

    user = repo.get_by_id(
        user_id
    )


    if user is None:

        raise HTTPException(
            status_code=(
                status.HTTP_401_UNAUTHORIZED
            ),
            detail=(
                "User no longer exists."
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


    return user


def require_admin(
    current_user: UserModel = Depends(
        get_current_user
    ),
) -> UserModel:

    if (
        current_user.system_role
        != SystemRole.ADMIN.value
    ):

        raise HTTPException(
            status_code=403,
            detail=(
                "Administrator privileges "
                "are required."
            ),
        )


    return current_user


def check_parcel_permission(
    *,
    db: Session,
    current_user: UserModel,
    parcel_id: str,
    permission: ParcelPermission,
) -> None:

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

                parcel_role = (
                    ParcelRole(
                        membership.role
                    )
                )

            except ValueError:

                parcel_role = None


    allowed = (
        authorization_engine
        .has_parcel_permission(
            system_role=system_role,
            parcel_role=parcel_role,
            permission=permission,
        )
    )


    if not allowed:

        raise HTTPException(
            status_code=403,
            detail=(
                "You do not have "
                f"{permission.value} "
                "permission for this parcel."
            ),
        )