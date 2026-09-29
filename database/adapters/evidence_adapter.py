from twin.evidence import (
    MachineEvidence,
    EvidenceStatus,
)

from twin.provenance import (
    ProvenanceRecord,
    EvidenceSourceType,
)

from database.models.evidence import (
    MachineEvidenceModel,
)


class EvidenceAdapter:

    @staticmethod
    def to_model_dict(
        evidence: MachineEvidence,
        parcel_id: str | None = None,
    ) -> dict:

        provenance = {
            "source_type":
                evidence.provenance
                .source_type
                .value,

            "source_name":
                evidence.provenance
                .source_name,

            "source_id":
                evidence.provenance
                .source_id,

            "source_version":
                evidence.provenance
                .source_version,

            "generated_at":
                (
                    evidence.provenance
                    .generated_at
                    .isoformat()
                    if evidence.provenance
                    .generated_at
                    is not None
                    else None
                ),

            "valid_at":
                (
                    evidence.provenance
                    .valid_at
                    .isoformat()
                    if evidence.provenance
                    .valid_at
                    is not None
                    else None
                ),

            "spatial_scope":
                evidence.provenance
                .spatial_scope,

            "transformation":
                evidence.provenance
                .transformation,

            "parent_ids":
                evidence.provenance
                .parent_ids,

            "metadata":
                evidence.provenance
                .metadata,
        }

        return {
            "evidence_id":
                evidence.evidence_id,

            "parcel_id":
                parcel_id,

            "variable":
                evidence.variable,

            "value":
                evidence.value,

            "unit":
                evidence.unit,

            "observed_at":
                evidence.observed_at,

            "status":
                evidence.status.value,

            "quality_score":
                evidence.quality_score,

            "uncertainty":
                evidence.uncertainty,

            "provenance":
                provenance,

            "metadata":
                evidence.metadata,
        }


    @staticmethod
    def from_model(
        model: MachineEvidenceModel,
    ) -> MachineEvidence:

        provenance_data = (
            model.provenance
            or {}
        )

        provenance = ProvenanceRecord(
            source_type=(
                EvidenceSourceType(
                    provenance_data[
                        "source_type"
                    ]
                )
            ),

            source_name=(
                provenance_data.get(
                    "source_name"
                )
            ),

            source_id=(
                provenance_data.get(
                    "source_id"
                )
            ),

            source_version=(
                provenance_data.get(
                    "source_version"
                )
            ),

            generated_at=None,

            valid_at=None,

            spatial_scope=(
                provenance_data.get(
                    "spatial_scope"
                )
            ),

            transformation=(
                provenance_data.get(
                    "transformation"
                )
            ),

            parent_ids=(
                provenance_data.get(
                    "parent_ids",
                    [],
                )
            ),

            metadata=(
                provenance_data.get(
                    "metadata",
                    {},
                )
            ),
        )

        stored_value = model.value

        if (
            isinstance(
                stored_value,
                dict,
            )
            and
            set(
                stored_value.keys()
            )
            == {"value"}
        ):
            value = (
                stored_value[
                    "value"
                ]
            )

        else:
            value = stored_value

        return MachineEvidence(
            evidence_id=model.id,

            variable=model.variable,

            value=value,

            unit=model.unit,

            observed_at=(
                model.observed_at
            ),

            provenance=provenance,

            status=(
                EvidenceStatus(
                    model.status
                )
            ),

            quality_score=(
                model.quality_score
            ),

            uncertainty=(
                model.uncertainty
            ),

            metadata=(
                model.metadata_json
                or {}
            ),
        )