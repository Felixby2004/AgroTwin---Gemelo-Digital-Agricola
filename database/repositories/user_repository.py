from sqlalchemy.orm import Session

from database.models.identity import (
    UserModel,
)


class UserRepository:

    def __init__(
        self,
        session: Session,
    ):

        self.session = session


    def create(
        self,
        *,
        user_id: str,
        email: str,
        full_name: str,
        password_hash: str,
        system_role: str,
        status: str,
        created_at,
        metadata: dict | None = None,
    ) -> UserModel:

        model = UserModel(
            id=user_id,
            email=email,
            full_name=full_name,
            password_hash=password_hash,
            system_role=system_role,
            status=status,
            created_at=created_at,
            metadata_json=(
                metadata
                or {}
            ),
        )

        self.session.add(
            model
        )

        self.session.flush()

        return model


    def get_by_id(
        self,
        user_id: str,
    ) -> UserModel | None:

        return self.session.get(
            UserModel,
            user_id,
        )


    def get_by_email(
        self,
        email: str,
    ) -> UserModel | None:

        return (
            self.session
            .query(
                UserModel
            )
            .filter(
                UserModel.email
                == email.lower()
            )
            .one_or_none()
        )


    def list_all(
        self,
    ) -> list[
        UserModel
    ]:

        return (
            self.session
            .query(
                UserModel
            )
            .order_by(
                UserModel.created_at
                .desc()
            )
            .all()
        )


    def update_profile(
        self,
        user: UserModel,
        *,
        full_name: str | None = None,
        metadata: dict | None = None,
    ) -> UserModel:

        if full_name is not None:
            user.full_name = (
                full_name
                .strip()
            )

        if metadata is not None:
            current = dict(
                user.metadata_json
                or {}
            )

            current.update(
                metadata
            )

            user.metadata_json = (
                current
            )

        self.session.flush()

        return user


    def update_admin_fields(
        self,
        user: UserModel,
        *,
        full_name: str | None = None,
        system_role: str | None = None,
        status: str | None = None,
        metadata: dict | None = None,
    ) -> UserModel:

        if full_name is not None:
            user.full_name = (
                full_name
                .strip()
            )

        if system_role is not None:
            user.system_role = (
                system_role
            )

        if status is not None:
            user.status = status

        if metadata is not None:
            current = dict(
                user.metadata_json
                or {}
            )

            current.update(
                metadata
            )

            user.metadata_json = (
                current
            )

        self.session.flush()

        return user
