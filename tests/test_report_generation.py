from datetime import (
    datetime,
    timezone,
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


def build_report():

    return {

        "parcel_id":
            "PARCEL-TEST",

        "generated_at":
            datetime.now(
                timezone.utc
            ),

        "parcel": {

            "id":
                "PARCEL-TEST",

            "name":
                "Test Parcel",

            "crop_type":
                "Maize",

            "area_ha":
                2.0,

            "geometry": {
                "type":
                    "Polygon",

                "coordinates":
                    [],
            },
        },


        "summary": {

            "evidence_count":
                1,

            "active_evidence_count":
                1,

            "stale_evidence_count":
                0,

            "farmer_knowledge_count":
                1,

            "decision_trace_count":
                1,

            "active_consent_count":
                1,
        },


        "latest_decision": {

            "trace_id":
                "TRACE-001",

            "provisional_recommendation": {
                "irrigation_mm":
                    20
            },
        },


        "evidence": [

            {
                "id":
                    "EV-001",

                "variable":
                    "soil_water_state",

                "value": {
                    "soil_moisture":
                        0.23
                },

                "unit":
                    "m3/m3",

                "observed_at":
                    datetime.now(
                        timezone.utc
                    ),

                "status":
                    "ACTIVE",

                "quality_score":
                    0.98,

                "uncertainty":
                    None,

                "provenance": {
                    "source":
                        "IOT"
                },

                "metadata":
                    {},
            }
        ],


        "farmer_knowledge": [

            {
                "id":
                    "FK-001",

                "knowledge_type":
                    "OBSERVATION",

                "source_id":
                    "FARMER-001",

                "source_role":
                    "FARMER",

                "payload": {
                    "text":
                        "Soil appears dry."
                },

                "validation_status":
                    "VALID",

                "constraint_type":
                    None,

                "affects":
                    [
                        "soil_water_state"
                    ],

                "rationale":
                    None,

                "created_at":
                    datetime.now(
                        timezone.utc
                    ),

                "valid_from":
                    None,

                "valid_until":
                    None,

                "reported_confidence":
                    0.9,

                "metadata":
                    {},
            }
        ],


        "decision_traces": [

            {
                "trace_id":
                    "TRACE-001"
            }
        ],


        "governance": {

            "consent_count":
                1,

            "active_consent_count":
                1,

            "audit_event_count":
                1,

            "latest_audit_events":
                [],
        },
    }


def test_pdf_generation():

    content = (
        ReportPDFService()
        .generate(
            build_report()
        )
    )

    assert isinstance(
        content,
        bytes,
    )

    assert (
        content[:4]
        == b"%PDF"
    )


def test_docx_generation():

    content = (
        ReportDOCXService()
        .generate(
            build_report()
        )
    )

    assert isinstance(
        content,
        bytes,
    )

    assert (
        content[:2]
        == b"PK"
    )


def test_excel_generation():

    content = (
        ReportExcelService()
        .generate(
            build_report()
        )
    )

    assert isinstance(
        content,
        bytes,
    )

    assert (
        content[:2]
        == b"PK"
    )