from datetime import (
    datetime,
    timezone,
)

from uuid import uuid4


from database.repositories.data_audit_repository import (
    DataAuditRepository,
)


class DataAuditService:

    def log(
        self,
        *,
        db,
        parcel_id: str | None,
        actor_id: str,
        action: str,
        allowed: bool,
        consent_id: str | None = None,
        purpose: str | None = None,
        data_category: str | None = None,
        details: dict | None = None,
    ):

        repo = DataAuditRepository(
            db
        )


        return repo.create(
            audit_id=(
                "AUDIT-"
                + uuid4()
                .hex[:12]
                .upper()
            ),

            parcel_id=parcel_id,

            actor_id=actor_id,

            action=action,

            allowed=allowed,

            consent_id=consent_id,

            purpose=purpose,

            data_category=data_category,

            created_at=(
                datetime.now(
                    timezone.utc
                )
            ),

            details=(
                details
                or {}
            ),
        )