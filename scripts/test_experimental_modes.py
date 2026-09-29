import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from datetime import datetime, timedelta

# ---------------------------------------------------------
# Imports del proyecto
# ---------------------------------------------------------

from twin.biophysical import (
    BiophysicalScenarioResult,
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
    ConstraintType,
)

from engines.reasoning_orchestrator import (
    ReasoningOrchestrator,
)

from engines.decision_trace_engine import (
    DecisionTraceEngine,
)

now = datetime.now()


# =========================================================
# 1. ESCENARIOS BIOFÍSICOS
# =========================================================

scenarios = [

    BiophysicalScenarioResult(
        irrigation_mm=0.0,

        dry_yield_t_ha=(
            12.1561769478
        ),

        yield_potential_t_ha=(
            14.7520783323
        ),

        yield_ratio=(
            0.8240314804
        ),

        marginal_gain_kg_ha_mm=None,
    ),

    BiophysicalScenarioResult(
        irrigation_mm=20.0,

        dry_yield_t_ha=(
            13.5498404859
        ),

        yield_potential_t_ha=(
            14.8639053170
        ),

        yield_ratio=(
            0.9115935682
        ),

        marginal_gain_kg_ha_mm=(
            69.6831769061
        ),
    ),

    BiophysicalScenarioResult(
        irrigation_mm=40.0,

        dry_yield_t_ha=(
            14.2478513387
        ),

        yield_potential_t_ha=(
            14.8724661707
        ),

        yield_ratio=(
            0.9580019329
        ),

        marginal_gain_kg_ha_mm=(
            34.9005426371
        ),
    ),

    BiophysicalScenarioResult(
        irrigation_mm=60.0,

        dry_yield_t_ha=(
            14.4807267528
        ),

        yield_potential_t_ha=(
            14.8750987956
        ),

        yield_ratio=(
            0.9734877698
        ),

        marginal_gain_kg_ha_mm=(
            11.6437707071
        ),
    ),
]


# =========================================================
# 2. EVIDENCIA DE MÁQUINA
# =========================================================

machine_evidence = [

    MachineEvidence(
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

            source_name=(
                "soil-sensor-01"
            ),

            generated_at=now,

            valid_at=now,

            spatial_scope=(
                "parcel-001"
            ),
        ),
    )
]


# =========================================================
# 3. CONOCIMIENTO DEL AGRICULTOR
# =========================================================

farmer_knowledge = [


    # -----------------------------------------------------
    # OBSERVATION
    # -----------------------------------------------------

    FarmerKnowledgeItem(
        knowledge_id="FK-OBS-001",

        knowledge_type=(
            FarmerKnowledgeType.OBSERVATION
        ),

        source_id="farmer-001",
        source_role="FARMER",

        payload={
            "observation": (
                "Se observa marchitez moderada."
            ),

            "severity": "MODERATE",
        },

        created_at=now,

        spatial_scope="parcel-001",

        reported_confidence=0.8,

        validation_status=(
            KnowledgeValidationStatus
            .UNVERIFIED
        ),

        affects=[
            "crop_water_stress",
        ],
    ),


    # -----------------------------------------------------
    # EVENT
    # -----------------------------------------------------

    FarmerKnowledgeItem(
        knowledge_id="FK-EVT-001",

        knowledge_type=(
            FarmerKnowledgeType.EVENT
        ),

        source_id="farmer-001",
        source_role="FARMER",

        payload={
            "event_type":
                "IRRIGATION",

            "amount_mm":
                15.0,

            "occurred_at": (
                now
                - timedelta(
                    hours=12
                )
            ),
        },

        created_at=now,

        valid_from=(
            now
            - timedelta(
                days=1
            )
        ),

        valid_until=now,

        spatial_scope=(
            "parcel-001"
        ),

        reported_confidence=1.0,

        validation_status=(
            KnowledgeValidationStatus
            .UNVERIFIED
        ),

        affects=[
            "soil_water_state",
            "irrigation_history",
        ],
    ),


    # -----------------------------------------------------
    # CONSTRAINT
    # -----------------------------------------------------

    FarmerKnowledgeItem(
        knowledge_id="FK-CON-001",

        knowledge_type=(
            FarmerKnowledgeType.CONSTRAINT
        ),

        source_id="farmer-001",
        source_role="FARMER",

        payload={
            "variable":
                "irrigation_mm",

            "operator":
                "<=",

            "value":
                20.0,

            "unit":
                "mm",
        },

        created_at=now,

        valid_from=now,

        valid_until=(
            now
            + timedelta(
                days=1
            )
        ),

        spatial_scope=(
            "parcel-001"
        ),

        validation_status=(
            KnowledgeValidationStatus
            .CONFIRMED
        ),

        constraint_type=(
            ConstraintType.HARD
        ),

        affects=[
            "candidate_irrigation_actions",
        ],

        rationale=(
            "Disponibilidad limitada "
            "de agua."
        ),
    ),


    # -----------------------------------------------------
    # PREFERENCE
    # -----------------------------------------------------

    FarmerKnowledgeItem(
        knowledge_id="FK-PREF-001",

        knowledge_type=(
            FarmerKnowledgeType.PREFERENCE
        ),

        source_id="farmer-001",
        source_role="FARMER",

        payload={
            "objective":
                "WATER_SAVING",

            "weight":
                0.8,
        },

        created_at=now,

        spatial_scope="parcel-001",

        validation_status=(
            KnowledgeValidationStatus
            .CONFIRMED
        ),

        affects=[
            "scenario_ranking",
        ],
    ),


    # -----------------------------------------------------
    # LOCAL KNOWLEDGE
    # -----------------------------------------------------

    FarmerKnowledgeItem(
        knowledge_id="FK-LOCAL-001",

        knowledge_type=(
            FarmerKnowledgeType
            .LOCAL_KNOWLEDGE
        ),

        source_id="farmer-001",
        source_role="FARMER",

        payload={
            "claim": (
                "Esta parcela retiene agua "
                "más tiempo de lo habitual."
            ),

            "hypothesis": (
                "HIGHER_WATER_RETENTION"
            ),
        },

        created_at=now,

        spatial_scope="parcel-001",

        reported_confidence=0.9,

        validation_status=(
            KnowledgeValidationStatus
            .UNVERIFIED
        ),

        affects=[
            "soil_water_retention",
        ],
    ),
]

from engines.experimental_runner import (
    ExperimentalRunner,
)

from twin.experiment import (
    ExperimentMode,
    ExperimentCondition,
)


runner = ExperimentalRunner()


modes = [
    ExperimentMode.B0_MACHINE_ONLY,
    ExperimentMode.B1_UNTYPED_HUMAN,
    ExperimentMode.P_PROVENANCE_AWARE,
]


results = []


for mode in modes:

    result = runner.run(
        mode=mode,

        condition=(
            ExperimentCondition.CONFLICT
        ),

        scenarios=scenarios,

        evidence=machine_evidence,

        farmer_knowledge=(
            farmer_knowledge
        ),
    )

    results.append(
        result
    )


print()
print("EXPERIMENTAL MODES")
print("=" * 120)


for result in results:

    print()
    print(
        "MODE:",
        result.mode.value,
    )

    print(
        "CONDITION:",
        result.condition.value,
    )

    print(
        "RECOMMENDATION:",
        result.recommendation,
    )

    print(
        "FEASIBLE:",
        [
            scenario.irrigation_mm
            for scenario
            in result.feasible_scenarios
        ],
    )

    print(
        "REJECTED:",
        [
            scenario.irrigation_mm
            for scenario
            in result.rejected_scenarios
        ],
    )

    print(
        "CONFLICTS:",
        len(
            result.conflicts
        ),
    )

    print(
        "TRANSFORMATIONS:",
        len(
            result.transformations
        ),
    )

    print(
        "EPISTEMIC SEPARATION:",
        result
        .epistemic_separation_preserved,
    )

    print(
        "STATE CONTAMINATION:",
        result
        .state_contamination_detected,
    )

    print(
        "APPLIED KNOWLEDGE:",
        result.applied_knowledge_ids,
    )

    print(
        "IGNORED KNOWLEDGE:",
        result.ignored_knowledge_ids,
    )

    print("-" * 120)