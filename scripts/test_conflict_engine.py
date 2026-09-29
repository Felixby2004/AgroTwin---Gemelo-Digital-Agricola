import sys
from pathlib import Path

# Agregar la raíz del proyecto al PYTHONPATH
ROOT_DIR = Path(__file__).resolve().parent.parent

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from datetime import datetime, timedelta

from engines.conflict_engine import (
    ConflictEngine,
)

from twin.evidence import (
    MachineEvidence,
)

from twin.provenance import (
    ProvenanceRecord,
    EvidenceSourceType,
)

from twin.farmer_knowledge import (
    FarmerKnowledgeItem,
    FarmerKnowledgeType,
    KnowledgeValidationStatus,
)


now = datetime.now()


# ---------------------------------------------------------
# Evidencia de máquina
# ---------------------------------------------------------

machine = MachineEvidence(
    evidence_id="EV-SM-001",

    variable="soil_water_state",

    value={
        "soil_moisture": 0.14,
        "interpretation": "LOW",
    },

    unit=None,

    observed_at=now,

    provenance=ProvenanceRecord(
        source_type=(
            EvidenceSourceType.MEASURED
        ),

        source_name="soil-sensor-01",

        generated_at=now,
        valid_at=now,

        spatial_scope="parcel-001",
    ),
)


# ---------------------------------------------------------
# Conocimiento humano
# ---------------------------------------------------------

farmer_event = FarmerKnowledgeItem(
    knowledge_id="FK-EVT-002",

    knowledge_type=(
        FarmerKnowledgeType.EVENT
    ),

    source_id="farmer-001",
    source_role="FARMER",

    payload={
        "event_type": "IRRIGATION",
        "amount_mm": 20.0,
        "occurred_at": (
            now - timedelta(hours=12)
        ),
    },

    created_at=now,

    valid_from=(
        now - timedelta(days=1)
    ),

    valid_until=now,

    spatial_scope="parcel-001",

    reported_confidence=1.0,

    validation_status=(
        KnowledgeValidationStatus.UNVERIFIED
    ),

    affects=[
        "soil_water_state",
        "irrigation_history",
    ],
)


# ---------------------------------------------------------
# Detectar conflicto
# ---------------------------------------------------------

engine = ConflictEngine()

conflict = (
    engine.detect_human_machine_conflict(
        evidence=machine,
        knowledge=farmer_event,
    )
)


print()
print("CONFLICT ENGINE")
print("=" * 120)

print(conflict)

print("=" * 120)