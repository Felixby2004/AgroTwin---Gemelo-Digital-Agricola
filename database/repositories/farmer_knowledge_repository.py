from sqlalchemy.orm import Session

from database.models.farmer_knowledge import (
    FarmerKnowledgeModel,
)


class FarmerKnowledgeRepository:

    def __init__(
        self,
        session: Session,
    ):

        self.session = session


    def create(
        self,
        *,
        knowledge_id: str,
        parcel_id: str | None,
        knowledge_type: str,
        source_id: str,
        source_role: str,
        payload: dict,
        created_at,
        valid_from,
        valid_until,
        reported_confidence,
        validation_status: str,
        constraint_type: str | None,
        affects: list | None,
        rationale: str | None,
        metadata: dict | None = None,
    ) -> FarmerKnowledgeModel:

        item = FarmerKnowledgeModel(
            id=knowledge_id,
            parcel_id=parcel_id,
            knowledge_type=knowledge_type,
            source_id=source_id,
            source_role=source_role,
            payload=payload,
            created_at=created_at,
            valid_from=valid_from,
            valid_until=valid_until,
            reported_confidence=(
                reported_confidence
            ),
            validation_status=(
                validation_status
            ),
            constraint_type=(
                constraint_type
            ),
            affects=affects,
            rationale=rationale,
            metadata_json=metadata,
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
        FarmerKnowledgeModel
    ]:

        return (
            self.session
            .query(
                FarmerKnowledgeModel
            )
            .filter(
                FarmerKnowledgeModel
                .parcel_id
                == parcel_id
            )
            .order_by(
                FarmerKnowledgeModel
                .created_at
                .desc()
            )
            .all()
        )