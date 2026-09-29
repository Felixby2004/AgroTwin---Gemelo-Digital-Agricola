from datetime import (
    datetime,
    timedelta,
    timezone,
)

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)

from sqlalchemy.orm import (
    Session,
)

from api.schemas.ml_prediction import (
    SoilMoisturePredictionInput,
)

from api.auth_dependencies import (
    check_parcel_permission,
    get_current_user,
)

from database.session import (
    get_db,
)

from database.models.identity import (
    UserModel,
)

from database.repositories.machine_evidence_repository import (
    MachineEvidenceRepository,
)

from twin.identity import (
    ParcelPermission,
)

from services.ml_feature_builder_service import (
    InsufficientMLHistoryError,
)

from services.ml_prediction_service import (
    MLPredictionService,
)

from services.parcel_ml_forecast_service import (
    ParcelMLForecastService,
)


router = APIRouter(
    prefix="/ml",
    tags=[
        "Machine Learning",
    ],
)


service = (
    MLPredictionService()
)


# ======================================================
# STATUS
# ======================================================

@router.get(
    "/status",
)
def get_ml_status():

    return service.status()


# ======================================================
# MANUAL / DEVELOPMENT PREDICTION
# ======================================================

@router.post(
    "/predict/soil-moisture",
)
def predict_soil_moisture(
    payload: SoilMoisturePredictionInput,
):

    if not service.model_available():

        raise HTTPException(
            status_code=(
                status.HTTP_409_CONFLICT
            ),
            detail=(
                "Random Forest model "
                "has not been trained."
            ),
        )


    try:

        return service.predict(
            payload.model_dump()
        )


    except ValueError as exc:

        raise HTTPException(
            status_code=(
                status.HTTP_422_UNPROCESSABLE_ENTITY
            ),
            detail=str(exc),
        ) from exc


# ======================================================
# AUTOMATIC PARCEL FORECAST
# ======================================================

@router.get(
    "/parcels/{parcel_id}/"
    "soil-moisture-forecast",
)
def get_parcel_soil_moisture_forecast(
    parcel_id: str,
    db: Session = Depends(
        get_db
    ),
    current_user: UserModel = Depends(
        get_current_user
    ),
):

    check_parcel_permission(
        db=db,
        current_user=current_user,
        parcel_id=parcel_id,
        permission=ParcelPermission.VIEW,
    )


    if not service.model_available():

        raise HTTPException(
            status_code=(
                status.HTTP_409_CONFLICT
            ),
            detail=(
                "Random Forest model "
                "has not been trained."
            ),
        )


    forecast_service = (
        ParcelMLForecastService(
            db
        )
    )


    try:

        return (
            forecast_service
            .forecast(
                parcel_id
            )
        )


    except (
        InsufficientMLHistoryError
    ) as exc:

        raise HTTPException(
            status_code=(
                status.HTTP_422_UNPROCESSABLE_ENTITY
            ),
            detail={
                "code":
                    "INSUFFICIENT_ML_HISTORY",

                "message":
                    str(exc),

                "parcel_id":
                    parcel_id,

                "required":
                    (
                        "At least 24 hours "
                        "of historical "
                        "soil-moisture evidence."
                    ),
            },
        ) from exc


    except ValueError as exc:

        raise HTTPException(
            status_code=(
                status.HTTP_422_UNPROCESSABLE_ENTITY
            ),
            detail=str(exc),
        ) from exc


# ======================================================
# COMPLEMENTARY SOIL-MOISTURE HISTORY
# ======================================================

def _extract_soil_moisture_value(
    item,
) -> float | None:

    value = item.value


    if isinstance(
        value,
        (int, float),
    ):
        return float(
            value
        )


    if not isinstance(
        value,
        dict,
    ):
        return None


    for key in (
        "soil_moisture",
        "value",
    ):

        candidate = value.get(
            key
        )

        if isinstance(
            candidate,
            (int, float),
        ):
            return float(
                candidate
            )


    return None


@router.get(
    "/parcels/{parcel_id}/"
    "soil-moisture-history",
)
def get_parcel_soil_moisture_history(
    parcel_id: str,
    hours: int = Query(
        default=72,
        ge=1,
        le=720,
    ),
    db: Session = Depends(
        get_db
    ),
    current_user: UserModel = Depends(
        get_current_user
    ),
):

    """
    Read-only historical series used exclusively by the
    complementary ML visualization.

    It does not modify TrustedState, DecisionTrace,
    recommendations, scenarios or farmer responses.
    """

    check_parcel_permission(
        db=db,
        current_user=current_user,
        parcel_id=parcel_id,
        permission=ParcelPermission.VIEW,
    )


    now = datetime.now(
        timezone.utc
    )

    start_at = (
        now
        - timedelta(
            hours=hours
        )
    )


    repository = (
        MachineEvidenceRepository(
            db
        )
    )


    evidence = (
        repository
        .list_parcel_history(
            parcel_id,
            start_at=start_at,
            end_at=now,
            variables=[
                "soil_water_state",
                "soil_moisture",
            ],
            active_only=False,
        )
    )


    points: list[dict] = []


    for item in evidence:

        if (
            item.observed_at
            is None
        ):
            continue


        if (
            item.status
            not in {
                "ACTIVE",
                "STALE",
            }
        ):
            continue


        moisture = (
            _extract_soil_moisture_value(
                item
            )
        )


        if moisture is None:
            continue


        if not (
            0.0
            <= moisture
            <= 1.0
        ):
            continue


        provenance = (
            item.provenance
            if isinstance(
                item.provenance,
                dict,
            )
            else {}
        )


        points.append({
            "timestamp":
                item.observed_at
                .isoformat(),

            "soil_moisture":
                moisture,

            "unit":
                item.unit
                or "m3/m3",

            "quality_score":
                item.quality_score,

            "status":
                item.status,

            "source_type":
                provenance.get(
                    "source_type"
                ),

            "source_name":
                provenance.get(
                    "source_name"
                ),

            "source_id":
                provenance.get(
                    "source_id"
                ),
        })


    points.sort(
        key=lambda point:
            point["timestamp"]
    )


    coverage_hours = 0.0


    if len(points) >= 2:

        first_timestamp = (
            datetime.fromisoformat(
                points[0][
                    "timestamp"
                ]
            )
        )

        last_timestamp = (
            datetime.fromisoformat(
                points[-1][
                    "timestamp"
                ]
            )
        )

        coverage_hours = max(
            0.0,
            (
                last_timestamp
                - first_timestamp
            ).total_seconds()
            / 3600.0,
        )


    return {
        "parcel_id":
            parcel_id,

        "requested_hours":
            hours,

        "coverage_hours":
            coverage_hours,

        "count":
            len(
                points
            ),

        "variable":
            "soil_water_state",

        "provenance":
            "MEASURED_OR_PERSISTED_EVIDENCE",

        "decision_authority":
            False,

        "modifies_trusted_state":
            False,

        "modifies_recommendation":
            False,

        "points":
            points,
    }

