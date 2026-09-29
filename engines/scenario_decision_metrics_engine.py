from twin.biophysical import (
    BiophysicalScenarioResult,
)

from twin.scenario_decision import (
    ScenarioDecisionMetrics,
)


class ScenarioDecisionMetricsEngine:

    def calculate(
        self,
        scenarios: list[
            BiophysicalScenarioResult
        ],
    ) -> list[
        ScenarioDecisionMetrics
    ]:

        if not scenarios:
            return []

        ordered = sorted(
            scenarios,
            key=lambda item: (
                item.irrigation_mm
            ),
        )

        max_irrigation = max(
            item.irrigation_mm
            for item in ordered
        )

        max_yield = max(
            item.dry_yield_t_ha
            for item in ordered
        )

        results = []

        previous = None

        for scenario in ordered:

            # -----------------------------------------
            # WATER PRODUCTIVITY
            # -----------------------------------------

            if scenario.irrigation_mm > 0:

                water_productivity = (
                    scenario.dry_yield_t_ha
                    * 1000.0
                    / scenario.irrigation_mm
                )

            else:

                water_productivity = None


            # -----------------------------------------
            # MARGINAL GAIN
            # -----------------------------------------

            marginal_yield_gain = None
            marginal_gain_per_mm = None

            if previous is not None:

                delta_yield_kg_ha = (
                    scenario.dry_yield_t_ha
                    - previous.dry_yield_t_ha
                ) * 1000.0

                delta_irrigation = (
                    scenario.irrigation_mm
                    - previous.irrigation_mm
                )

                marginal_yield_gain = (
                    delta_yield_kg_ha
                )

                if delta_irrigation > 0:

                    marginal_gain_per_mm = (
                        delta_yield_kg_ha
                        / delta_irrigation
                    )


            # -----------------------------------------
            # NORMALIZED SCORES
            # -----------------------------------------

            yield_preservation_score = (
                scenario.dry_yield_t_ha
                / max_yield
                if max_yield > 0
                else 0.0
            )

            water_saving_score = (
                1.0
                - (
                    scenario.irrigation_mm
                    / max_irrigation
                )
                if max_irrigation > 0
                else 1.0
            )

            # -----------------------------------------
            # IRRIGATION EFFICIENCY
            #
            # Premia una combinación de:
            # - rendimiento preservado
            # - menor uso de agua
            # -----------------------------------------

            irrigation_efficiency_score = (
                0.70
                * yield_preservation_score
                +
                0.30
                * water_saving_score
            )


            # -----------------------------------------
            # AGRONOMIC SCORE BASE
            #
            # Todavía no incorpora preferencias.
            # -----------------------------------------

            agronomic_score = (
                0.75
                * yield_preservation_score
                +
                0.25
                * irrigation_efficiency_score
            )


            results.append(
                ScenarioDecisionMetrics(
                    irrigation_mm=(
                        scenario.irrigation_mm
                    ),

                    yield_ratio=(
                        scenario.yield_ratio
                    ),

                    dry_yield_t_ha=(
                        scenario.dry_yield_t_ha
                    ),

                    potential_yield_t_ha=(
                        getattr(
                            scenario,
                            "potential_yield_t_ha",
                            None,
                        )
                    ),

                    water_productivity_kg_ha_mm=(
                        water_productivity
                    ),

                    marginal_yield_gain_kg_ha=(
                        marginal_yield_gain
                    ),

                    marginal_gain_kg_ha_mm=(
                        marginal_gain_per_mm
                    ),

                    irrigation_efficiency_score=(
                        irrigation_efficiency_score
                    ),

                    yield_preservation_score=(
                        yield_preservation_score
                    ),

                    water_saving_score=(
                        water_saving_score
                    ),

                    agronomic_score=(
                        agronomic_score
                    ),
                )
            )

            previous = scenario

        return results