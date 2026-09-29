import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from datetime import datetime, timedelta
from copy import deepcopy

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

from engines.farmer_response_engine import (
    FarmerResponseEngine,
)

from twin.decision_trace import (
    DecisionResponseType,
)

response_engine = (
    FarmerResponseEngine()
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


# =========================================================
# 4. EJECUTAR ORQUESTADOR
# =========================================================

orchestrator = (
    ReasoningOrchestrator()
)


result = orchestrator.run(
    scenarios=scenarios,
    evidence=machine_evidence,
    farmer_knowledge=farmer_knowledge,
)

trace_engine = (
    DecisionTraceEngine()
)

trace = trace_engine.build_trace(
    reasoning_result=result,

    evidence=machine_evidence,

    farmer_knowledge=farmer_knowledge,

    parcel_id="parcel-001",
)


# =========================================================
# 5. MOSTRAR EFECTOS
# =========================================================

print()
print("KNOWLEDGE EFFECTS")
print("=" * 100)


for effect in result.knowledge_effects:

    print(
        effect.knowledge_id,
        "|",
        effect.effect_type.value,
        "|",
        effect.reason,
    )


# =========================================================
# 6. MOSTRAR CONFLICTOS
# =========================================================

print()
print("CONFLICTS")
print("=" * 100)


if not result.conflicts:

    print(
        "No se detectaron conflictos."
    )

else:

    for conflict in result.conflicts:

        print(
            conflict.conflict_type.value,
            "|",
            conflict.left_item_id,
            "|",
            conflict.right_item_id,
            "|",
            conflict.status.value,
        )


# =========================================================
# 7. ESCENARIOS FACTIBLES
# =========================================================

print()
print("FEASIBLE SCENARIOS")
print("=" * 100)


for scenario in result.feasible_scenarios:

    print(
        f"{scenario.irrigation_mm} mm"
    )


# =========================================================
# 8. ESCENARIOS RECHAZADOS
# =========================================================

print()
print("REJECTED SCENARIOS")
print("=" * 100)


for scenario in result.rejected_scenarios:

    print(
        f"{scenario.irrigation_mm} mm"
    )


# =========================================================
# 9. RANKING
# =========================================================

print()
print("RANKING")
print("=" * 100)


for position, item in enumerate(
    result.ranked_scenarios,
    start=1,
):

    print(
        f"#{position}"
        f" | {item.scenario.irrigation_mm} mm"
        f" | score={item.score:.3f}"
        f" | {item.reasons}"
    )


# =========================================================
# 10. TRANSFORMACIONES
# =========================================================

print()
print("TRANSFORMATIONS")
print("=" * 120)


for transformation in (
    result.transformations
):

    print(
        transformation
        .transformation_type
        .value,

        "|",

        transformation
        .affected_scenario,

        "|",

        transformation
        .source_knowledge_id,

        "|",

        transformation
        .reason,
    )


print()
print("=" * 120)
print("REASONING COMPLETED")


print()
print("HUMAN-TWIN DECISION TRACE")
print("=" * 120)

print(
    "Trace ID:",
    trace.trace_id,
)

print(
    "Parcel:",
    trace.parcel_id,
)

print(
    "Evidence IDs:",
    trace.evidence_ids,
)

print(
    "Knowledge IDs:",
    trace.knowledge_ids,
)

print(
    "Conflict IDs:",
    trace.conflict_ids,
)

print(
    "Transformation IDs:",
    trace.transformation_ids,
)


print()
print("FEASIBLE SCENARIOS")

for scenario in trace.feasible_scenarios:

    print(
        "  ",
        scenario,
    )


print()
print("REJECTED SCENARIOS")

for scenario in trace.rejected_scenarios:

    print(
        "  ",
        scenario,
    )


print()
print("RANKING")

for item in trace.ranking:

    print(
        "  ",
        item,
    )


print()
print(
    "PROVISIONAL RECOMMENDATION:"
)

print(
    trace.provisional_recommendation
)


print()
print(
    "FARMER RESPONSE:",
    trace.farmer_response,
)

print(
    "OUTCOME:",
    trace.outcome,
)

print("=" * 120)



accepted_trace = response_engine.register_response(
    trace=deepcopy(trace),
    response_type=DecisionResponseType.ACCEPT,
    rationale="La recomendación es aceptada.",
)

print()
print("ACCEPT RESPONSE")
print("=" * 100)

print(
    accepted_trace.farmer_response
)

print("=" * 100)



modified_trace = response_engine.register_response(
    trace=deepcopy(trace),
    response_type=DecisionResponseType.MODIFY,
    modified_action={
        "irrigation_mm": 10.0
    },
    rationale="Se prefiere una aplicación intermedia.",
)

from datetime import datetime

from engines.outcome_engine import (
    OutcomeEngine,
)

from engines.feedback_engine import (
    FeedbackEngine,
)

from twin.outcome import (
    OutcomeStatus,
)


# =========================================================
# 1. Registrar outcome
# =========================================================

outcome_engine = OutcomeEngine()


modified_trace = (
    outcome_engine.register_outcome(
        trace=modified_trace,

        executed_action={
            "irrigation_mm": 9.6,
        },

        observations={
            "soil_moisture_before": 0.14,
            "soil_moisture_after": 0.21,
            "observation_delay_hours": 6,
        },

        rationale=(
            "El sistema de riego aplicó "
            "9.6 mm de los 10 mm previstos."
        ),

        status=OutcomeStatus.OBSERVED,
    )
)

print()
print("FARMER DECISION")
print("=" * 110)

print(
    "Response:",
    modified_trace.farmer_response.response_type.value,
)

print(
    "Final action:",
    modified_trace.get_final_action(),
)

print(
    "Rationale:",
    modified_trace.farmer_response.rationale,
)

print("=" * 110)


print()
print("DECISION OUTCOME")
print("=" * 110)

print(
    "Outcome ID:",
    modified_trace.outcome.outcome_id,
)

print(
    "Status:",
    modified_trace.outcome.status.value,
)

print(
    "Executed action:",
    modified_trace.outcome.executed_action,
)

print(
    "Observations:",
    modified_trace.outcome.observations,
)

print(
    "Deviation:",
    modified_trace.outcome
    .deviation_from_final_action,
)

print("=" * 110)


feedback_engine = FeedbackEngine()


feedback_evidence = (
    feedback_engine
    .create_observation_evidence(
        trace=modified_trace,

        variable="soil_moisture",

        value=0.21,

        unit="m3/m3",

        source_name="soil-sensor-01",

        observed_at=datetime.now(),

        spatial_scope="parcel-001",

        quality_score=0.95,
    )
)


print()
print("FEEDBACK MACHINE EVIDENCE")
print("=" * 110)

print(
    feedback_evidence
)

print("=" * 110)


modified_trace.outcome.resulting_evidence_ids.append(
    feedback_evidence.evidence_id
)

print(
    "Resulting evidence IDs:",
    modified_trace.outcome
    .resulting_evidence_ids,
)