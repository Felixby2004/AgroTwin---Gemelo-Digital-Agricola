from twin.biophysical import (
    BiophysicalScenarioResult,
)

from twin.evidence import (
    MachineEvidence,
)

from twin.farmer_knowledge import (
    FarmerKnowledgeItem,
    FarmerKnowledgeType,
)

from twin.reasoning import (
    ReasoningResult,
)

from engines.knowledge_reasoner import (
    KnowledgeReasoner,
)

from engines.conflict_engine import (
    ConflictEngine,
)

from engines.constraint_engine import (
    ConstraintEngine,
)

from engines.preference_ranker import (
    PreferenceRanker,
)

from engines.evidence_policy_engine import (
    EvidencePolicyEngine,
)

from engines.trusted_state_engine import (
    TrustedStateEngine,
)

from engines.twin_quality_gate_engine import (
    TwinQualityGateEngine,
)

from engines.multicriteria_recommendation_engine import (
    MultiCriteriaRecommendationEngine,
)

from engines.decision_risk_engine import (
    DecisionRiskEngine,
)

class ReasoningOrchestrator:

    def __init__(
        self,
        knowledge_reasoner: KnowledgeReasoner | None = None,
        conflict_engine: ConflictEngine | None = None,
        constraint_engine: ConstraintEngine | None = None,
        preference_ranker: PreferenceRanker | None = None,
    ):

        self.knowledge_reasoner = (
            knowledge_reasoner
            or KnowledgeReasoner()
        )

        self.conflict_engine = (
            conflict_engine
            or ConflictEngine()
        )

        self.constraint_engine = (
            constraint_engine
            or ConstraintEngine()
        )

        self.preference_ranker = (
            preference_ranker
            or PreferenceRanker()
        )

        self.evidence_policy_engine = (
            EvidencePolicyEngine()
        )

        self.trusted_state_engine = (
            TrustedStateEngine(
                policy_engine=(
                    self.evidence_policy_engine
                )
            )
        )

        self.quality_gate_engine = (
            TwinQualityGateEngine()
        )

        self.recommendation_engine = (
            MultiCriteriaRecommendationEngine()
        )

        self.decision_risk_engine = (
            DecisionRiskEngine()
        )


    def run(
        self,
        scenarios: list[
            BiophysicalScenarioResult
        ],
        evidence: list[
            MachineEvidence
        ],
        farmer_knowledge: list[
            FarmerKnowledgeItem
        ],
    ) -> ReasoningResult:


        # =====================================================
        # 1. EVIDENCE POLICY
        # =====================================================

        policy_decisions = (
            self.evidence_policy_engine
            .evaluate_all(
                evidence
            )
        )


        operational_evidence = []

        excluded_evidence_ids = []


        for item, decision in zip(
            evidence,
            policy_decisions,
        ):

            if decision.usable_for_reasoning:

                operational_evidence.append(
                    item
                )

            else:

                excluded_evidence_ids.append(
                    item.evidence_id
                )


        # =====================================================
        # 2. TRUSTED TWIN STATE
        # =====================================================

        trusted_state = (
            self.trusted_state_engine.build(
                evidence
            )
        )

        # =====================================================
        # 3. TWIN QUALITY GATE
        # =====================================================

        quality_gate = (
            self.quality_gate_engine.evaluate(
                trusted_state
            )
        )

        recommendation_allowed = (
            quality_gate.recommendation_allowed
        )


        operational_evidence_ids = [
            item.evidence_id
            for item in operational_evidence
        ]


        update_required_variables = list(
            trusted_state
            .update_required_variables
        )

        # -------------------------------------------------
        # 4. Preservar escenarios originales
        # -------------------------------------------------

        original_scenarios = list(
            scenarios
        )

        # -------------------------------------------------
        # 5. Interpretar conocimiento humano
        # -------------------------------------------------

        knowledge_effects = []

        for knowledge in farmer_knowledge:

            effects = (
                self.knowledge_reasoner.reason(
                    knowledge
                )
            )

            knowledge_effects.extend(
                effects
            )

        # -------------------------------------------------
        # 6. Detectar conflictos humano-máquina
        # -------------------------------------------------

        conflicts = []

        for machine_item in operational_evidence:

            for knowledge in farmer_knowledge:

                conflict = (
                    self.conflict_engine
                    .detect_human_machine_conflict(
                        evidence=machine_item,
                        knowledge=knowledge,
                    )
                )

                if conflict is not None:

                    conflicts.append(
                        conflict
                    )

        # -------------------------------------------------
        # 7. Separar restricciones y preferencias
        # -------------------------------------------------

        constraints = [
            item
            for item in farmer_knowledge
            if (
                item.knowledge_type
                == FarmerKnowledgeType.CONSTRAINT
            )
        ]

        preferences = [
            item
            for item in farmer_knowledge
            if (
                item.knowledge_type
                == FarmerKnowledgeType.PREFERENCE
            )
        ]

        # -------------------------------------------------
        # 8. Aplicar restricciones
        # -------------------------------------------------

        constraint_result = (
            self.constraint_engine.apply(
                scenarios=original_scenarios,
                constraints=constraints,
            )
        )

        # -------------------------------------------------
        # 9. Aplicar preferencias al conjunto factible
        # -------------------------------------------------

        ranking_result = (
            self.preference_ranker.rank(
                scenarios=(
                    constraint_result
                    .feasible_scenarios
                ),
                preferences=preferences,
            )
        )

        # -------------------------------------------------
        # 10. Consolidar transformaciones
        # -------------------------------------------------

        transformations = (
            constraint_result.transformations
            +
            ranking_result.transformations
        )


        # =====================================================
        # RECOMENDACIÓN MULTICRITERIO
        # =====================================================

        soil_water = (
            trusted_state.get(
                "soil_water_state"
            )
        )

        twin_confidence = (
            soil_water.confidence.confidence_score
            if soil_water is not None
            else None
        )


        recommendation_result = (
            self.recommendation_engine.recommend(
                scenarios=(
                    constraint_result.feasible_scenarios
                ),

                farmer_knowledge=farmer_knowledge,

                quality_gate=quality_gate,

                twin_confidence=twin_confidence,
            )
        )


        # =====================================================
        # RIESGO DE DECISIÓN
        # =====================================================

        decision_risk = (
            self.decision_risk_engine.evaluate(
                quality_gate=quality_gate,

                twin_confidence=twin_confidence,

                conflict_count=len(
                    conflicts
                ),
            )
        )

        # -------------------------------------------------
        # 11. Resultado completo
        # -------------------------------------------------

        return ReasoningResult(
            original_scenarios=(
                original_scenarios
            ),

            feasible_scenarios=(
                constraint_result
                .feasible_scenarios
            ),

            rejected_scenarios=(
                constraint_result
                .rejected_scenarios
            ),

            ranked_scenarios=(
                ranking_result
                .ranked_scenarios
            ),

            knowledge_effects=(
                knowledge_effects
            ),

            conflicts=conflicts,

            constraint_evaluations=(
                constraint_result
                .evaluations
            ),

            transformations=(
                transformations
            ),

            trusted_state=trusted_state,

            operational_evidence_ids=(
                operational_evidence_ids
            ),

            excluded_evidence_ids=(
                excluded_evidence_ids
            ),

            update_required_variables=(
                update_required_variables
            ),

            quality_gate=quality_gate,

            recommendation_allowed=(
                recommendation_allowed
            ),

            recommendation_result=(
                recommendation_result
            ),

            decision_risk=(
                decision_risk
            ),
        )