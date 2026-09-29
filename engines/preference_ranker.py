from dataclasses import dataclass
from datetime import datetime
from uuid import uuid4

from twin.biophysical import (
    BiophysicalScenarioResult,
)

from twin.farmer_knowledge import (
    FarmerKnowledgeItem,
    FarmerKnowledgeType,
    KnowledgeValidationStatus,
)

from twin.scenario_transformation import (
    ScenarioTransformation,
    TransformationType,
)


@dataclass
class RankedScenario:
    scenario: BiophysicalScenarioResult
    score: float
    reasons: list[str]


@dataclass
class PreferenceRankingResult:
    ranked_scenarios: list[RankedScenario]
    transformations: list[ScenarioTransformation]


class PreferenceRanker:

    def rank(
        self,
        scenarios: list[BiophysicalScenarioResult],
        preferences: list[FarmerKnowledgeItem],
    ) -> PreferenceRankingResult:

        # -------------------------------------------------
        # 1. Filtrar únicamente preferencias confirmadas
        # -------------------------------------------------

        active_preferences = [
            item
            for item in preferences
            if (
                item.knowledge_type
                == FarmerKnowledgeType.PREFERENCE
                and item.validation_status
                == KnowledgeValidationStatus.CONFIRMED
            )
        ]

        ranked = []

        # -------------------------------------------------
        # 2. Calcular score de cada escenario
        # -------------------------------------------------

        for scenario in scenarios:

            score = 0.0
            reasons = []

            # ---------------------------------------------
            # Base agronómica
            #
            # Por ahora usamos yield_ratio como componente
            # principal del score.
            # ---------------------------------------------

            if scenario.yield_ratio is not None:

                agronomic_score = (
                    scenario.yield_ratio
                    * 100.0
                )

                score += agronomic_score

                reasons.append(
                    f"Yield ratio="
                    f"{scenario.yield_ratio:.3f}"
                )

            # ---------------------------------------------
            # Preferencias humanas
            # ---------------------------------------------

            for preference in active_preferences:

                payload = preference.payload

                objective = payload.get(
                    "objective"
                )

                weight = float(
                    payload.get(
                        "weight",
                        1.0,
                    )
                )

                # -----------------------------------------
                # Preferencia: ahorro de agua
                # -----------------------------------------

                if objective == "WATER_SAVING":

                    water_penalty = (
                        scenario.irrigation_mm
                        * weight
                    )

                    score -= water_penalty

                    reasons.append(
                        f"WATER_SAVING penalty="
                        f"{water_penalty:.2f}"
                    )

            ranked.append(
                RankedScenario(
                    scenario=scenario,
                    score=score,
                    reasons=reasons,
                )
            )

        # -------------------------------------------------
        # 3. Ordenar de mayor a menor score
        # -------------------------------------------------

        sorted_ranked = sorted(
            ranked,
            key=lambda item: item.score,
            reverse=True,
        )

        # -------------------------------------------------
        # 4. Registrar transformaciones de ranking
        # -------------------------------------------------

        transformations = []

        for position, item in enumerate(
            sorted_ranked,
            start=1,
        ):

            # ---------------------------------------------
            # Identificar qué preferencias participaron
            # ---------------------------------------------

            preference_ids = [
                preference.knowledge_id
                for preference in active_preferences
            ]

            # Si hay una sola preferencia, usamos su ID
            # como fuente principal de la transformación.
            #
            # Si hay varias, dejamos "MULTIPLE_PREFERENCES"
            # y guardamos los IDs en metadata.

            if len(preference_ids) == 1:

                source_knowledge_id = (
                    preference_ids[0]
                )

            elif len(preference_ids) > 1:

                source_knowledge_id = (
                    "MULTIPLE_PREFERENCES"
                )

            else:

                source_knowledge_id = (
                    "SYSTEM_BASE_RANKING"
                )

            transformations.append(
                ScenarioTransformation(
                    transformation_id=(
                        f"TR-"
                        f"{uuid4().hex[:10].upper()}"
                    ),

                    transformation_type=(
                        TransformationType.ACTION_RERANKED
                    ),

                    source_knowledge_id=(
                        source_knowledge_id
                    ),

                    affected_scenario=(
                        f"irrigation_"
                        f"{item.scenario.irrigation_mm}_mm"
                    ),

                    before_value=None,

                    after_value={
                        "rank": position,
                        "score": item.score,
                        "irrigation_mm": (
                            item.scenario.irrigation_mm
                        ),
                    },

                    reason=(
                        "Escenario reordenado considerando "
                        "la base agronómica y las "
                        "preferencias humanas activas."
                    ),

                    created_at=datetime.now(),

                    metadata={
                        "preference_ids":
                            preference_ids,

                        "reasons":
                            item.reasons,

                        "yield_ratio": (
                            item.scenario.yield_ratio
                        ),

                        "irrigation_mm": (
                            item.scenario.irrigation_mm
                        ),
                    },
                )
            )

        # -------------------------------------------------
        # 5. Retornar ranking + trazabilidad
        # -------------------------------------------------

        return PreferenceRankingResult(
            ranked_scenarios=sorted_ranked,
            transformations=transformations,
        )