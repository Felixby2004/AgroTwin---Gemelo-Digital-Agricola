from sqlalchemy.orm import Session

from database.models.evidence import (
    MachineEvidenceModel,
)


class EvidenceRepository:

    def __init__(
        self,
        session: Session,
    ):

        self.session = session


    def create(
        self,
        *,
        evidence_id: str,
        parcel_id: str | None,
        variable: str,
        value,
        unit: str | None,
        observed_at,
        status: str,
        quality_score: float | None,
        uncertainty,
        provenance: dict,
        metadata: dict | None = None,
    ) -> MachineEvidenceModel:

        # JSON column: scalar values are wrapped
        # to maintain a consistent JSON object.
        stored_value = (
            value
            if isinstance(
                value,
                dict,
            )
            else {
                "value": value
            }
        )

        item = MachineEvidenceModel(
            id=evidence_id,
            parcel_id=parcel_id,
            variable=variable,
            value=stored_value,
            unit=unit,
            observed_at=observed_at,
            status=status,
            quality_score=quality_score,
            uncertainty=uncertainty,
            provenance=provenance,
            metadata_json=metadata,
        )

        self.session.add(
            item
        )

        self.session.flush()

        return item


    def get_by_id(
        self,
        evidence_id: str,
    ) -> MachineEvidenceModel | None:

        return self.session.get(
            MachineEvidenceModel,
            evidence_id,
        )


    def list_by_parcel(
        self,
        parcel_id: str,
    ) -> list[
        MachineEvidenceModel
    ]:

        return (
            self.session
            .query(
                MachineEvidenceModel
            )
            .filter(
                MachineEvidenceModel
                .parcel_id
                == parcel_id
            )
            .order_by(
                MachineEvidenceModel
                .observed_at
                .desc()
            )
            .all()
        )