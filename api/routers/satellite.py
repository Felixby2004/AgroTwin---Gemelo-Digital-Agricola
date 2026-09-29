from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from sqlalchemy.orm import Session


from api.dependencies import (
    get_db,
)

from api.schemas.satellite import (
    Sentinel2ObservationCreate,
    Sentinel2ObservationResult,
    VegetationIndexRead,
)


from database.repositories.parcel_repository import (
    ParcelRepository,
)

from database.repositories.evidence_repository import (
    EvidenceRepository,
)


from services.sentinel2_service import (
    Sentinel2Service,
)


router = APIRouter(
    prefix="/satellite",
    tags=["satellite"],
)


sentinel_service = (
    Sentinel2Service()
)


@router.post(
    "/sentinel-2",
    response_model=(
        Sentinel2ObservationResult
    ),
)
def ingest_sentinel_2(
    payload: Sentinel2ObservationCreate,
    db: Session = Depends(
        get_db
    ),
):

    # =====================================================
    # 1. PARCEL
    # =====================================================

    parcel_repo = (
        ParcelRepository(
            db
        )
    )

    parcel = (
        parcel_repo.get_by_id(
            payload.parcel_id
        )
    )

    if parcel is None:

        raise HTTPException(
            status_code=404,
            detail="Parcel not found.",
        )


    # =====================================================
    # 2. CALCULATE INDICES
    # =====================================================

    try:

        evidence_items = (
            sentinel_service
            .build_evidence(
                parcel_id=(
                    payload.parcel_id
                ),

                scene_id=(
                    payload.scene_id
                ),

                acquired_at=(
                    payload.acquired_at
                ),

                red=(
                    payload.b04_red
                ),

                nir=(
                    payload.b08_nir
                ),

                swir=(
                    payload.b11_swir
                ),

                cloud_cover_pct=(
                    payload.cloud_cover_pct
                ),

                source_url=(
                    payload.source_url
                ),

                processing_level=(
                    payload.processing_level
                ),

                metadata=(
                    payload.metadata
                ),
            )
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=422,
            detail=str(
                exc
            ),
        )


    # =====================================================
    # 3. PERSIST
    # =====================================================

    repo = EvidenceRepository(
        db
    )

    persisted = []


    try:

        for data in evidence_items:

            item = repo.create(
                evidence_id=(
                    data[
                        "evidence_id"
                    ]
                ),

                parcel_id=(
                    data[
                        "parcel_id"
                    ]
                ),

                variable=(
                    data[
                        "variable"
                    ]
                ),

                value=(
                    data[
                        "value"
                    ]
                ),

                unit=(
                    data[
                        "unit"
                    ]
                ),

                observed_at=(
                    data[
                        "observed_at"
                    ]
                ),

                status=(
                    data[
                        "status"
                    ]
                ),

                quality_score=(
                    data[
                        "quality_score"
                    ]
                ),

                uncertainty=(
                    data[
                        "uncertainty"
                    ]
                ),

                provenance=(
                    data[
                        "provenance"
                    ]
                ),

                metadata={
                    **data["metadata"],
                    "data_origin": "MANUAL_TEST",
                },
            )

            persisted.append(
                item
            )


        db.commit()


    except Exception:

        db.rollback()

        raise


    # =====================================================
    # 4. RESPONSE
    # =====================================================

    by_variable = {
        item.variable: item
        for item in persisted
    }


    return Sentinel2ObservationResult(

        parcel_id=(
            payload.parcel_id
        ),

        scene_id=(
            payload.scene_id
        ),

        acquired_at=(
            payload.acquired_at
        ),

        cloud_cover_pct=(
            payload.cloud_cover_pct
        ),

        ndvi=VegetationIndexRead(
            evidence_id=(
                by_variable[
                    "ndvi"
                ].id
            ),

            variable="ndvi",

            value=(
                evidence_items[0][
                    "value"
                ]
            ),

            unit="index",

            status=(
                evidence_items[0][
                    "status"
                ]
            ),

            quality_score=(
                evidence_items[0][
                    "quality_score"
                ]
            ),
        ),

        ndmi=VegetationIndexRead(
            evidence_id=(
                by_variable[
                    "ndmi"
                ].id
            ),

            variable="ndmi",

            value=(
                evidence_items[1][
                    "value"
                ]
            ),

            unit="index",

            status=(
                evidence_items[1][
                    "status"
                ]
            ),

            quality_score=(
                evidence_items[1][
                    "quality_score"
                ]
            ),
        ),
    )