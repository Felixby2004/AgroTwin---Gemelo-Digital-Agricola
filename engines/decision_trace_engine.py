from datetime import datetime
from uuid import uuid4

from twin.decision_trace import (
    HumanTwinDecisionTrace,
)

from twin.evidence import (
    MachineEvidence,
)

from twin.farmer_knowledge import (
    FarmerKnowledgeItem,
)

from twin.reasoning import (
    ReasoningResult,
)


class DecisionTraceEngine:

    def build_trace(
        self,
        reasoning_result: ReasoningResult,
        evidence: list[MachineEvidence],
        farmer_knowledge: list[
            FarmerKnowledgeItem
        ],
        parcel_id: str | None = None,
    ) -> HumanTwinDecisionTrace:

        # -------------------------------------------------
        # Evidencia
        # -------------------------------------------------

        evidence_ids = [
            item.evidence_id
            for item in evidence
        ]

        # -------------------------------------------------
        # Conocimiento humano
        # -------------------------------------------------

        knowledge_ids = [
            item.knowledge_id
            for item in farmer_knowledge
        ]

        # -------------------------------------------------
        # Conflictos
        # -------------------------------------------------

        conflict_ids = [
            conflict.conflict_id
            for conflict
            in reasoning_result.conflicts
        ]

        # -------------------------------------------------
        # Transformaciones
        # -------------------------------------------------

        transformation_ids = [
            transformation.transformation_id
            for transformation
            in reasoning_result.transformations
        ]

        # -------------------------------------------------
        # Escenarios factibles
        # -------------------------------------------------

        feasible_scenarios = [
            {
                "irrigation_mm":
                    scenario.irrigation_mm,

                "dry_yield_t_ha":
                    scenario.dry_yield_t_ha,

                "yield_ratio":
                    scenario.yield_ratio,

                "marginal_gain_kg_ha_mm":
                    scenario.marginal_gain_kg_ha_mm,
            }
            for scenario
            in reasoning_result.feasible_scenarios
        ]

        # -------------------------------------------------
        # Escenarios rechazados
        # -------------------------------------------------

        rejected_scenarios = [
            {
                "irrigation_mm":
                    scenario.irrigation_mm,

                "dry_yield_t_ha":
                    scenario.dry_yield_t_ha,

                "yield_ratio":
                    scenario.yield_ratio,

                "marginal_gain_kg_ha_mm":
                    scenario.marginal_gain_kg_ha_mm,
            }
            for scenario
            in reasoning_result.rejected_scenarios
        ]

        # -------------------------------------------------
        # Ranking
        # -------------------------------------------------

        ranking = []

        for position, item in enumerate(
            reasoning_result.ranked_scenarios,
            start=1,
        ):

            ranking.append(
                {
                    "rank":
                        position,

                    "irrigation_mm":
                        item.scenario.irrigation_mm,

                    "score":
                        item.score,

                    "reasons":
                        item.reasons,
                }
            )

        # =========================================================
        # PROVISIONAL RECOMMENDATION
        #
        # Prioridad:
        # 1. Nuevo MultiCriteriaRecommendationEngine
        # 2. Fallback al ranking antiguo solo por compatibilidad
        # =========================================================

        provisional_recommendation = None


        # ---------------------------------------------------------
        # 1. NUEVO MOTOR MULTICRITERIO
        # ---------------------------------------------------------

        recommendation_result = getattr(
            reasoning_result,
            "recommendation_result",
            None,
        )


        if (
            recommendation_result is not None
            and
            recommendation_result
            .recommendation_allowed
            and
            recommendation_result
            .recommended_scenario
            is not None
        ):

            recommended_scenario = (
                recommendation_result
                .recommended_scenario
            )

            best_score = None
            reasons = []

            if (
                recommendation_result
                .ranked_scenarios
            ):

                best_ranked = (
                    recommendation_result
                    .ranked_scenarios[0]
                )

                best_score = (
                    best_ranked.final_score
                )

                reasons = list(
                    best_ranked.reasons
                )


            provisional_recommendation = {
                "irrigation_mm": (
                    recommended_scenario
                    .irrigation_mm
                ),

                "score": best_score,

                "reasons": reasons,

                "status": "PROVISIONAL",

                "source": (
                    "MULTICRITERIA_RECOMMENDATION"
                ),
            }


        # ---------------------------------------------------------
        # 2. FALLBACK LEGACY
        #
        # Solo para compatibilidad con pruebas o flujos antiguos.
        # ---------------------------------------------------------

        elif (
            recommendation_result is None
            and
            reasoning_result.ranked_scenarios
        ):

            best = (
                reasoning_result
                .ranked_scenarios[0]
            )

            provisional_recommendation = {
                "irrigation_mm":
                    best.scenario.irrigation_mm,

                "score":
                    best.score,

                "reasons":
                    best.reasons,

                "status":
                    "PROVISIONAL",

                "source":
                    "LEGACY_PREFERENCE_RANKER",
            }

        # -------------------------------------------------
        # Crear trace
        # -------------------------------------------------

        return HumanTwinDecisionTrace(
            trace_id=(
                f"TRACE-"
                f"{uuid4().hex[:12].upper()}"
            ),

            created_at=datetime.now(),

            parcel_id=parcel_id,

            evidence_ids=evidence_ids,

            knowledge_ids=knowledge_ids,

            conflict_ids=conflict_ids,

            transformation_ids=(
                transformation_ids
            ),

            feasible_scenarios=(
                feasible_scenarios
            ),

            rejected_scenarios=(
                rejected_scenarios
            ),

            ranking=ranking,

            provisional_recommendation=(
                provisional_recommendation
            ),

            farmer_response=None,

            outcome=None,

            metadata={
                "trace_version": "1.0",
            },
        )