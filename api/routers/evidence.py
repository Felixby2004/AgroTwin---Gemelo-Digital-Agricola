from fastapi import (
    APIRouter,
    Depends,
)

from sqlalchemy.orm import Session

from api.dependencies import (
    get_db,
)

from api.schemas.evidence import (
    MachineEvidenceCreate,
)

from database.repositories.evidence_repository import (
    EvidenceRepository,
)


router = APIRouter(
    prefix="/evidence",
    tags=["evidence"],
)


@router.post("")
def create_evidence(
    payload: MachineEvidenceCreate,
    db: Session = Depends(
        get_db
    ),
):

    repo = EvidenceRepository(
        db
    )

    item = repo.create(
        evidence_id=(
            payload.evidence_id
        ),

        parcel_id=(
            payload.parcel_id
        ),

        variable=(
            payload.variable
        ),

        value=(
            payload.value
        ),

        unit=(
            payload.unit
        ),

        observed_at=(
            payload.observed_at
        ),

        status=(
            payload.status
        ),

        quality_score=(
            payload.quality_score
        ),

        uncertainty=(
            payload.uncertainty
        ),

        provenance=(
            payload.provenance
            .model_dump(
                mode="json"
            )
        ),

        metadata=(
            payload.metadata
        ),
    )

    db.commit()

    return {
        "id": item.id,
        "variable": item.variable,
        "status": item.status,
    }