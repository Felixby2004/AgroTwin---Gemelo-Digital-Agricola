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


from api.schemas import (
    ParcelCreate,
    MachineEvidenceCreate,
    ProvenanceSchema,
    FarmerKnowledgeCreate,
)


print()
print(
    "PYDANTIC CONTRACTS TEST"
)

print("=" * 100)


parcel = ParcelCreate(
    name="Parcel API Test",
    crop_type="Maize",
    area_ha=1.5,
)

print(
    "PARCEL:",
    parcel.model_dump(),
)


provenance = ProvenanceSchema(
    source_type="MEASURED",
    source_name="TEST_SENSOR",
    source_id="S-001",
    generated_at=(
        datetime.now(
            timezone.utc
        )
    ),
)


evidence = MachineEvidenceCreate(
    evidence_id="EV-API-001",
    parcel_id=None,
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
    provenance=provenance,
)

print(
    "EVIDENCE:",
    evidence.model_dump(),
)


knowledge = FarmerKnowledgeCreate(
    knowledge_id="FK-API-001",
    parcel_id=None,
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
    validation_status=(
        "CONFIRMED"
    ),
    affects=[
        "irrigation_mm"
    ],
)

print(
    "KNOWLEDGE:",
    knowledge.model_dump(),
)


print("=" * 100)

print(
    "PYDANTIC CONTRACTS TEST: OK"
)