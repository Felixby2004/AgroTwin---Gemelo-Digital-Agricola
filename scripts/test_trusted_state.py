import sys
from pathlib import Path
from datetime import datetime, timedelta


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


from twin.evidence import (
    MachineEvidence,
    EvidenceStatus,
)

from twin.provenance import (
    ProvenanceRecord,
    EvidenceSourceType,
)

from engines.trusted_state_engine import (
    TrustedStateEngine,
)


now = datetime.now()


def provenance(
    source_id: str,
) -> ProvenanceRecord:

    return ProvenanceRecord(
        source_type=(
            EvidenceSourceType.MEASURED
        ),

        source_name="TEST",

        source_id=source_id,

        generated_at=now,

        transformation="Test measurement",
    )


evidence_items = [

    MachineEvidence(
        evidence_id="EV-SM-GOOD",

        variable="soil_moisture",

        value=0.22,

        unit="m3/m3",

        observed_at=now,

        provenance=provenance(
            "SM-01"
        ),

        status=EvidenceStatus.ACTIVE,

        quality_score=0.95,
    ),

    MachineEvidence(
        evidence_id="EV-SM-LOW",

        variable="soil_moisture",

        value=0.20,

        unit="m3/m3",

        observed_at=now,

        provenance=provenance(
            "SM-02"
        ),

        status=EvidenceStatus.ACTIVE,

        quality_score=0.40,
    ),

    MachineEvidence(
        evidence_id="EV-RAIN-STALE",

        variable="rainfall",

        value=4.2,

        unit="mm",

        observed_at=(
            now
            - timedelta(
                hours=48
            )
        ),

        provenance=provenance(
            "RAIN-01"
        ),

        status=EvidenceStatus.STALE,

        quality_score=0.80,
    ),

    MachineEvidence(
        evidence_id="EV-TEMP",

        variable="air_temperature",

        value=27.5,

        unit="C",

        observed_at=now,

        provenance=provenance(
            "TEMP-01"
        ),

        status=EvidenceStatus.ACTIVE,

        quality_score=0.90,
    ),

    MachineEvidence(
        evidence_id="EV-BAD",

        variable="soil_moisture",

        value=-5.0,

        unit="m3/m3",

        observed_at=now,

        provenance=provenance(
            "BAD-01"
        ),

        status=EvidenceStatus.INVALID,

        quality_score=0.0,
    ),
]


engine = (
    TrustedStateEngine()
)


state = engine.build(
    evidence_items
)


print()
print(
    "TRUSTED TWIN STATE TEST"
)

print("=" * 150)


for variable, item in state.variables.items():

    print(
        variable,
        "| value=",
        item.value,
        "| unit=",
        item.unit,
        "| selected=",
        item.metadata.get(
            "selected_evidence_id"
        ),
        "| confidence=",
        item.confidence
        .confidence_score,
        "| uncertainty=",
        item.confidence
        .uncertainty_level
        .value,
        "| update=",
        item.confidence
        .requires_update,
    )


print("-" * 150)

print(
    "EXCLUDED:",
    state.excluded_evidence_ids,
)

print(
    "UPDATE REQUIRED:",
    state.update_required_variables,
)

print("=" * 150)