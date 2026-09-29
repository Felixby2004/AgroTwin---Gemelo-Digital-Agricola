from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from sqlalchemy.orm import Session

from geoalchemy2.elements import (
    WKTElement,
)

from api.auth_dependencies import (
    get_current_user,
    check_parcel_permission,
)

from api.dependencies import (
    get_db,
)

from api.schemas.parcel import (
    ParcelCreate,
    ParcelRead,
    ParcelUpdate,
)

from api.schemas.parcel_map import (
    ParcelMapFeature,
    ParcelMapFeatureCollection,
    ParcelMapFeatureProperties,
)

from database.repositories.parcel_repository import (
    ParcelRepository,
)

from database.repositories.parcel_membership_repository import (
    ParcelMembershipRepository,
)

from database.models.identity import (
    UserModel,
)

from twin.identity import (
    SystemRole,
    ParcelPermission,
)


from api.schemas.parcel_geometry import (
    ParcelGeometryRead,
    ParcelGeometryUpdate,
)

router = APIRouter(
    prefix="/parcels",
    tags=["parcels"],
)


def _visible_parcel_ids(
    *,
    db: Session,
    current_user: UserModel,
) -> set[str] | None:
    """
    ADMIN -> None means all parcels are visible.
    USER  -> only parcels where the user has a membership.
    """

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


# ======================================================
# CREATE PARCEL
# ======================================================

@router.post(
    "",
    response_model=ParcelRead,
)
def create_parcel(
    payload: ParcelCreate,
    current_user: UserModel = Depends(
        get_current_user
    ),
    db: Session = Depends(
        get_db
    ),
):

    _ = current_user

    repo = ParcelRepository(
        db
    )


    parcel = repo.create(
        name=payload.name,
        crop_type=payload.crop_type,
        area_ha=payload.area_ha,
        geometry=(
            WKTElement(
                payload.geometry_wkt,
                srid=4326,
            )
            if payload.geometry_wkt
            else None
        ),
    )


    db.commit()

    db.refresh(
        parcel
    )


    return parcel


# ======================================================
# LIST PARCELS
# ======================================================

@router.get(
    "",
    response_model=list[
        ParcelRead
    ],
)
def list_parcels(
    current_user: UserModel = Depends(
        get_current_user
    ),
    db: Session = Depends(
        get_db
    ),
):

    repo = ParcelRepository(
        db
    )

    items = repo.list_all()

    visible_ids = _visible_parcel_ids(
        db=db,
        current_user=current_user,
    )

    if visible_ids is None:
        return items

    return [
        item
        for item
        in items
        if item.id
        in visible_ids
    ]


# ======================================================
# PARCEL MAP
#
# IMPORTANT:
# This route MUST be declared before /{parcel_id}
# ======================================================

@router.get(
    "/map",
    response_model=ParcelMapFeatureCollection,
)
def get_parcel_map(
    current_user: UserModel = Depends(
        get_current_user
    ),
    db: Session = Depends(
        get_db
    ),
):

    repository = ParcelRepository(
        db
    )


    rows = (
        repository
        .list_with_geometry()
    )

    visible_ids = _visible_parcel_ids(
        db=db,
        current_user=current_user,
    )

    if visible_ids is not None:
        rows = [
            row
            for row
            in rows
            if row["id"]
            in visible_ids
        ]


    features: list[
        ParcelMapFeature
    ] = []


    for row in rows:

        features.append(
            ParcelMapFeature(
                geometry=row[
                    "geometry"
                ],
                properties=(
                    ParcelMapFeatureProperties(
                        parcel_id=row[
                            "id"
                        ],
                        name=row[
                            "name"
                        ],
                        crop_type=row[
                            "crop_type"
                        ],
                        area_ha=row[
                            "area_ha"
                        ],
                    )
                ),
            )
        )


    return (
        ParcelMapFeatureCollection(
            features=features
        )
    )


# ======================================================
# GET PARCEL BY ID
#
# Keep dynamic route AFTER /map.
# ======================================================

@router.get(
    "/{parcel_id}",
    response_model=ParcelRead,
)
def get_parcel(
    parcel_id: str,
    current_user: UserModel = Depends(
        get_current_user
    ),
    db: Session = Depends(
        get_db
    ),
):

    repo = ParcelRepository(
        db
    )


    parcel = repo.get_by_id(
        parcel_id
    )


    if parcel is None:

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

    return parcel


# ======================================================
# UPDATE PARCEL DETAILS
# ======================================================

@router.put(
    "/{parcel_id}",
    response_model=ParcelRead,
)
def update_parcel(
    parcel_id: str,
    payload: ParcelUpdate,
    current_user: UserModel = Depends(
        get_current_user
    ),
    db: Session = Depends(
        get_db
    ),
):

    repo = ParcelRepository(
        db
    )

    existing = repo.get_by_id(
        parcel_id
    )

    if existing is None:

        raise HTTPException(
            status_code=404,
            detail="Parcel not found.",
        )

    check_parcel_permission(
        db=db,
        current_user=current_user,
        parcel_id=parcel_id,
        permission=(
            ParcelPermission.EDIT
        ),
    )

    parcel = repo.update_details(
        parcel_id=parcel_id,
        name=payload.name,
        crop_type=payload.crop_type,
        area_ha=payload.area_ha,
    )

    if parcel is None:

        raise HTTPException(
            status_code=404,
            detail="Parcel not found.",
        )

    db.commit()

    db.refresh(
        parcel
    )

    return parcel



# ======================================================
# GET PARCEL GEOMETRY
# ======================================================

@router.get(
    "/{parcel_id}/geometry",
    response_model=ParcelGeometryRead,
)
def get_parcel_geometry(
    parcel_id: str,

    current_user: UserModel = Depends(
        get_current_user
    ),

    db: Session = Depends(
        get_db
    ),
):

    repository = ParcelRepository(
        db
    )

    parcel = (
        repository
        .get_by_id(
            parcel_id
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
        parcel_id=parcel_id,
        permission=(
            ParcelPermission.VIEW
        ),
    )

    geometry = (
        repository
        .get_geometry_geojson(
            parcel_id
        )
    )

    if geometry is None:

        raise HTTPException(
            status_code=404,
            detail=(
                "Parcel geometry not found."
            ),
        )

    return ParcelGeometryRead(
        parcel_id=parcel_id,
        geometry=geometry,
    )


# ======================================================
# UPDATE PARCEL GEOMETRY
# ======================================================

@router.put(
    "/{parcel_id}/geometry",
    response_model=ParcelGeometryRead,
)
def update_parcel_geometry(
    parcel_id: str,
    payload: ParcelGeometryUpdate,

    current_user: UserModel = Depends(
        get_current_user
    ),

    db: Session = Depends(
        get_db
    ),
):

    repository = ParcelRepository(
        db
    )


    parcel = (
        repository
        .get_by_id(
            parcel_id
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
        parcel_id=parcel_id,
        permission=(
            ParcelPermission.EDIT
        ),
    )


    try:

        updated = (
            repository
            .update_geometry_geojson(
                parcel_id=parcel_id,
                geometry=payload.geometry,
            )
        )


    except ValueError as exc:

        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc


    if not updated:

        raise HTTPException(
            status_code=404,
            detail="Parcel not found.",
        )


    db.commit()


    geometry = (
        repository
        .get_geometry_geojson(
            parcel_id
        )
    )


    if geometry is None:

        raise HTTPException(
            status_code=500,
            detail=(
                "Geometry was saved "
                "but could not be read."
            ),
        )


    return ParcelGeometryRead(
        parcel_id=parcel_id,
        geometry=geometry,
    )


# ======================================================
# REMOVE PARCEL GEOMETRY
# ======================================================

@router.delete(
    "/{parcel_id}/geometry",
)
def delete_parcel_geometry(
    parcel_id: str,

    current_user=Depends(
        get_current_user
    ),

    db: Session = Depends(
        get_db
    ),
):

    repository = ParcelRepository(
        db
    )


    parcel = (
        repository
        .get_by_id(
            parcel_id
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
        parcel_id=parcel_id,
        permission=(
            ParcelPermission.EDIT
        ),
    )


    repository.remove_geometry(
        parcel_id
    )


    db.commit()


    return {
        "parcel_id":
            parcel_id,

        "geometry":
            None,

        "status":
            "REMOVED",
    }