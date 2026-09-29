from datetime import (
    datetime,
    timezone,
)

from uuid import uuid4

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from sqlalchemy.orm import Session


# =========================================================
# API
# =========================================================

from api.dependencies import (
    get_db,
)

from api.auth_dependencies import (
    get_current_user,
    check_parcel_permission,
)

from api.schemas.data_governance import (
    DataConsentCreate,
    DataConsentRead,
    DataConsentStatusUpdate,
    DataAccessCheckRequest,
    DataAccessCheckResult,
    ParcelExportRequest,
    ParcelExportResult,
)

from api.schemas.data_audit import (
    DataAuditEventRead,
)


# =========================================================
# MODELS
# =========================================================

from database.models.identity import (
    UserModel,
)


# =========================================================
# REPOSITORIES
# =========================================================

from database.repositories.parcel_repository import (
    ParcelRepository,
)

from database.repositories.data_consent_repository import (
    DataConsentRepository,
)

from database.repositories.evidence_repository import (
    EvidenceRepository,
)

from database.repositories.farmer_knowledge_repository import (
    FarmerKnowledgeRepository,
)

from database.repositories.decision_trace_repository import (
    DecisionTraceRepository,
)

from database.repositories.data_audit_repository import (
    DataAuditRepository,
)


# =========================================================
# ADAPTERS
# =========================================================

from database.adapters.data_governance_adapter import (
    DataGovernanceAdapter,
)

from database.adapters.decision_trace_adapter import (
    DecisionTraceAdapter,
)


# =========================================================
# ENGINES
# =========================================================

from engines.data_governance_engine import (
    DataGovernanceEngine,
)


# =========================================================
# DOMAIN
# =========================================================

from twin.data_governance import (
    DataConsent,
    DataPurpose,
    DataPermission,
    ConsentStatus,
    DataAccessRequest,
)

from twin.identity import (
    ParcelPermission,
)


# =========================================================
# SERVICES
# =========================================================

from services.data_audit_service import (
    DataAuditService,
)


# =========================================================
# ROUTER
# =========================================================

router = APIRouter(
    prefix="/governance",
    tags=[
        "data-governance",
    ],
)


governance_engine = (
    DataGovernanceEngine()
)

audit_service = (
    DataAuditService()
)


# =========================================================
# HELPERS
# =========================================================

def _consent_to_schema(
    consent: DataConsent,
) -> DataConsentRead:

    return DataConsentRead(
        consent_id=(
            consent.consent_id
        ),

        parcel_id=(
            consent.parcel_id
        ),

        subject_id=(
            consent.subject_id
        ),

        purposes=[
            item.value
            for item
            in consent.purposes
        ],

        permissions=[
            item.value
            for item
            in consent.permissions
        ],

        allowed_data_categories=(
            consent
            .allowed_data_categories
        ),

        created_at=(
            consent.created_at
        ),

        valid_until=(
            consent.valid_until
        ),

        status=(
            consent.status.value
        ),

        metadata=(
            consent.metadata
        ),
    )


# =========================================================
# CREATE CONSENT
# =========================================================

@router.post(
    "/consents",
    response_model=(
        DataConsentRead
    ),
)
def create_consent(
    payload: DataConsentCreate,
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


    # =====================================================
    # AUTHORIZATION
    # =====================================================

    check_parcel_permission(
        db=db,
        current_user=current_user,
        parcel_id=payload.parcel_id,
        permission=(
            ParcelPermission
            .MANAGE_GOVERNANCE
        ),
    )


    try:

        purposes = [
            DataPurpose(
                item
            )
            for item
            in payload.purposes
        ]

        permissions = [
            DataPermission(
                item
            )
            for item
            in payload.permissions
        ]

    except ValueError as exc:

        raise HTTPException(
            status_code=422,
            detail=str(
                exc
            ),
        )


    consent = DataConsent(

        consent_id=(
            "CONSENT-"
            + uuid4()
            .hex[:12]
            .upper()
        ),

        parcel_id=(
            payload.parcel_id
        ),

        subject_id=(
            payload.subject_id
        ),

        purposes=(
            purposes
        ),

        permissions=(
            permissions
        ),

        allowed_data_categories=(
            payload
            .allowed_data_categories
        ),

        created_at=(
            datetime.now(
                timezone.utc
            )
        ),

        valid_until=(
            payload.valid_until
        ),

        status=(
            ConsentStatus.ACTIVE
        ),

        metadata=(
            payload.metadata
        ),
    )


    repo = (
        DataConsentRepository(
            db
        )
    )


    try:

        model = repo.create(
            **(
                DataGovernanceAdapter
                .to_model_dict(
                    consent
                )
            )
        )


        audit_service.log(

            db=db,

            parcel_id=(
                payload.parcel_id
            ),

            actor_id=(
                current_user.id
            ),

            action=(
                "CREATE_CONSENT"
            ),

            allowed=True,

            consent_id=(
                consent.consent_id
            ),

            details={
                "subject_id":
                    payload.subject_id,

                "purposes": [
                    item.value
                    for item
                    in purposes
                ],

                "permissions": [
                    item.value
                    for item
                    in permissions
                ],
            },
        )


        db.commit()

        db.refresh(
            model
        )


    except Exception:

        db.rollback()

        raise


    return (
        _consent_to_schema(
            DataGovernanceAdapter
            .from_model(
                model
            )
        )
    )


# =========================================================
# LIST CONSENTS
# =========================================================

@router.get(
    "/consents/parcel/{parcel_id}",
    response_model=list[
        DataConsentRead
    ],
)
def list_parcel_consents(
    parcel_id: str,
    current_user: UserModel = Depends(
        get_current_user
    ),
    db: Session = Depends(
        get_db
    ),
):

    check_parcel_permission(
        db=db,
        current_user=current_user,
        parcel_id=parcel_id,
        permission=(
            ParcelPermission.VIEW
        ),
    )


    repo = (
        DataConsentRepository(
            db
        )
    )


    models = (
        repo.list_by_parcel(
            parcel_id
        )
    )


    return [

        _consent_to_schema(
            DataGovernanceAdapter
            .from_model(
                model
            )
        )

        for model
        in models
    ]


# =========================================================
# UPDATE CONSENT STATUS
# =========================================================

@router.patch(
    "/consents/{consent_id}/status",
    response_model=(
        DataConsentRead
    ),
)
def update_consent_status(
    consent_id: str,
    payload: DataConsentStatusUpdate,
    current_user: UserModel = Depends(
        get_current_user
    ),
    db: Session = Depends(
        get_db
    ),
):

    repo = (
        DataConsentRepository(
            db
        )
    )


    existing = (
        repo.get_by_id(
            consent_id
        )
    )


    if existing is None:

        raise HTTPException(
            status_code=404,
            detail=(
                "Consent not found."
            ),
        )


    check_parcel_permission(
        db=db,
        current_user=current_user,
        parcel_id=(
            existing.parcel_id
        ),
        permission=(
            ParcelPermission
            .MANAGE_GOVERNANCE
        ),
    )


    try:

        status = (
            ConsentStatus(
                payload.status
            )
        )

    except ValueError:

        raise HTTPException(
            status_code=422,
            detail=(
                "status must be ACTIVE, "
                "REVOKED or EXPIRED."
            ),
        )


    model = (
        repo.update_status(
            consent_id=(
                consent_id
            ),
            status=(
                status.value
            ),
        )
    )


    try:

        audit_service.log(

            db=db,

            parcel_id=(
                model.parcel_id
            ),

            actor_id=(
                current_user.id
            ),

            action=(
                "UPDATE_CONSENT_STATUS"
            ),

            allowed=True,

            consent_id=(
                model.id
            ),

            details={
                "new_status":
                    status.value
            },
        )


        db.commit()

        db.refresh(
            model
        )


    except Exception:

        db.rollback()

        raise


    return (
        _consent_to_schema(
            DataGovernanceAdapter
            .from_model(
                model
            )
        )
    )


# =========================================================
# ACCESS CHECK
# =========================================================

@router.post(
    "/access/check",
    response_model=(
        DataAccessCheckResult
    ),
)
def check_access(
    payload: DataAccessCheckRequest,
    current_user: UserModel = Depends(
        get_current_user
    ),
    db: Session = Depends(
        get_db
    ),
):

    check_parcel_permission(
        db=db,
        current_user=current_user,
        parcel_id=(
            payload.parcel_id
        ),
        permission=(
            ParcelPermission.VIEW
        ),
    )


    try:

        request = (
            DataAccessRequest(

                actor_id=(
                    payload.actor_id
                ),

                parcel_id=(
                    payload.parcel_id
                ),

                permission=(
                    DataPermission(
                        payload.permission
                    )
                ),

                purpose=(
                    DataPurpose(
                        payload.purpose
                    )
                ),

                data_category=(
                    payload.data_category
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


    repo = (
        DataConsentRepository(
            db
        )
    )


    consents = [

        DataGovernanceAdapter
        .from_model(
            model
        )

        for model
        in repo.list_by_parcel(
            payload.parcel_id
        )
    ]


    decision = (
        governance_engine.evaluate(
            request=request,
            consents=consents,
        )
    )


    audit_service.log(

        db=db,

        parcel_id=(
            payload.parcel_id
        ),

        actor_id=(
            current_user.id
        ),

        action=(
            "ACCESS_CHECK"
        ),

        allowed=(
            decision.allowed
        ),

        consent_id=(
            decision.consent_id
        ),

        purpose=(
            payload.purpose
        ),

        data_category=(
            payload.data_category
        ),

        details={
            "requested_actor_id":
                payload.actor_id,

            "permission":
                payload.permission,

            "reason":
                decision.reason,
        },
    )


    db.commit()


    return DataAccessCheckResult(
        allowed=(
            decision.allowed
        ),
        reason=(
            decision.reason
        ),
        consent_id=(
            decision.consent_id
        ),
        metadata=(
            decision.metadata
        ),
    )


# =========================================================
# EXPORT PARCEL
# =========================================================

@router.post(
    "/parcels/{parcel_id}/export",
    response_model=(
        ParcelExportResult
    ),
)
def export_parcel(
    parcel_id: str,
    payload: ParcelExportRequest,
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
            parcel_id
        )
    )


    if parcel is None:

        raise HTTPException(
            status_code=404,
            detail="Parcel not found.",
        )


    # =====================================================
    # ROLE AUTHORIZATION
    # =====================================================

    check_parcel_permission(
        db=db,
        current_user=current_user,
        parcel_id=parcel_id,
        permission=(
            ParcelPermission
            .EXPORT_DATA
        ),
    )


    # =====================================================
    # CONSENT AUTHORIZATION
    # =====================================================

    consent_repo = (
        DataConsentRepository(
            db
        )
    )


    consents = [

        DataGovernanceAdapter
        .from_model(
            item
        )

        for item
        in consent_repo
        .list_by_parcel(
            parcel_id
        )
    ]


    request = (
        DataAccessRequest(
            actor_id=(
                current_user.id
            ),
            parcel_id=(
                parcel_id
            ),
            permission=(
                DataPermission.EXPORT
            ),
            purpose=(
                DataPurpose.EXPORT
            ),
            data_category=(
                "PARCEL_DATA"
            ),
        )
    )


    decision = (
        governance_engine.evaluate(
            request=request,
            consents=consents,
        )
    )


    audit_service.log(

        db=db,

        parcel_id=(
            parcel_id
        ),

        actor_id=(
            current_user.id
        ),

        action=(
            "EXPORT"
            if decision.allowed
            else "EXPORT_DENIED"
        ),

        allowed=(
            decision.allowed
        ),

        consent_id=(
            decision.consent_id
        ),

        purpose=(
            "EXPORT"
        ),

        data_category=(
            "PARCEL_DATA"
        ),

        details={
            "reason":
                decision.reason
        },
    )


    db.commit()


    if not decision.allowed:

        raise HTTPException(
            status_code=403,
            detail=(
                decision.reason
            ),
        )


    export_data = {

        "parcel": {
            "id":
                parcel.id,

            "name":
                parcel.name,

            "crop_type":
                parcel.crop_type,

            "area_ha":
                parcel.area_ha,
        }
    }


    if payload.include_geometry:

        export_data[
            "parcel"
        ][
            "geometry"
        ] = (
            parcel_repo
            .get_geometry_geojson(
                parcel_id
            )
        )


    if payload.include_evidence:

        evidence_repo = (
            EvidenceRepository(
                db
            )
        )


        items = (
            evidence_repo
            .list_by_parcel(
                parcel_id
            )
        )


        export_data[
            "machine_evidence"
        ] = [

            {
                "id":
                    item.id,

                "variable":
                    item.variable,

                "value":
                    item.value,

                "unit":
                    item.unit,

                "observed_at":
                    (
                        item.observed_at
                        .isoformat()

                        if item.observed_at
                        is not None

                        else None
                    ),

                "status":
                    item.status,

                "quality_score":
                    item.quality_score,

                "uncertainty":
                    item.uncertainty,

                "provenance":
                    item.provenance,

                "metadata":
                    item.metadata_json,
            }

            for item
            in items
        ]


    if (
        payload
        .include_farmer_knowledge
    ):

        knowledge_repo = (
            FarmerKnowledgeRepository(
                db
            )
        )


        items = (
            knowledge_repo
            .list_by_parcel(
                parcel_id
            )
        )


        export_data[
            "farmer_knowledge"
        ] = [

            {
                "id":
                    item.id,

                "knowledge_type":
                    item.knowledge_type,

                "source_id":
                    item.source_id,

                "source_role":
                    item.source_role,

                "payload":
                    item.payload,

                "validation_status":
                    item.validation_status,

                "constraint_type":
                    item.constraint_type,

                "affects":
                    item.affects,

                "rationale":
                    item.rationale,

                "created_at":
                    (
                        item.created_at
                        .isoformat()

                        if item.created_at
                        is not None

                        else None
                    ),

                "metadata":
                    item.metadata_json,
            }

            for item
            in items
        ]


    if (
        payload
        .include_decision_traces
    ):

        trace_repo = (
            DecisionTraceRepository(
                db
            )
        )


        traces = (
            trace_repo
            .list_by_parcel(
                parcel_id
            )
        )


        export_data[
            "decision_traces"
        ] = [

            DecisionTraceAdapter
            .from_model(
                item
            )

            for item
            in traces
        ]


    export_data[
        "_metadata"
    ] = {

        "schema":
            (
                "participatory-agricultural-"
                "digital-twin"
            ),

        "schema_version":
            "0.1.0",

        "exported_under_consent":
            decision.consent_id,

        "authenticated_user_id":
            current_user.id,

        "purpose":
            payload.purpose,

        "provenance_preserved":
            True,
    }


    return ParcelExportResult(

        parcel_id=(
            parcel_id
        ),

        generated_at=(
            datetime.now(
                timezone.utc
            )
        ),

        format=(
            "JSON+GeoJSON"
        ),

        data=(
            export_data
        ),
    )


# =========================================================
# AUDIT TRAIL
# =========================================================

@router.get(
    "/audit/parcel/{parcel_id}",
    response_model=list[
        DataAuditEventRead
    ],
)
def list_parcel_audit(
    parcel_id: str,
    current_user: UserModel = Depends(
        get_current_user
    ),
    db: Session = Depends(
        get_db
    ),
):

    check_parcel_permission(
        db=db,
        current_user=current_user,
        parcel_id=parcel_id,
        permission=(
            ParcelPermission
            .MANAGE_GOVERNANCE
        ),
    )


    repo = (
        DataAuditRepository(
            db
        )
    )


    items = (
        repo.list_by_parcel(
            parcel_id
        )
    )


    return [

        DataAuditEventRead(

            audit_id=(
                item.id
            ),

            parcel_id=(
                item.parcel_id
            ),

            actor_id=(
                item.actor_id
            ),

            action=(
                item.action
            ),

            allowed=(
                item.allowed
            ),

            consent_id=(
                item.consent_id
            ),

            purpose=(
                item.purpose
            ),

            data_category=(
                item.data_category
            ),

            created_at=(
                item.created_at
            ),

            details=(
                item.details
                or {}
            ),
        )

        for item
        in items
    ]