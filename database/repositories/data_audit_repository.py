from sqlalchemy.orm import Session

from database.models.data_audit import (
    DataAuditEventModel,
)


class DataAuditRepository:

    def __init__(
        self,
        session: Session,
    ):

        self.session = session


    def create(
        self,
        *,
        audit_id: str,
        parcel_id: str | None,
        actor_id: str,
        action: str,
        allowed: bool,
        consent_id: str | None,
        purpose: str | None,
        data_category: str | None,
        created_at,
        details: dict | None = None,
    ) -> DataAuditEventModel:

        item = DataAuditEventModel(
            id=audit_id,
            parcel_id=parcel_id,
            actor_id=actor_id,
            action=action,
            allowed=allowed,
            consent_id=consent_id,
            purpose=purpose,
            data_category=data_category,
            created_at=created_at,
            details=details,
        )

        self.session.add(
            item
        )

        self.session.flush()

        return item


    def list_by_parcel(
        self,
        parcel_id: str,
    ) -> list[
        DataAuditEventModel
    ]:

        return (
            self.session
            .query(
                DataAuditEventModel
            )
            .filter(
                DataAuditEventModel
                .parcel_id
                == parcel_id
            )
            .order_by(
                DataAuditEventModel
                .created_at
                .desc()
            )
            .all()
        )