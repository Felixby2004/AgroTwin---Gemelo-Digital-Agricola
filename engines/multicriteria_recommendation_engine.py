from twin.biophysical import (
    BiophysicalScenarioResult,
)

from twin.farmer_knowledge import (
    FarmerKnowledgeItem,
    FarmerKnowledgeType,
    KnowledgeValidationStatus,
)

from twin.quality_gate import (
    TwinQualityGateResult,
)

from twin.recommendation import (
    RecommendationResult,
    RecommendationStatus,
    ScenarioRecommendationScore,
)

from engines.scenario_decision_metrics_engine import (
    ScenarioDecisionMetricsEngine,
)


class MultiCriteriaRecommendationEngine:

    def __init__(
        self,
        agronomic_weight: float = 0.75,
        marginal_weight: float = 0.15,
        preference_weight: float = 0.10,
    ):

        total = (
            agronomic_weight
            + marginal_weight
            + preference_weight
        )

        if abs(
            total - 1.0
        ) > 1e-9:

            raise ValueError(
                "Recommendation weights "
                "must sum to 1.0."
            )

        self.agronomic_weight = (
            agronomic_weight
        )

        self.marginal_weight = (
            marginal_weight
        )

        self.preference_weight = (
            preference_weight
        )

        self.metrics_engine = (
            ScenarioDecisionMetricsEngine()
        )


    def recommend(
        self,
        scenarios: list[
            BiophysicalScenarioResult
        ],
        farmer_knowledge: list[
            FarmerKnowledgeItem
        ],
        quality_gate: TwinQualityGateResult,
        twin_confidence: float | None,
    ) -> RecommendationResult:

        # =================================================
        # 1. QUALITY GATE
        # =================================================

        if not (
            quality_gate
            .recommendation_allowed
        ):

            return RecommendationResult(
                status=(
                    RecommendationStatus
                    .BLOCKED
                ),

                recommended_scenario=None,

                ranked_scenarios=[],

                recommendation_allowed=False,

                reason=(
                    "Recommendation blocked by "
                    "Twin Quality Gate."
                ),

                metadata={
                    "quality_gate_status":
                        quality_gate
                        .status
                        .value,

                    "blocking_reasons":
                        list(
                            quality_gate
                            .blocking_reasons
                        ),
                },
            )


        # =================================================
        # 2. ESCENARIOS FACTIBLES
        # =================================================

        if not scenarios:

            return RecommendationResult(
                status=(
                    RecommendationStatus
                    .NO_FEASIBLE_SCENARIOS
                ),

                recommended_scenario=None,

                ranked_scenarios=[],

                recommendation_allowed=False,

                reason=(
                    "No feasible irrigation "
                    "scenarios are available."
                ),
            )


        # =================================================
        # 3. MÉTRICAS AGRONÓMICAS
        # =================================================

        metrics = (
            self.metrics_engine.calculate(
                scenarios
            )
        )


        metric_by_irrigation = {
            item.irrigation_mm:
                item
            for item in metrics
        }


        # =================================================
        # 4. NORMALIZAR GANANCIA MARGINAL
        # =================================================

        positive_marginal_values = [
            item.marginal_gain_kg_ha_mm
            for item in metrics
            if (
                item.marginal_gain_kg_ha_mm
                is not None
                and
                item.marginal_gain_kg_ha_mm
                > 0
            )
        ]


        max_marginal = (
            max(
                positive_marginal_values
            )
            if positive_marginal_values
            else None
        )


        # =================================================
        # 5. PREFERENCIAS ACTIVAS
        # =================================================

        active_preferences = [
            item
            for item in farmer_knowledge
            if (
                item.knowledge_type
                == FarmerKnowledgeType.PREFERENCE
                and
                item.validation_status
                == KnowledgeValidationStatus.CONFIRMED
            )
        ]


        # =================================================
        # 6. CONFIANZA DEL TWIN
        # =================================================

        if twin_confidence is None:

            confidence_factor = 0.5

        else:

            confidence_factor = max(
                0.0,
                min(
                    twin_confidence,
                    1.0,
                ),
            )


        # =================================================
        # 7. CALCULAR SCORE FINAL
        # =================================================

        scored = []


        for scenario in scenarios:

            item = metric_by_irrigation[
                scenario.irrigation_mm
            ]


            # ---------------------------------------------
            # AGRONOMIC COMPONENT
            # ---------------------------------------------

            agronomic_component = (
                item.agronomic_score
            )


            # ---------------------------------------------
            # MARGINAL COMPONENT
            # ---------------------------------------------

            if (
                item.marginal_gain_kg_ha_mm
                is not None
                and
                max_marginal is not None
                and
                max_marginal > 0
            ):

                marginal_component = max(
                    0.0,
                    min(
                        item
                        .marginal_gain_kg_ha_mm
                        / max_marginal,
                        1.0,
                    ),
                )

            else:

                marginal_component = 0.0


            # ---------------------------------------------
            # PREFERENCE COMPONENT
            # ---------------------------------------------

            preference_component = (
                self._preference_score(
                    metrics=item,
                    preferences=(
                        active_preferences
                    ),
                )
            )


            # ---------------------------------------------
            # SCORE MULTICRITERIO
            # ---------------------------------------------

            raw_score = (
                self.agronomic_weight
                * agronomic_component

                +

                self.marginal_weight
                * marginal_component

                +

                self.preference_weight
                * preference_component
            )


            # ---------------------------------------------
            # La confianza NO cambia el orden de forma
            # arbitraria; reduce la fuerza de decisión.
            # ---------------------------------------------

            final_score = (
                raw_score
                * confidence_factor
            )


            reasons = [
                (
                    "Agronomic="
                    f"{agronomic_component:.4f}"
                ),

                (
                    "Marginal="
                    f"{marginal_component:.4f}"
                ),

                (
                    "Preference="
                    f"{preference_component:.4f}"
                ),

                (
                    "TwinConfidence="
                    f"{confidence_factor:.4f}"
                ),
            ]


            scored.append(
                ScenarioRecommendationScore(
                    scenario=scenario,

                    metrics=item,

                    agronomic_component=(
                        agronomic_component
                    ),

                    marginal_component=(
                        marginal_component
                    ),

                    preference_component=(
                        preference_component
                    ),

                    confidence_factor=(
                        confidence_factor
                    ),

                    final_score=(
                        final_score
                    ),

                    reasons=reasons,
                )
            )


        # =================================================
        # 8. RANKING
        # =================================================

        scored.sort(
            key=lambda item: (
                item.final_score
            ),
            reverse=True,
        )


        best = scored[0]


        return RecommendationResult(
            status=(
                RecommendationStatus
                .RECOMMENDED
            ),

            recommended_scenario=(
                best.scenario
            ),

            ranked_scenarios=scored,

            recommendation_allowed=True,

            reason=(
                "Scenario selected using "
                "multicriteria agronomic, "
                "marginal-gain, preference "
                "and Twin-confidence scoring."
            ),

            metadata={
                "agronomic_weight":
                    self.agronomic_weight,

                "marginal_weight":
                    self.marginal_weight,

                "preference_weight":
                    self.preference_weight,

                "twin_confidence":
                    twin_confidence,
            },
        )


    def _preference_score(
        self,
        metrics,
        preferences: list[
            FarmerKnowledgeItem
        ],
    ) -> float:

        # =================================================
        # SIN PREFERENCIAS
        #
        # 0.5 representa un efecto neutral:
        # ni beneficia ni penaliza el escenario.
        # =================================================

        if not preferences:
            return 0.5


        scores = []


        for preference in preferences:

            payload = (
                preference.payload
                or {}
            )


            # =================================================
            # 1. OBJETIVO REAL DEL CONTRATO
            # =================================================

            objective = (
                payload.get(
                    "objective"
                )
            )


            # =================================================
            # 2. INTENSIDAD DE LA PREFERENCIA
            #
            # Ejemplo actual:
            # weight = 0.8
            #
            # Se limita siempre a [0, 1].
            # =================================================

            preference_intensity = (
                payload.get(
                    "weight",
                    1.0,
                )
            )

            try:

                preference_intensity = float(
                    preference_intensity
                )

            except (
                TypeError,
                ValueError,
            ):

                preference_intensity = 1.0


            preference_intensity = max(
                0.0,
                min(
                    preference_intensity,
                    1.0,
                ),
            )


            # =================================================
            # 3. CONFIANZA REPORTADA POR EL AGRICULTOR
            #
            # Si no existe, no penalizamos.
            # =================================================

            reported_confidence = (
                preference
                .reported_confidence
            )


            if reported_confidence is None:

                confidence_factor = 1.0

            else:

                confidence_factor = max(
                    0.0,
                    min(
                        float(
                            reported_confidence
                        ),
                        1.0,
                    ),
                )


            effective_intensity = (
                preference_intensity
                * confidence_factor
            )


            # =================================================
            # 4. SCORE OBJETIVO
            # =================================================

            target_score = None


            # -------------------------------------------------
            # WATER SAVING
            # -------------------------------------------------

            if (
                objective
                == "WATER_SAVING"
            ):

                target_score = (
                    metrics
                    .water_saving_score
                )


            # -------------------------------------------------
            # YIELD PRIORITY
            # -------------------------------------------------

            elif (
                objective
                == "YIELD_PRIORITY"
            ):

                target_score = (
                    metrics
                    .yield_preservation_score
                )


            # -------------------------------------------------
            # BALANCED
            # -------------------------------------------------

            elif (
                objective
                == "BALANCED"
            ):

                target_score = (
                    (
                        metrics
                        .water_saving_score
                        +
                        metrics
                        .yield_preservation_score
                    )
                    / 2.0
                )


            # =================================================
            # 5. OBJETIVO DESCONOCIDO
            #
            # No inventamos comportamiento:
            # mantenemos efecto neutral.
            # =================================================

            if target_score is None:

                scores.append(
                    0.5
                )

                continue


            # =================================================
            # 6. APLICAR INTENSIDAD SIN DEJAR QUE LA
            #    PREFERENCIA DOMINE POR COMPLETO
            #
            # Neutral = 0.5
            #
            # intensity = 0:
            #     resultado = 0.5
            #
            # intensity = 1:
            #     resultado = target_score
            #
            # intensity = 0.8:
            #     80 % del efecto solicitado.
            # =================================================

            neutral_score = 0.5


            weighted_score = (
                neutral_score
                +
                effective_intensity
                * (
                    target_score
                    - neutral_score
                )
            )


            weighted_score = max(
                0.0,
                min(
                    weighted_score,
                    1.0,
                ),
            )


            scores.append(
                weighted_score
            )


        # =================================================
        # 7. VARIAS PREFERENCIAS
        #
        # Por ahora usamos promedio.
        # Posteriormente podremos incorporar prioridades.
        # =================================================

        if not scores:

            return 0.5


        return (
            sum(scores)
            / len(scores)
        )