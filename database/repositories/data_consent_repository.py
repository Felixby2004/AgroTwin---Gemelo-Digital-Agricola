from sqlalchemy.orm import (
    Session,
)

from database.models.data_governance import (
    DataConsentModel,
)


class DataConsentRepository:

    def __init__(
        self,
        session: Session,
    ):

        self.session = session


    def create(
        self,
        *,
        consent_id: str,
        parcel_id: str,
        subject_id: str,
        purposes: list,
        permissions: list,
        allowed_data_categories: list,
        created_at,
        valid_until,
        status: str,
        metadata: dict | None = None,
    ) -> DataConsentModel:

        item = DataConsentModel(
            id=consent_id,

            parcel_id=parcel_id,

            subject_id=subject_id,

            purposes=purposes,

            permissions=permissions,

            allowed_data_categories=(
                allowed_data_categories
            ),

            created_at=created_at,

            valid_until=valid_until,

            status=status,

            metadata_json=metadata,
        )


        self.session.add(
            item
        )

        self.session.flush()

        return item


    def get_by_id(
        self,
        consent_id: str,
    ) -> DataConsentModel | None:

        return self.session.get(
            DataConsentModel,
            consent_id,
        )


    def list_by_parcel(
        self,
        parcel_id: str,
    ) -> list[
        DataConsentModel
    ]:

        return (
            self.session
            .query(
                DataConsentModel
            )
            .filter(
                DataConsentModel
                .parcel_id
                == parcel_id
            )
            .order_by(
                DataConsentModel
                .created_at
                .desc()
            )
            .all()
        )


    def update_status(
        self,
        consent_id: str,
        status: str,
    ) -> DataConsentModel | None:

        item = self.get_by_id(
            consent_id
        )

        if item is None:
            return None


        item.status = status

        self.session.flush()

        return item