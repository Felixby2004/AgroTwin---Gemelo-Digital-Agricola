import sys
from pathlib import Path

# Agregar la raíz del proyecto al PYTHONPATH
ROOT_DIR = Path(__file__).resolve().parent.parent

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


from datetime import datetime, timedelta

from twin.farmer_knowledge import (
    FarmerKnowledgeItem,
    FarmerKnowledgeType,
    KnowledgeValidationStatus,
    ConstraintType,
)


now = datetime.now()


items = [
    FarmerKnowledgeItem(
        knowledge_id="FK-OBS-001",

        knowledge_type=(
            FarmerKnowledgeType.OBSERVATION
        ),

        source_id="farmer-001",
        source_role="FARMER",

        payload={
            "observation": (
                "Se observa marchitez moderada "
                "en la zona norte."
            ),
            "severity": "MODERATE",
        },

        created_at=now,

        spatial_scope="parcel-001:north-zone",

        reported_confidence=0.8,

        affects=[
            "crop_water_stress",
        ],
    ),

    FarmerKnowledgeItem(
        knowledge_id="FK-EVT-001",

        knowledge_type=(
            FarmerKnowledgeType.EVENT
        ),

        source_id="farmer-001",
        source_role="FARMER",

        payload={
            "event_type": "IRRIGATION",
            "amount_mm": 15.0,
            "occurred_at": (
                now - timedelta(days=1)
            ),
        },

        created_at=now,

        spatial_scope="parcel-001",

        reported_confidence=1.0,

        validation_status=(
            KnowledgeValidationStatus.UNVERIFIED
        ),

        affects=[
            "irrigation_history",
            "soil_water_state",
        ],
    ),

    FarmerKnowledgeItem(
        knowledge_id="FK-CON-001",

        knowledge_type=(
            FarmerKnowledgeType.CONSTRAINT
        ),

        source_id="farmer-001",
        source_role="FARMER",

        payload={
            "variable": "irrigation_mm",
            "operator": "<=",
            "value": 20.0,
            "unit": "mm",
        },

        created_at=now,

        valid_from=now,
        valid_until=(
            now + timedelta(days=1)
        ),

        spatial_scope="parcel-001",

        validation_status=(
            KnowledgeValidationStatus.CONFIRMED
        ),

        constraint_type=(
            ConstraintType.HARD
        ),

        affects=[
            "candidate_irrigation_actions",
        ],

        rationale=(
            "Disponibilidad limitada "
            "de agua para hoy."
        ),
    ),

    FarmerKnowledgeItem(
        knowledge_id="FK-PREF-001",

        knowledge_type=(
            FarmerKnowledgeType.PREFERENCE
        ),

        source_id="farmer-001",
        source_role="FARMER",

        payload={
            "objective": "WATER_SAVING",
            "weight": 0.8,
        },

        created_at=now,

        spatial_scope="parcel-001",

        validation_status=(
            KnowledgeValidationStatus.CONFIRMED
        ),

        affects=[
            "scenario_ranking",
        ],
    ),

    FarmerKnowledgeItem(
        knowledge_id="FK-LOCAL-001",

        knowledge_type=(
            FarmerKnowledgeType.LOCAL_KNOWLEDGE
        ),

        source_id="farmer-001",
        source_role="FARMER",

        payload={
            "claim": (
                "La zona norte retiene agua "
                "más tiempo que el resto."
            ),
            "hypothesis": (
                "HIGHER_WATER_RETENTION"
            ),
        },

        created_at=now,

        spatial_scope="parcel-001:north-zone",

        reported_confidence=0.9,

        validation_status=(
            KnowledgeValidationStatus.UNVERIFIED
        ),

        affects=[
            "soil_water_retention",
        ],
    ),
]


print()
print("FARMER KNOWLEDGE ITEMS")
print("=" * 120)

for item in items:

    item.validate()

    print()
    print(item)

print()
print("=" * 120)
print(
    f"Items válidos: {len(items)}"
)