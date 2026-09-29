from twin.farmer_knowledge import (
    FarmerKnowledgeItem,
    FarmerKnowledgeType,
    KnowledgeValidationStatus,
    ConstraintType,
)

from database.models.farmer_knowledge import (
    FarmerKnowledgeModel,
)

from api.schemas.farmer_knowledge import (
    FarmerKnowledgeCreate,
    FarmerKnowledgeRead,
)


class FarmerKnowledgeAdapter:

    @staticmethod
    def to_model_dict(
        item: FarmerKnowledgeItem,
        parcel_id: str | None = None,
    ) -> dict:

        return {
            "knowledge_id":
                item.knowledge_id,

            "parcel_id":
                parcel_id,

            "knowledge_type":
                item.knowledge_type.value,

            "source_id":
                item.source_id,

            "source_role":
                item.source_role,

            "payload":
                item.payload,

            "created_at":
                item.created_at,

            "valid_from":
                item.valid_from,

            "valid_until":
                item.valid_until,

            "reported_confidence":
                item.reported_confidence,

            "validation_status":
                item.validation_status.value,

            "constraint_type":
                (
                    item.constraint_type.value
                    if item.constraint_type
                    is not None
                    else None
                ),

            "affects":
                item.affects,

            "rationale":
                item.rationale,

            "metadata":
                item.metadata,
        }


    @staticmethod
    def from_create_schema(
        payload: FarmerKnowledgeCreate,
    ) -> FarmerKnowledgeItem:

        try:

            knowledge_type = (
                FarmerKnowledgeType(
                    payload.knowledge_type
                )
            )

        except ValueError as exc:

            raise ValueError(
                "Invalid knowledge_type."
            ) from exc


        try:

            validation_status = (
                KnowledgeValidationStatus(
                    payload.validation_status
                )
            )

        except ValueError as exc:

            raise ValueError(
                "Invalid validation_status."
            ) from exc


        constraint_type = None

        if (
            payload.constraint_type
            is not None
        ):

            try:

                constraint_type = (
                    ConstraintType(
                        payload.constraint_type
                    )
                )

            except ValueError as exc:

                raise ValueError(
                    "Invalid constraint_type."
                ) from exc


        return FarmerKnowledgeItem(
            knowledge_id=(
                payload.knowledge_id
            ),

            knowledge_type=(
                knowledge_type
            ),

            source_id=(
                payload.source_id
            ),

            source_role=(
                payload.source_role
            ),

            payload=(
                payload.payload
            ),

            created_at=(
                payload.created_at
            ),

            valid_from=(
                payload.valid_from
            ),

            valid_until=(
                payload.valid_until
            ),

            spatial_scope=(
                payload.spatial_scope
            ),

            reported_confidence=(
                payload.reported_confidence
            ),

            validation_status=(
                validation_status
            ),

            affects=(
                payload.affects
                or []
            ),

            constraint_type=(
                constraint_type
            ),

            rationale=(
                payload.rationale
            ),

            metadata=(
                payload.metadata
                or {}
            ),
        )


    @staticmethod
    def from_model(
        model: FarmerKnowledgeModel,
    ) -> FarmerKnowledgeItem:

        return FarmerKnowledgeItem(
            knowledge_id=model.id,

            knowledge_type=(
                FarmerKnowledgeType(
                    model.knowledge_type
                )
            ),

            source_id=model.source_id,

            source_role=model.source_role,

            payload=model.payload,

            created_at=model.created_at,

            valid_from=model.valid_from,

            valid_until=model.valid_until,

            spatial_scope=None,

            reported_confidence=(
                model.reported_confidence
            ),

            validation_status=(
                KnowledgeValidationStatus(
                    model.validation_status
                )
            ),

            affects=(
                model.affects
                or []
            ),

            constraint_type=(
                ConstraintType(
                    model.constraint_type
                )
                if model.constraint_type
                is not None
                else None
            ),

            rationale=model.rationale,

            metadata=(
                model.metadata_json
                or {}
            ),
        )


    @staticmethod
    def to_read_schema(
        model: FarmerKnowledgeModel,
    ) -> FarmerKnowledgeRead:

        return FarmerKnowledgeRead(
            knowledge_id=(
                model.id
            ),

            parcel_id=(
                model.parcel_id
            ),

            knowledge_type=(
                model.knowledge_type
            ),

            source_id=(
                model.source_id
            ),

            source_role=(
                model.source_role
            ),

            payload=(
                model.payload
            ),

            created_at=(
                model.created_at
            ),

            valid_from=(
                model.valid_from
            ),

            valid_until=(
                model.valid_until
            ),

            spatial_scope=None,

            reported_confidence=(
                model.reported_confidence
            ),

            validation_status=(
                model.validation_status
            ),

            affects=(
                model.affects
                or []
            ),

            constraint_type=(
                model.constraint_type
            ),

            rationale=(
                model.rationale
            ),

            metadata=(
                model.metadata_json
                or {}
            ),
        )
