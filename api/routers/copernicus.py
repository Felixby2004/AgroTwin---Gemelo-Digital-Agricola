import httpx

from fastapi import (
    APIRouter,
    HTTPException,
)

from api.schemas.copernicus import (
    Sentinel2SearchRequest,
    Sentinel2SearchResult,
    Sentinel2SceneRead,
    Sentinel2IndicesRequest,
    Sentinel2IndicesResult,
    Sentinel2IndexStatistics,
)

from services.copernicus_stac_service import (
    CopernicusSTACService,
)

from datetime import datetime

from fastapi import Depends

from sqlalchemy.orm import Session


from api.dependencies import get_db


from database.repositories.parcel_repository import (
    ParcelRepository,
)

from database.repositories.evidence_repository import (
    EvidenceRepository,
)


from services.copernicus_statistics_service import (
    CopernicusStatisticsService,
)

from services.sentinel2_service import (
    Sentinel2Service,
)

router = APIRouter(
    prefix="/copernicus",
    tags=["copernicus"],
)


stac_service = (
    CopernicusSTACService()
)

statistics_service = (
    CopernicusStatisticsService()
)

sentinel_service = (
    Sentinel2Service()
)

@router.post(
    "/sentinel-2/search",
    response_model=(
        Sentinel2SearchResult
    ),
)
def search_sentinel2(
    payload: Sentinel2SearchRequest,
):

    try:

        scenes = (
            stac_service
            .search_sentinel2(
                bbox=payload.bbox,

                start_date=(
                    payload.start_date
                ),

                end_date=(
                    payload.end_date
                ),

                max_cloud_cover=(
                    payload
                    .max_cloud_cover
                ),

                limit=(
                    payload.limit
                ),
            )
        )

    except (
        httpx.HTTPError,
        ValueError,
    ) as exc:

        raise HTTPException(
            status_code=502,
            detail=str(exc),
        )


    return Sentinel2SearchResult(
        count=len(
            scenes
        ),

        scenes=[
            Sentinel2SceneRead(
                scene_id=(
                    item[
                        "scene_id"
                    ]
                ),

                collection=(
                    item.get(
                        "collection"
                    )
                ),

                datetime=(
                    item.get(
                        "datetime"
                    )
                ),

                cloud_cover_pct=(
                    item.get(
                        "cloud_cover_pct"
                    )
                ),

                bbox=(
                    item.get(
                        "bbox"
                    )
                ),

                geometry=(
                    item.get(
                        "geometry"
                    )
                ),
            )

            for item
            in scenes
        ],
    )



@router.post(
    "/sentinel-2/indices",
    response_model=(
        Sentinel2IndicesResult
    ),
)
def calculate_real_indices(
    payload: Sentinel2IndicesRequest,

    db: Session = Depends(
        get_db
    ),
):

    # =====================================================
    # PARCEL
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

    geometry = (
        parcel_repo
        .get_geometry_geojson(
            payload.parcel_id
        )
    )

    if geometry is None:

        raise HTTPException(
            status_code=422,
            detail=(
                "Parcel has no geometry. "
                "A polygon is required for "
                "Sentinel-2 parcel statistics."
            ),
        )

    # =====================================================
    # COPERNICUS STATISTICS
    # =====================================================

    try:

        result = (
            statistics_service.get_indices(
                geometry=geometry,

                start_date=(
                    payload.start_date
                ),

                end_date=(
                    payload.end_date
                ),

                max_cloud_cover=(
                    payload.max_cloud_cover
                ),

                resolution_m=(
                    payload.resolution_m
                ),
            )
        )

    except (
        httpx.HTTPError,
        RuntimeError,
        ValueError,
    ) as exc:

        raise HTTPException(
            status_code=502,
            detail=str(exc),
        )


    # =====================================================
    # OBSERVATION DATE
    # =====================================================

    interval_from = (
        result[
            "interval"
        ][
            "from"
        ]
    )

    observed_at = (
        datetime.fromisoformat(
            interval_from.replace(
                "Z",
                "+00:00",
            )
        )
    )


    status = (
        sentinel_service
        .determine_status(
            acquired_at=(
                observed_at
            )
        )
    )


    # valid_fraction becomes the
    # observation quality estimate.

    quality_score = min(
        1.0,
        max(
            0.0,
            result[
                "valid_fraction"
            ],
        ),
    )


    evidence_repo = (
        EvidenceRepository(
            db
        )
    )


    provenance_base = {
        "source_type":
            "EXTERNAL",

        "source_name":
            "COPERNICUS_SENTINEL_2",

        "source_id":
            "CDSE_STATISTICAL_API",

        "source_version":
            "sentinel-2-l2a",

        "generated_at":
            observed_at.isoformat(),

        "valid_at":
            observed_at.isoformat(),

        "spatial_scope": {
            "geometry": geometry,
        },

        "parent_ids":
            [],

        "metadata": {
            "max_cloud_cover":
                payload
                .max_cloud_cover,

            "resolution_m":
                payload
                .resolution_m,

            "sample_count":
                result[
                    "sample_count"
                ],

            "no_data_count":
                result[
                    "no_data_count"
                ],

            "valid_fraction":
                result[
                    "valid_fraction"
                ],
                
            "data_origin": "CDSE_REAL",
        },
    }


    from uuid import uuid4


    ndvi_id = (
        "EV-CDSE-NDVI-"
        + uuid4().hex[
            :10
        ].upper()
    )

    ndmi_id = (
        "EV-CDSE-NDMI-"
        + uuid4().hex[
            :10
        ].upper()
    )


    try:

        evidence_repo.create(
            evidence_id=ndvi_id,

            parcel_id=(
                payload.parcel_id
            ),

            variable="ndvi",

            value=(
                result[
                    "ndvi_mean"
                ]
            ),

            unit="index",

            observed_at=(
                observed_at
            ),

            status=status,

            quality_score=(
                quality_score
            ),

            uncertainty=(
                result[
                    "ndvi_std"
                ]
            ),

            provenance={
                **provenance_base,

                "transformation":
                    (
                        "Mean NDVI calculated "
                        "with Sentinel Hub "
                        "Statistical API."
                    ),
            },

            metadata={
                "minimum":
                    result[
                        "ndvi_min"
                    ],

                "maximum":
                    result[
                        "ndvi_max"
                    ],

                "standard_deviation":
                    result[
                        "ndvi_std"
                    ],
            },
        )


        evidence_repo.create(
            evidence_id=ndmi_id,

            parcel_id=(
                payload.parcel_id
            ),

            variable="ndmi",

            value=(
                result[
                    "ndmi_mean"
                ]
            ),

            unit="index",

            observed_at=(
                observed_at
            ),

            status=status,

            quality_score=(
                quality_score
            ),

            uncertainty=(
                result[
                    "ndmi_std"
                ]
            ),

            provenance={
                **provenance_base,

                "transformation":
                    (
                        "Mean NDMI calculated "
                        "with Sentinel Hub "
                        "Statistical API."
                    ),
            },

            metadata={
                "minimum":
                    result[
                        "ndmi_min"
                    ],

                "maximum":
                    result[
                        "ndmi_max"
                    ],

                "standard_deviation":
                    result[
                        "ndmi_std"
                    ],
            },
        )


        db.commit()


    except Exception:

        db.rollback()

        raise


    return Sentinel2IndicesResult(

        parcel_id=(
            payload.parcel_id
        ),

        interval=(
            result[
                "interval"
            ]
        ),

        ndvi=(
            Sentinel2IndexStatistics(
                mean=result[
                    "ndvi_mean"
                ],

                minimum=result[
                    "ndvi_min"
                ],

                maximum=result[
                    "ndvi_max"
                ],

                standard_deviation=(
                    result[
                        "ndvi_std"
                    ]
                ),

                evidence_id=(
                    ndvi_id
                ),
            )
        ),

        ndmi=(
            Sentinel2IndexStatistics(
                mean=result[
                    "ndmi_mean"
                ],

                minimum=result[
                    "ndmi_min"
                ],

                maximum=result[
                    "ndmi_max"
                ],

                standard_deviation=(
                    result[
                        "ndmi_std"
                    ]
                ),

                evidence_id=(
                    ndmi_id
                ),
            )
        ),

        sample_count=(
            result[
                "sample_count"
            ]
        ),

        no_data_count=(
            result[
                "no_data_count"
            ]
        ),

        valid_fraction=(
            result[
                "valid_fraction"
            ]
        ),

        source_type="EXTERNAL",
    )