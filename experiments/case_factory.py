from dataclasses import dataclass
from datetime import datetime, timedelta

from twin.biophysical import (
    BiophysicalScenarioResult,
)

from twin.evidence import (
    MachineEvidence,
    EvidenceStatus,
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

from twin.experiment import (
    ExperimentCondition,
)


@dataclass
class ExperimentalCase:
    condition: ExperimentCondition

    scenarios: list[
        BiophysicalScenarioResult
    ]

    evidence: list[
        MachineEvidence
    ]

    farmer_knowledge: list[
        FarmerKnowledgeItem
    ]


class ExperimentalCaseFactory:

    def build(
        self,
        condition: ExperimentCondition,
    ) -> ExperimentalCase:

        now = datetime.now()

        scenarios = (
            self._build_scenarios()
        )

        if (
            condition
            == ExperimentCondition.COMPLETE
        ):
            return self._build_complete(
                now=now,
                scenarios=scenarios,
            )

        if (
            condition
            == ExperimentCondition.MISSING_STALE
        ):
            return self._build_missing_stale(
                now=now,
                scenarios=scenarios,
            )

        if (
            condition
            == ExperimentCondition.CONFLICT
        ):
            return self._build_conflict(
                now=now,
                scenarios=scenarios,
            )

        raise ValueError(
            f"Condición experimental "
            f"no soportada: {condition}"
        )


    # =====================================================
    # ESCENARIOS COMUNES
    # =====================================================

    def _build_scenarios(
        self,
    ) -> list[BiophysicalScenarioResult]:

        return [

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


    # =====================================================
    # CONOCIMIENTO HUMANO COMÚN
    # =====================================================

    def _build_constraint(
        self,
        now: datetime,
    ) -> FarmerKnowledgeItem:

        return FarmerKnowledgeItem(
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
                "Disponibilidad máxima de "
                "20 mm para la decisión actual."
            ),
        )


    def _build_preference(
        self,
        now: datetime,
    ) -> FarmerKnowledgeItem:

        return FarmerKnowledgeItem(
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
        )


    # =====================================================
    # COMPLETE
    # =====================================================

    def _build_complete(
        self,
        now: datetime,
        scenarios: list[
            BiophysicalScenarioResult
        ],
    ) -> ExperimentalCase:

        evidence = [

            MachineEvidence(
                evidence_id="EV-SM-COMPLETE",

                variable="soil_water_state",

                value={
                    "soil_moisture": 0.21,
                    "interpretation": "ADEQUATE",
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

                status=EvidenceStatus.ACTIVE,

                quality_score=0.95,
            ),
        ]

        farmer_knowledge = [
            self._build_constraint(
                now
            ),

            self._build_preference(
                now
            ),
        ]

        return ExperimentalCase(
            condition=(
                ExperimentCondition.COMPLETE
            ),

            scenarios=scenarios,

            evidence=evidence,

            farmer_knowledge=farmer_knowledge,
        )


    # =====================================================
    # MISSING / STALE
    # =====================================================

    def _build_missing_stale(
        self,
        now: datetime,
        scenarios: list[
            BiophysicalScenarioResult
        ],
    ) -> ExperimentalCase:

        stale_time = (
            now - timedelta(hours=72)
        )

        evidence = [

            MachineEvidence(
                evidence_id="EV-SM-STALE",

                variable="soil_water_state",

                value={
                    "soil_moisture": 0.18,
                    "interpretation": "LOW",
                },

                unit=None,

                observed_at=stale_time,

                provenance=ProvenanceRecord(
                    source_type=(
                        EvidenceSourceType.MEASURED
                    ),

                    source_name="soil-sensor-01",

                    generated_at=stale_time,

                    valid_at=stale_time,

                    spatial_scope="parcel-001",

                    metadata={
                        "age_hours": 72,
                    },
                ),

                status=EvidenceStatus.STALE,

                quality_score=0.70,
            ),
        ]

        observation = FarmerKnowledgeItem(
            knowledge_id="FK-OBS-MISSING-001",

            knowledge_type=(
                FarmerKnowledgeType.OBSERVATION
            ),

            source_id="farmer-001",
            source_role="FARMER",

            payload={
                "observation": (
                    "El cultivo presenta marchitez "
                    "moderada esta mañana."
                ),

                "severity": "MODERATE",
            },

            created_at=now,

            spatial_scope="parcel-001",

            reported_confidence=0.85,

            validation_status=(
                KnowledgeValidationStatus.UNVERIFIED
            ),

            affects=[
                "crop_water_stress",
            ],
        )

        farmer_knowledge = [
            observation,

            self._build_constraint(
                now
            ),

            self._build_preference(
                now
            ),
        ]

        return ExperimentalCase(
            condition=(
                ExperimentCondition.MISSING_STALE
            ),

            scenarios=scenarios,

            evidence=evidence,

            farmer_knowledge=farmer_knowledge,
        )


    # =====================================================
    # CONFLICT
    # =====================================================

    def _build_conflict(
        self,
        now: datetime,
        scenarios: list[
            BiophysicalScenarioResult
        ],
    ) -> ExperimentalCase:

        evidence = [

            MachineEvidence(
                evidence_id="EV-SM-CONFLICT",

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

                status=EvidenceStatus.ACTIVE,

                quality_score=0.95,
            ),
        ]

        event = FarmerKnowledgeItem(
            knowledge_id="FK-EVT-CONFLICT-001",

            knowledge_type=(
                FarmerKnowledgeType.EVENT
            ),

            source_id="farmer-001",
            source_role="FARMER",

            payload={
                "event_type": "IRRIGATION",

                "amount_mm": 15.0,

                "occurred_at": (
                    now
                    - timedelta(hours=12)
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

        local_knowledge = FarmerKnowledgeItem(
            knowledge_id="FK-LOCAL-CONFLICT-001",

            knowledge_type=(
                FarmerKnowledgeType.LOCAL_KNOWLEDGE
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
                KnowledgeValidationStatus.UNVERIFIED
            ),

            affects=[
                "soil_water_retention",
            ],
        )

        farmer_knowledge = [
            event,

            self._build_constraint(
                now
            ),

            self._build_preference(
                now
            ),

            local_knowledge,
        ]

        return ExperimentalCase(
            condition=(
                ExperimentCondition.CONFLICT
            ),

            scenarios=scenarios,

            evidence=evidence,

            farmer_knowledge=farmer_knowledge,
        )