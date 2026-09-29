import sys
from pathlib import Path
from datetime import datetime, timezone


ROOT_DIR = (
    Path(__file__)
    .resolve()
    .parent
    .parent
)

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(
        0,
        str(ROOT_DIR),
    )


from database.session import (
    SessionLocal,
)

from database.repositories import (
    ParcelRepository,
    EvidenceRepository,
    FarmerKnowledgeRepository,
    DecisionTraceRepository,
)


print()
print("REPOSITORY TEST")
print("=" * 120)


with SessionLocal() as session:

    parcel_repo = (
        ParcelRepository(
            session
        )
    )

    evidence_repo = (
        EvidenceRepository(
            session
        )
    )

    knowledge_repo = (
        FarmerKnowledgeRepository(
            session
        )
    )

    trace_repo = (
        DecisionTraceRepository(
            session
        )
    )


    # =====================================================
    # PARCEL
    # =====================================================

    parcel = parcel_repo.create(
        name="Test Parcel",
        crop_type="Maize",
        area_ha=1.5,
    )

    print(
        "PARCEL CREATED:",
        parcel.id,
        parcel.name,
    )


    # =====================================================
    # EVIDENCE
    # =====================================================

    evidence = evidence_repo.create(
        evidence_id="EV-DB-001",
        parcel_id=parcel.id,
        variable="soil_water_state",
        value={
            "soil_moisture": 0.21,
            "interpretation": "ADEQUATE",
        },
        unit="m3/m3",
        observed_at=(
            datetime.now(
                timezone.utc
            )
        ),
        status="ACTIVE",
        quality_score=0.95,
        uncertainty=None,
        provenance={
            "source_type": "MEASURED",
            "source_name": "TEST_SENSOR",
        },
        metadata={
            "test": True,
        },
    )

    print(
        "EVIDENCE CREATED:",
        evidence.id,
        evidence.variable,
    )


    # =====================================================
    # FARMER KNOWLEDGE
    # =====================================================

    knowledge = (
        knowledge_repo.create(
            knowledge_id="FK-DB-001",
            parcel_id=parcel.id,
            knowledge_type="PREFERENCE",
            source_id="FARMER-001",
            source_role="FARMER",
            payload={
                "objective":
                    "WATER_SAVING",

                "weight":
                    0.8,
            },
            created_at=(
                datetime.now(
                    timezone.utc
                )
            ),
            valid_from=None,
            valid_until=None,
            reported_confidence=None,
            validation_status=(
                "CONFIRMED"
            ),
            constraint_type=None,
            affects=[
                "irrigation_mm"
            ],
            rationale=(
                "Test preference"
            ),
            metadata={
                "test": True,
            },
        )
    )

    print(
        "KNOWLEDGE CREATED:",
        knowledge.id,
        knowledge.knowledge_type,
    )


    # =====================================================
    # DECISION TRACE
    # =====================================================

    trace = trace_repo.create(
        trace_id="TRACE-DB-001",
        parcel_id=parcel.id,
        created_at=(
            datetime.now(
                timezone.utc
            )
        ),
        evidence_ids=[
            evidence.id
        ],
        knowledge_ids=[
            knowledge.id
        ],
        conflict_ids=[],
        transformation_ids=[],
        feasible_scenarios=[
            {
                "irrigation_mm":
                    20.0
            }
        ],
        rejected_scenarios=[],
        ranking=[
            {
                "irrigation_mm":
                    20.0,

                "score":
                    0.81,
            }
        ],
        provisional_recommendation={
            "irrigation_mm":
                20.0
        },
        farmer_response=None,
        outcome=None,
        metadata={
            "test": True,
        },
    )

    print(
        "TRACE CREATED:",
        trace.id,
    )


    session.commit()


print("-" * 120)


with SessionLocal() as session:

    parcel_repo = (
        ParcelRepository(
            session
        )
    )

    evidence_repo = (
        EvidenceRepository(
            session
        )
    )

    knowledge_repo = (
        FarmerKnowledgeRepository(
            session
        )
    )

    trace_repo = (
        DecisionTraceRepository(
            session
        )
    )


    parcel = (
        parcel_repo.list_all()[0]
    )

    evidence_items = (
        evidence_repo
        .list_by_parcel(
            parcel.id
        )
    )

    knowledge_items = (
        knowledge_repo
        .list_by_parcel(
            parcel.id
        )
    )

    traces = (
        trace_repo
        .list_by_parcel(
            parcel.id
        )
    )


    print(
        "PARCEL READ:",
        parcel.id,
    )

    print(
        "EVIDENCE COUNT:",
        len(
            evidence_items
        ),
    )

    print(
        "KNOWLEDGE COUNT:",
        len(
            knowledge_items
        ),
    )

    print(
        "TRACE COUNT:",
        len(
            traces
        ),
    )


print("=" * 120)
print("REPOSITORY TEST: OK")