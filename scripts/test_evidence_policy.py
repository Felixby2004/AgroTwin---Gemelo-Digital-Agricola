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

from engines.evidence_policy_engine import (
    EvidencePolicyEngine,
)


now = datetime.now()


def make_provenance(
    source_id: str,
) -> ProvenanceRecord:

    return ProvenanceRecord(
        source_type=(
            EvidenceSourceType.MEASURED
        ),

        source_name="TEST_SENSOR",

        source_id=source_id,

        generated_at=now,

        transformation="Raw test measurement",
    )


evidence_items = [

    # =====================================================
    # ACTIVE / GOOD QUALITY
    # =====================================================

    MachineEvidence(
        evidence_id="EV-ACTIVE-GOOD",

        variable="soil_moisture",

        value=0.23,

        unit="m3/m3",

        observed_at=now,

        provenance=make_provenance(
            "SENSOR-001"
        ),

        status=EvidenceStatus.ACTIVE,

        quality_score=0.95,
    ),


    # =====================================================
    # ACTIVE / LOW QUALITY
    # =====================================================

    MachineEvidence(
        evidence_id="EV-ACTIVE-LOW",

        variable="soil_moisture",

        value=0.20,

        unit="m3/m3",

        observed_at=now,

        provenance=make_provenance(
            "SENSOR-002"
        ),

        status=EvidenceStatus.ACTIVE,

        quality_score=0.40,
    ),


    # =====================================================
    # STALE
    # =====================================================

    MachineEvidence(
        evidence_id="EV-STALE",

        variable="soil_moisture",

        value=0.18,

        unit="m3/m3",

        observed_at=(
            now
            - timedelta(
                hours=72
            )
        ),

        provenance=make_provenance(
            "SENSOR-003"
        ),

        status=EvidenceStatus.STALE,

        quality_score=0.70,
    ),


    # =====================================================
    # INVALID
    # =====================================================

    MachineEvidence(
        evidence_id="EV-INVALID",

        variable="soil_moisture",

        value=-10.0,

        unit="m3/m3",

        observed_at=now,

        provenance=make_provenance(
            "SENSOR-004"
        ),

        status=EvidenceStatus.INVALID,

        quality_score=0.10,
    ),
]


engine = EvidencePolicyEngine()


decisions = engine.evaluate_all(
    evidence_items
)


print()
print(
    "EVIDENCE POLICY TEST"
)

print("=" * 120)


for decision in decisions:

    print(
        decision.evidence_id,
        "| policy=",
        decision.policy.value,
        "| reasoning=",
        decision.usable_for_reasoning,
        "| current_state=",
        decision.usable_as_current_state,
        "| update=",
        decision.requires_update,
        "| weight=",
        decision.confidence_weight,
    )


print("=" * 120)
print(
    "TOTAL:",
    len(decisions),
)