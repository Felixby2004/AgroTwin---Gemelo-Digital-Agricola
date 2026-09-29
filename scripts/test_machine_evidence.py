import sys
from pathlib import Path

# Agregar la raíz del proyecto al PYTHONPATH
ROOT_DIR = Path(__file__).resolve().parent.parent

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from datetime import datetime

from twin.evidence import (
    MachineEvidence,
    EvidenceStatus,
)

from twin.provenance import (
    ProvenanceRecord,
    EvidenceSourceType,
)


provenance = ProvenanceRecord(
    source_type=EvidenceSourceType.MODEL_DERIVED,
    source_name="AquaCrop",
    source_version="3.1.0",

    generated_at=datetime.now(),

    spatial_scope="parcel-001",

    transformation=(
        "AquaCrop irrigation scenario simulation"
    ),

    metadata={
        "soil_source": "SoilGrids",
        "weather_source": "NASA POWER",
        "soil_profile_depth_m": 2.0,
        "soil_layers": 6,
        "crop": "Maize",
    },
)


evidence = MachineEvidence(
    evidence_id="EV-AQUA-001",

    variable="dry_yield_t_ha",
    value=14.4807,
    unit="t/ha",

    observed_at=None,

    provenance=provenance,

    status=EvidenceStatus.ACTIVE,

    quality_score=None,
    uncertainty=None,
)


print()
print("MACHINE EVIDENCE")
print("=" * 100)

print(evidence)

print("=" * 100)