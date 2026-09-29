from sqlalchemy.orm import Session

from database.models.identity import (
    ParcelMembershipModel,
)


class ParcelMembershipRepository:

    def __init__(
        self,
        session: Session,
    ):

        self.session = session


    def create(
        self,
        *,
        membership_id: str,
        parcel_id: str,
        user_id: str,
        role: str,
        created_at,
        metadata: dict | None = None,
    ) -> ParcelMembershipModel:

        model = (
            ParcelMembershipModel(
                id=membership_id,
                parcel_id=parcel_id,
                user_id=user_id,
                role=role,
                created_at=created_at,
                metadata_json=(
                    metadata
                    or {}
                ),
            )
        )


        self.session.add(
            model
        )

        self.session.flush()

        return model


    def get_for_user_and_parcel(
        self,
        *,
        user_id: str,
        parcel_id: str,
    ) -> (
        ParcelMembershipModel
        | None
    ):

        return (
            self.session
            .query(
                ParcelMembershipModel
            )
            .filter(
                ParcelMembershipModel
                .user_id
                == user_id,

                ParcelMembershipModel
                .parcel_id
                == parcel_id,
            )
            .one_or_none()
        )


    def list_by_user(
        self,
        user_id: str,
    ) -> list[
        ParcelMembershipModel
    ]:

        return (
            self.session
            .query(
                ParcelMembershipModel
            )
            .filter(
                ParcelMembershipModel
                .user_id
                == user_id
            )
            .all()
        )


    def list_by_parcel(
        self,
        parcel_id: str,
    ) -> list[
        ParcelMembershipModel
    ]:

        return (
            self.session
            .query(
                ParcelMembershipModel
            )
            .filter(
                ParcelMembershipModel
                .parcel_id
                == parcel_id
            )
            .all()
        )


    def update_role(
        self,
        model: ParcelMembershipModel,
        *,
        role: str,
    ) -> ParcelMembershipModel:

        model.role = role

        self.session.flush()

        return model


    def delete(
        self,
        model: ParcelMembershipModel,
    ) -> None:

        self.session.delete(
            model
        )

        self.session.flush()
