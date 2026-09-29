from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
)

from sqlalchemy.orm import Session


from api.dependencies import (
    get_db,
)

from api.auth_dependencies import (
    get_current_user,
    check_parcel_permission,
)

from database.models.identity import (
    UserModel,
)

from database.repositories.parcel_membership_repository import (
    ParcelMembershipRepository,
)

from twin.identity import (
    SystemRole,
    ParcelPermission,
)

from api.schemas.sensor import (
    SensorBatchCreate,
    SensorBatchResult,
    SensorCreate,
    SensorRead,
    SensorReadingCreate,
    SensorReadingHistoryItem,
    SensorReadingResult,
    SensorUpdate,
)

from database.repositories.parcel_repository import (
    ParcelRepository,
)

from database.repositories.evidence_repository import (
    EvidenceRepository,
)

from database.repositories.machine_evidence_repository import (
    MachineEvidenceRepository,
)

from database.repositories.sensor_repository import (
    SensorRepository,
)

from services.sensor_ingestion_service import (
    SensorIngestionService,
)


router = APIRouter(
    prefix="/sensors",
    tags=["sensors-iot"],
)


ingestion_service = (
    SensorIngestionService()
)


def _visible_parcel_ids(
    *,
    db: Session,
    current_user: UserModel,
) -> set[str] | None:

    if (
        current_user.system_role
        == SystemRole.ADMIN.value
    ):
        return None

    memberships = (
        ParcelMembershipRepository(
            db
        )
        .list_by_user(
            current_user.id
        )
    )

    return {
        membership.parcel_id
        for membership
        in memberships
    }


def _extract_latest_value(
    value,
):
    if not isinstance(
        value,
        dict,
    ):
        return value

    if (
        "soil_moisture"
        in value
    ):
        return value[
            "soil_moisture"
        ]

    if (
        "value"
        in value
    ):
        return value[
            "value"
        ]

    for item in value.values():
        if isinstance(
            item,
            (
                int,
                float,
                str,
            ),
        ):
            return item

    return value


def _sensor_to_read(
    sensor,
    machine_repo:
        MachineEvidenceRepository,
) -> SensorRead:

    latest = (
        machine_repo
        .get_sensor_latest(
            sensor.id
        )
    )


    if not sensor.is_active:

        operational_status = (
            "INACTIVE"
        )

    elif latest is None:

        operational_status = (
            "NO_DATA"
        )

    elif latest.status == "ERROR":

        operational_status = (
            "ERROR"
        )

    elif latest.status == "STALE":

        operational_status = (
            "STALE"
        )

    else:

        operational_status = (
            "ACTIVE"
        )


    return SensorRead(
        sensor_id=sensor.id,
        parcel_id=sensor.parcel_id,
        name=sensor.name,
        sensor_type=sensor.sensor_type,
        variables=(
            sensor.variables
            or []
        ),
        latitude=sensor.latitude,
        longitude=sensor.longitude,
        manufacturer=sensor.manufacturer,
        model=sensor.model_name,
        installed_at=sensor.installed_at,
        is_active=sensor.is_active,
        operational_status=(
            operational_status
        ),
        latest_value=(
            _extract_latest_value(
                latest.value
            )
            if latest
            else None
        ),
        latest_unit=(
            latest.unit
            if latest
            else None
        ),
        latest_variable=(
            latest.variable
            if latest
            else None
        ),
        latest_quality_score=(
            latest.quality_score
            if latest
            else None
        ),
        latest_observed_at=(
            latest.observed_at
            if latest
            else None
        ),
        metadata=(
            sensor.metadata_json
            or {}
        ),
        created_at=sensor.created_at,
        updated_at=sensor.updated_at,
    )


# ======================================================
# SENSOR REGISTRY
# ======================================================

@router.post(
    "",
    response_model=SensorRead,
)
def create_sensor(
    payload: SensorCreate,
    current_user: UserModel = Depends(
        get_current_user
    ),
    db: Session = Depends(
        get_db
    ),
):

    parcel_repo = (
        ParcelRepository(
            db
        )
    )

    if (
        parcel_repo.get_by_id(
            payload.parcel_id
        )
        is None
    ):

        raise HTTPException(
            status_code=404,
            detail="Parcel not found.",
        )

    check_parcel_permission(
        db=db,
        current_user=current_user,
        parcel_id=payload.parcel_id,
        permission=(
            ParcelPermission.EDIT
        ),
    )


    repo = SensorRepository(
        db
    )

    if (
        repo.get_by_id(
            payload.sensor_id
        )
        is not None
    ):

        raise HTTPException(
            status_code=409,
            detail=(
                "Sensor already exists."
            ),
        )


    item = repo.create(
        sensor_id=payload.sensor_id,
        parcel_id=payload.parcel_id,
        name=payload.name,
        sensor_type=payload.sensor_type,
        variables=[
            variable.value
            for variable
            in payload.variables
        ],
        latitude=payload.latitude,
        longitude=payload.longitude,
        manufacturer=payload.manufacturer,
        model_name=payload.model,
        installed_at=payload.installed_at,
        is_active=payload.is_active,
        metadata=payload.metadata,
    )

    db.commit()

    db.refresh(
        item
    )

    return _sensor_to_read(
        item,
        MachineEvidenceRepository(
            db
        ),
    )


@router.get(
    "",
    response_model=list[
        SensorRead
    ],
)
def list_sensors(
    parcel_id:
        str | None = Query(
            default=None
        ),
    current_user: UserModel = Depends(
        get_current_user
    ),
    db: Session = Depends(
        get_db
    ),
):

    repo = SensorRepository(
        db
    )

    if parcel_id:

        check_parcel_permission(
            db=db,
            current_user=current_user,
            parcel_id=parcel_id,
            permission=(
                ParcelPermission.VIEW
            ),
        )

        items = repo.list_by_parcel(
            parcel_id
        )

    else:

        items = repo.list_all()

        visible_ids = _visible_parcel_ids(
            db=db,
            current_user=current_user,
        )

        if visible_ids is not None:
            items = [
                item
                for item
                in items
                if item.parcel_id
                in visible_ids
            ]

    machine_repo = (
        MachineEvidenceRepository(
            db
        )
    )

    return [
        _sensor_to_read(
            item,
            machine_repo,
        )
        for item
        in items
    ]


@router.get(
    "/parcel/{parcel_id}",
    response_model=list[
        SensorRead
    ],
)
def list_parcel_sensors(
    parcel_id: str,
    current_user: UserModel = Depends(
        get_current_user
    ),
    db: Session = Depends(
        get_db
    ),
):

    parcel_repo = (
        ParcelRepository(
            db
        )
    )

    if (
        parcel_repo.get_by_id(
            parcel_id
        )
        is None
    ):

        raise HTTPException(
            status_code=404,
            detail="Parcel not found.",
        )

    check_parcel_permission(
        db=db,
        current_user=current_user,
        parcel_id=parcel_id,
        permission=(
            ParcelPermission.VIEW
        ),
    )


    repo = SensorRepository(
        db
    )

    machine_repo = (
        MachineEvidenceRepository(
            db
        )
    )

    return [
        _sensor_to_read(
            item,
            machine_repo,
        )
        for item
        in repo.list_by_parcel(
            parcel_id
        )
    ]


@router.get(
    "/{sensor_id}/readings",
    response_model=list[
        SensorReadingHistoryItem
    ],
)
def get_sensor_readings(
    sensor_id: str,
    limit: int = Query(
        default=50,
        ge=1,
        le=500,
    ),
    current_user: UserModel = Depends(
        get_current_user
    ),
    db: Session = Depends(
        get_db
    ),
):

    sensor_repo = (
        SensorRepository(
            db
        )
    )

    sensor = sensor_repo.get_by_id(
        sensor_id
    )

    if sensor is None:

        raise HTTPException(
            status_code=404,
            detail="Sensor not found.",
        )

    check_parcel_permission(
        db=db,
        current_user=current_user,
        parcel_id=sensor.parcel_id,
        permission=(
            ParcelPermission.VIEW
        ),
    )


    rows = (
        MachineEvidenceRepository(
            db
        )
        .list_sensor_history(
            sensor_id,
            limit=limit,
        )
    )


    return [
        SensorReadingHistoryItem(
            evidence_id=row.id,
            variable=row.variable,
            value=(
                _extract_latest_value(
                    row.value
                )
            ),
            unit=row.unit,
            quality_score=(
                row.quality_score
            ),
            status=row.status,
            observed_at=(
                row.observed_at
            ),
        )
        for row
        in rows
    ]


@router.get(
    "/{sensor_id}",
    response_model=SensorRead,
)
def get_sensor(
    sensor_id: str,
    current_user: UserModel = Depends(
        get_current_user
    ),
    db: Session = Depends(
        get_db
    ),
):

    repo = SensorRepository(
        db
    )

    item = repo.get_by_id(
        sensor_id
    )

    if item is None:

        raise HTTPException(
            status_code=404,
            detail="Sensor not found.",
        )

    check_parcel_permission(
        db=db,
        current_user=current_user,
        parcel_id=item.parcel_id,
        permission=(
            ParcelPermission.VIEW
        ),
    )


    return _sensor_to_read(
        item,
        MachineEvidenceRepository(
            db
        ),
    )


@router.put(
    "/{sensor_id}",
    response_model=SensorRead,
)
def update_sensor(
    sensor_id: str,
    payload: SensorUpdate,
    current_user: UserModel = Depends(
        get_current_user
    ),
    db: Session = Depends(
        get_db
    ),
):

    repo = SensorRepository(
        db
    )

    item = repo.get_by_id(
        sensor_id
    )

    if item is None:

        raise HTTPException(
            status_code=404,
            detail="Sensor not found.",
        )

    check_parcel_permission(
        db=db,
        current_user=current_user,
        parcel_id=item.parcel_id,
        permission=(
            ParcelPermission.EDIT
        ),
    )


    item = repo.update(
        item,
        name=payload.name,
        sensor_type=payload.sensor_type,
        variables=[
            variable.value
            for variable
            in payload.variables
        ],
        latitude=payload.latitude,
        longitude=payload.longitude,
        manufacturer=payload.manufacturer,
        model_name=payload.model,
        installed_at=payload.installed_at,
        is_active=payload.is_active,
        metadata=payload.metadata,
    )

    db.commit()

    db.refresh(
        item
    )


    return _sensor_to_read(
        item,
        MachineEvidenceRepository(
            db
        ),
    )


# ======================================================
# INGEST ONE READING
# ======================================================

@router.post(
    "/readings",
    response_model=(
        SensorReadingResult
    ),
)
def ingest_sensor_reading(
    payload: SensorReadingCreate,
    current_user: UserModel = Depends(
        get_current_user
    ),
    db: Session = Depends(
        get_db
    ),
):

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

    check_parcel_permission(
        db=db,
        current_user=current_user,
        parcel_id=payload.parcel_id,
        permission=(
            ParcelPermission.EDIT
        ),
    )


    sensor_repo = (
        SensorRepository(
            db
        )
    )

    try:

        sensor_repo.ensure_from_reading(
            sensor_id=payload.sensor_id,
            parcel_id=payload.parcel_id,
            variable=payload.variable.value,
            latitude=payload.latitude,
            longitude=payload.longitude,
        )

        normalized = (
            ingestion_service
            .normalize(
                payload
            )
        )

    except ValueError as exc:

        db.rollback()

        raise HTTPException(
            status_code=422,
            detail=str(
                exc
            ),
        )


    evidence_repo = (
        EvidenceRepository(
            db
        )
    )


    item = evidence_repo.create(
        evidence_id=(
            normalized[
                "evidence_id"
            ]
        ),
        parcel_id=(
            normalized[
                "parcel_id"
            ]
        ),
        variable=(
            normalized[
                "canonical_variable"
            ]
        ),
        value=(
            normalized[
                "value"
            ]
        ),
        unit=(
            normalized[
                "unit"
            ]
        ),
        observed_at=(
            normalized[
                "observed_at"
            ]
        ),
        status=(
            normalized[
                "status"
            ]
        ),
        quality_score=(
            normalized[
                "quality_score"
            ]
        ),
        uncertainty=(
            normalized[
                "uncertainty"
            ]
        ),
        provenance=(
            normalized[
                "provenance"
            ]
        ),
        metadata=(
            normalized[
                "metadata"
            ]
        ),
    )


    db.commit()

    db.refresh(
        item
    )


    return SensorReadingResult(
        evidence_id=(
            item.id
        ),
        parcel_id=(
            payload.parcel_id
        ),
        sensor_id=(
            payload.sensor_id
        ),
        input_variable=(
            payload.variable.value
        ),
        canonical_variable=(
            item.variable
        ),
        value=(
            normalized[
                "value"
            ]
        ),
        unit=(
            item.unit
        ),
        quality_score=(
            item.quality_score
        ),
        status=(
            item.status
        ),
        observed_at=(
            item.observed_at
        ),
    )


@router.post(
    "/readings/batch",
    response_model=(
        SensorBatchResult
    ),
)
def ingest_sensor_batch(
    payload: SensorBatchCreate,
    current_user: UserModel = Depends(
        get_current_user
    ),
    db: Session = Depends(
        get_db
    ),
):

    parcel_repo = (
        ParcelRepository(
            db
        )
    )


    parcel_ids = {
        reading.parcel_id
        for reading
        in payload.readings
    }


    for parcel_id in parcel_ids:

        parcel = (
            parcel_repo.get_by_id(
                parcel_id
            )
        )

        if parcel is None:

            raise HTTPException(
                status_code=404,
                detail=(
                    f"Parcel not found: "
                    f"{parcel_id}"
                ),
            )

        check_parcel_permission(
            db=db,
            current_user=current_user,
            parcel_id=parcel_id,
            permission=(
                ParcelPermission.EDIT
            ),
        )


    sensor_repo = (
        SensorRepository(
            db
        )
    )


    try:

        for reading in payload.readings:

            sensor_repo.ensure_from_reading(
                sensor_id=reading.sensor_id,
                parcel_id=reading.parcel_id,
                variable=reading.variable.value,
                latitude=reading.latitude,
                longitude=reading.longitude,
            )


        normalized_items = (
            ingestion_service
            .normalize_batch(
                payload.readings
            )
        )

    except ValueError as exc:

        db.rollback()

        raise HTTPException(
            status_code=422,
            detail=str(
                exc
            ),
        )


    evidence_repo = (
        EvidenceRepository(
            db
        )
    )

    response_items = []

    active_count = 0

    stale_count = 0


    try:

        for reading, normalized in zip(
            payload.readings,
            normalized_items,
        ):

            item = evidence_repo.create(
                evidence_id=(
                    normalized[
                        "evidence_id"
                    ]
                ),
                parcel_id=(
                    normalized[
                        "parcel_id"
                    ]
                ),
                variable=(
                    normalized[
                        "canonical_variable"
                    ]
                ),
                value=(
                    normalized[
                        "value"
                    ]
                ),
                unit=(
                    normalized[
                        "unit"
                    ]
                ),
                observed_at=(
                    normalized[
                        "observed_at"
                    ]
                ),
                status=(
                    normalized[
                        "status"
                    ]
                ),
                quality_score=(
                    normalized[
                        "quality_score"
                    ]
                ),
                uncertainty=(
                    normalized[
                        "uncertainty"
                    ]
                ),
                provenance=(
                    normalized[
                        "provenance"
                    ]
                ),
                metadata=(
                    normalized[
                        "metadata"
                    ]
                ),
            )


            if (
                normalized[
                    "status"
                ]
                == "ACTIVE"
            ):
                active_count += 1

            elif (
                normalized[
                    "status"
                ]
                == "STALE"
            ):
                stale_count += 1


            response_items.append(
                SensorReadingResult(
                    evidence_id=(
                        item.id
                    ),
                    parcel_id=(
                        reading.parcel_id
                    ),
                    sensor_id=(
                        reading.sensor_id
                    ),
                    input_variable=(
                        reading
                        .variable
                        .value
                    ),
                    canonical_variable=(
                        item.variable
                    ),
                    value=(
                        normalized[
                            "value"
                        ]
                    ),
                    unit=(
                        normalized[
                            "unit"
                        ]
                    ),
                    quality_score=(
                        normalized[
                            "quality_score"
                        ]
                    ),
                    status=(
                        normalized[
                            "status"
                        ]
                    ),
                    observed_at=(
                        normalized[
                            "observed_at"
                        ]
                    ),
                )
            )


        db.commit()


    except Exception:

        db.rollback()

        raise


    return SensorBatchResult(
        total=len(
            response_items
        ),
        active=(
            active_count
        ),
        stale=(
            stale_count
        ),
        readings=(
            response_items
        ),
    )
