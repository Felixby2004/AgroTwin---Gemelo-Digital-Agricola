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

from engines.state_confidence_engine import (
    StateConfidenceEngine,
)


now = datetime.now()


def provenance(
    source_id: str,
) -> ProvenanceRecord:

    return ProvenanceRecord(
        source_type=(
            EvidenceSourceType.MEASURED
        ),

        source_name="TEST_SENSOR",

        source_id=source_id,

        generated_at=now,

        transformation="Test measurement",
    )


evidence_items = [

    MachineEvidence(
        evidence_id="EV-SM-01",

        variable="soil_moisture",

        value=0.22,

        unit="m3/m3",

        observed_at=now,

        provenance=provenance(
            "SENSOR-01"
        ),

        status=EvidenceStatus.ACTIVE,

        quality_score=0.95,
    ),

    MachineEvidence(
        evidence_id="EV-SM-02",

        variable="soil_moisture",

        value=0.21,

        unit="m3/m3",

        observed_at=now,

        provenance=provenance(
            "SENSOR-02"
        ),

        status=EvidenceStatus.ACTIVE,

        quality_score=0.75,
    ),

    MachineEvidence(
        evidence_id="EV-SM-STALE",

        variable="soil_moisture",

        value=0.18,

        unit="m3/m3",

        observed_at=(
            now
            - timedelta(
                hours=72
            )
        ),

        provenance=provenance(
            "SENSOR-03"
        ),

        status=EvidenceStatus.STALE,

        quality_score=0.70,
    ),

    MachineEvidence(
        evidence_id="EV-TEMP-01",

        variable="air_temperature",

        value=27.5,

        unit="C",

        observed_at=now,

        provenance=provenance(
            "WEATHER-01"
        ),

        status=EvidenceStatus.ACTIVE,

        quality_score=0.90,
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
            "WEATHER-02"
        ),

        status=EvidenceStatus.STALE,

        quality_score=0.80,
    ),
]


engine = (
    StateConfidenceEngine()
)


results = engine.calculate_all(
    evidence_items
)


print()
print(
    "STATE CONFIDENCE TEST"
)

print("=" * 140)


for result in results:

    print(
        result.variable,
        "| confidence=",
        result.confidence_score,
        "| uncertainty=",
        result.uncertainty_level.value,
        "| supporting=",
        result.supporting_evidence_count,
        "| current=",
        result.current_state_evidence_count,
        "| degraded=",
        result.degraded_evidence_count,
        "| excluded=",
        result.excluded_evidence_count,
        "| update=",
        result.requires_update,
    )


print("=" * 140)

print(
    "TOTAL VARIABLES:",
    len(results),
)