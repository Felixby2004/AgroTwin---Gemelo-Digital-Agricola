from io import BytesIO


from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from fastapi.responses import (
    StreamingResponse,
)

from sqlalchemy.orm import Session


from api.dependencies import (
    get_db,
)

from api.auth_dependencies import (
    get_current_user,
    check_parcel_permission,
)

from api.schemas.reports import (
    ReportPreview,
)


from database.models.identity import (
    UserModel,
)

from database.repositories.parcel_repository import (
    ParcelRepository,
)

from database.repositories.data_consent_repository import (
    DataConsentRepository,
)

from database.adapters.data_governance_adapter import (
    DataGovernanceAdapter,
)


from engines.data_governance_engine import (
    DataGovernanceEngine,
)


from services.report_data_service import (
    ReportDataService,
)

from services.report_pdf_service import (
    ReportPDFService,
)

from services.report_docx_service import (
    ReportDOCXService,
)

from services.report_excel_service import (
    ReportExcelService,
)


from twin.identity import (
    ParcelPermission,
)

from twin.data_governance import (
    DataAccessRequest,
    DataPermission,
    DataPurpose,
)


router = APIRouter(
    prefix="/reports",
    tags=[
        "reports",
    ],
)


report_data_service = (
    ReportDataService()
)

pdf_service = (
    ReportPDFService()
)

docx_service = (
    ReportDOCXService()
)

excel_service = (
    ReportExcelService()
)

governance_engine = (
    DataGovernanceEngine()
)


# =========================================================
# HELPERS
# =========================================================

def _safe_filename(
    value: str,
) -> str:

    allowed = set(
        (
            "abcdefghijklmnopqrstuvwxyz"
            "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
            "0123456789-_"
        )
    )


    clean = "".join(
        character
        if character in allowed
        else "_"

        for character
        in value
    )


    return (
        clean[:80]
        or "parcel"
    )


def _ensure_parcel(
    *,
    db: Session,
    parcel_id: str,
):

    repo = (
        ParcelRepository(
            db
        )
    )

    parcel = (
        repo.get_by_id(
            parcel_id
        )
    )


    if parcel is None:

        raise HTTPException(
            status_code=404,
            detail=(
                "Parcel not found."
            ),
        )


    return parcel


def _check_export_consent(
    *,
    db: Session,
    parcel_id: str,
    current_user: UserModel,
) -> None:

    consent_repo = (
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


    if not decision.allowed:

        raise HTTPException(
            status_code=403,
            detail=(
                "Report export denied by "
                "data governance policy: "
                + decision.reason
            ),
        )


def _build_report(
    *,
    db: Session,
    parcel_id: str,
) -> dict:

    try:

        return (
            report_data_service
            .build(
                db=db,
                parcel_id=parcel_id,
            )
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=404,
            detail=str(
                exc
            ),
        )


# =========================================================
# PREVIEW
# =========================================================

@router.get(
    "/parcels/{parcel_id}/preview",
    response_model=ReportPreview,
)
def preview_report(
    parcel_id: str,
    current_user: UserModel = Depends(
        get_current_user
    ),
    db: Session = Depends(
        get_db
    ),
):

    _ensure_parcel(
        db=db,
        parcel_id=parcel_id,
    )


    check_parcel_permission(
        db=db,
        current_user=current_user,
        parcel_id=parcel_id,
        permission=(
            ParcelPermission.VIEW
        ),
    )


    report = (
        _build_report(
            db=db,
            parcel_id=parcel_id,
        )
    )

    return ReportPreview(

        parcel_id=(
            report[
                "parcel_id"
            ]
        ),

        generated_at=(
            report[
                "generated_at"
            ]
        ),

        parcel=(
            report[
                "parcel"
            ]
        ),

        summary=(
            report[
                "summary"
            ]
        ),

        latest_decision=(
            report[
                "latest_decision"
            ]
        ),

        evidence=(
            report[
                "evidence"
            ]
        ),

        sensors=(
            report[
                "sensors"
            ]
        ),

        farmer_knowledge=(
            report[
                "farmer_knowledge"
            ]
        ),

        decision_traces=(
            report[
                "decision_traces"
            ]
        ),

        ml_complementary=(
            report[
                "ml_complementary"
            ]
        ),

        governance=(
            report[
                "governance"
            ]
        ),
    )

# =========================================================
# PDF PREVIEW
# =========================================================

@router.get(
    "/parcels/{parcel_id}/pdf-preview",
)
def preview_pdf(
    parcel_id: str,
    current_user: UserModel = Depends(
        get_current_user
    ),
    db: Session = Depends(
        get_db
    ),
):

    parcel = (
        _ensure_parcel(
            db=db,
            parcel_id=parcel_id,
        )
    )


    # Preview only requires VIEW permission.
    # It is not considered a data export.
    check_parcel_permission(
        db=db,
        current_user=current_user,
        parcel_id=parcel_id,
        permission=(
            ParcelPermission.VIEW
        ),
    )


    report = (
        _build_report(
            db=db,
            parcel_id=parcel_id,
        )
    )


    content = (
        pdf_service.generate(
            report
        )
    )


    filename = (
        _safe_filename(
            parcel.name
        )
        + "_report_preview.pdf"
    )


    return StreamingResponse(
        BytesIO(
            content
        ),

        media_type=(
            "application/pdf"
        ),

        headers={
            "Content-Disposition":
                (
                    "inline; "
                    f'filename="{filename}"'
                )
        },
    )

# =========================================================
# PDF
# =========================================================

@router.get(
    "/parcels/{parcel_id}/pdf",
)
def download_pdf(
    parcel_id: str,
    current_user: UserModel = Depends(
        get_current_user
    ),
    db: Session = Depends(
        get_db
    ),
):

    parcel = (
        _ensure_parcel(
            db=db,
            parcel_id=parcel_id,
        )
    )


    check_parcel_permission(
        db=db,
        current_user=current_user,
        parcel_id=parcel_id,
        permission=(
            ParcelPermission
            .EXPORT_DATA
        ),
    )


    _check_export_consent(
        db=db,
        parcel_id=parcel_id,
        current_user=current_user,
    )


    report = (
        _build_report(
            db=db,
            parcel_id=parcel_id,
        )
    )


    content = (
        pdf_service.generate(
            report
        )
    )


    filename = (
        _safe_filename(
            parcel.name
        )
        + "_report.pdf"
    )


    return StreamingResponse(
        BytesIO(
            content
        ),

        media_type=(
            "application/pdf"
        ),

        headers={
            "Content-Disposition":
                (
                    "attachment; "
                    f'filename="{filename}"'
                )
        },
    )


# =========================================================
# WORD
# =========================================================

@router.get(
    "/parcels/{parcel_id}/docx",
)
def download_docx(
    parcel_id: str,
    current_user: UserModel = Depends(
        get_current_user
    ),
    db: Session = Depends(
        get_db
    ),
):

    parcel = (
        _ensure_parcel(
            db=db,
            parcel_id=parcel_id,
        )
    )


    check_parcel_permission(
        db=db,
        current_user=current_user,
        parcel_id=parcel_id,
        permission=(
            ParcelPermission
            .EXPORT_DATA
        ),
    )


    _check_export_consent(
        db=db,
        parcel_id=parcel_id,
        current_user=current_user,
    )


    report = (
        _build_report(
            db=db,
            parcel_id=parcel_id,
        )
    )


    content = (
        docx_service.generate(
            report
        )
    )


    filename = (
        _safe_filename(
            parcel.name
        )
        + "_report.docx"
    )


    return StreamingResponse(
        BytesIO(
            content
        ),

        media_type=(
            "application/vnd.openxmlformats-"
            "officedocument.wordprocessingml."
            "document"
        ),

        headers={
            "Content-Disposition":
                (
                    "attachment; "
                    f'filename="{filename}"'
                )
        },
    )


# =========================================================
# EXCEL
# =========================================================

@router.get(
    "/parcels/{parcel_id}/xlsx",
)
def download_xlsx(
    parcel_id: str,
    current_user: UserModel = Depends(
        get_current_user
    ),
    db: Session = Depends(
        get_db
    ),
):

    parcel = (
        _ensure_parcel(
            db=db,
            parcel_id=parcel_id,
        )
    )


    check_parcel_permission(
        db=db,
        current_user=current_user,
        parcel_id=parcel_id,
        permission=(
            ParcelPermission
            .EXPORT_DATA
        ),
    )


    _check_export_consent(
        db=db,
        parcel_id=parcel_id,
        current_user=current_user,
    )


    report = (
        _build_report(
            db=db,
            parcel_id=parcel_id,
        )
    )


    content = (
        excel_service.generate(
            report
        )
    )


    filename = (
        _safe_filename(
            parcel.name
        )
        + "_report.xlsx"
    )


    return StreamingResponse(
        BytesIO(
            content
        ),

        media_type=(
            "application/vnd.openxmlformats-"
            "officedocument.spreadsheetml.sheet"
        ),

        headers={
            "Content-Disposition":
                (
                    "attachment; "
                    f'filename="{filename}"'
                )
        },
    )