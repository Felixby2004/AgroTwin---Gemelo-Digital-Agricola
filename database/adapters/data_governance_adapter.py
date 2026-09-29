from twin.data_governance import (
    DataConsent,
    DataPurpose,
    DataPermission,
    ConsentStatus,
)

from database.models.data_governance import (
    DataConsentModel,
)


class DataGovernanceAdapter:

    @staticmethod
    def to_model_dict(
        consent: DataConsent,
    ) -> dict:

        return {
            "consent_id":
                consent.consent_id,

            "parcel_id":
                consent.parcel_id,

            "subject_id":
                consent.subject_id,

            "purposes": [
                item.value
                for item
                in consent.purposes
            ],

            "permissions": [
                item.value
                for item
                in consent.permissions
            ],

            "allowed_data_categories":
                consent
                .allowed_data_categories,

            "created_at":
                consent.created_at,

            "valid_until":
                consent.valid_until,

            "status":
                consent.status.value,

            "metadata":
                consent.metadata,
        }


    @staticmethod
    def from_model(
        model: DataConsentModel,
    ) -> DataConsent:

        return DataConsent(
            consent_id=model.id,

            parcel_id=model.parcel_id,

            subject_id=model.subject_id,

            purposes=[
                DataPurpose(
                    item
                )
                for item
                in model.purposes
            ],

            permissions=[
                DataPermission(
                    item
                )
                for item
                in model.permissions
            ],

            allowed_data_categories=(
                model
                .allowed_data_categories
                or []
            ),

            created_at=model.created_at,

            valid_until=model.valid_until,

            status=(
                ConsentStatus(
                    model.status
                )
            ),

            metadata=(
                model.metadata_json
                or {}
            ),
        )