from dataclasses import dataclass

from engines.scenario import (
    IrrigationScenario,
    ScenarioComparisonResult,
)


@dataclass
class RecommendationResult:
    recommended_irrigation_mm: float

    selected_scenario_id: str

    decision_type: str

    technical_status: str

    reason_codes: list[str]

    final_soil_moisture_pct: float

    final_root_zone_depletion_mm: float

    final_water_stress_index: float

    deep_percolation_mm: float

    selected_scenario: IrrigationScenario

    @property
    def irrigation_required(self) -> bool:
        return self.recommended_irrigation_mm > 0

    @property
    def is_fully_acceptable(self) -> bool:
        return self.decision_type in {
            "NO_IRRIGATION_REQUIRED",
            "ACCEPTABLE_MINIMUM_WATER",
        }

    def to_dict(self) -> dict:
        return {
            "recommended_irrigation_mm": (
                self.recommended_irrigation_mm
            ),
            "selected_scenario_id": (
                self.selected_scenario_id
            ),
            "decision_type": self.decision_type,
            "technical_status": self.technical_status,
            "reason_codes": self.reason_codes,
            "final_soil_moisture_pct": (
                self.final_soil_moisture_pct
            ),
            "final_root_zone_depletion_mm": (
                self.final_root_zone_depletion_mm
            ),
            "final_water_stress_index": (
                self.final_water_stress_index
            ),
            "deep_percolation_mm": (
                self.deep_percolation_mm
            ),
        }


class RecommendationEngine:
    """
    Recomendador técnico inicial del gemelo digital.

    Estrategia:

    1. Evitar estrés hídrico excesivo.
    2. Evitar drenaje profundo significativo.
    3. Entre escenarios técnicamente aceptables,
       utilizar la menor cantidad posible de agua.
    4. Si ninguno es completamente aceptable,
       seleccionar la mejor alternativa disponible
       e informar que se trata de un fallback.
    """

    def __init__(
        self,
        acceptable_stress_threshold: float = 0.30,
        max_deep_percolation_mm: float = 1.0,
    ):
        if not 0 <= acceptable_stress_threshold <= 1:
            raise ValueError(
                "acceptable_stress_threshold debe estar "
                "entre 0 y 1."
            )

        if max_deep_percolation_mm < 0:
            raise ValueError(
                "max_deep_percolation_mm no puede "
                "ser negativo."
            )

        self.acceptable_stress_threshold = (
            acceptable_stress_threshold
        )

        self.max_deep_percolation_mm = (
            max_deep_percolation_mm
        )

    def recommend(
        self,
        comparison: ScenarioComparisonResult,
    ) -> RecommendationResult:

        if not comparison.scenarios:
            raise ValueError(
                "No existen escenarios para evaluar."
            )

        acceptable = [
            scenario
            for scenario in comparison.scenarios
            if self._is_acceptable(scenario)
        ]

        # Caso 1:
        # El escenario sin riego ya es suficiente.
        zero_irrigation = [
            scenario
            for scenario in acceptable
            if scenario.irrigation_mm == 0
        ]

        if zero_irrigation:
            selected = zero_irrigation[0]

            return self._build_result(
                scenario=selected,
                decision_type=(
                    "NO_IRRIGATION_REQUIRED"
                ),
                reason_codes=[
                    "CURRENT_STATE_ACCEPTABLE",
                    "IRRIGATION_NOT_REQUIRED",
                    "WATER_SAVING",
                ],
            )

        # Caso 2:
        # Hay varios escenarios aceptables.
        # Seleccionamos el que utilice menos agua.
        if acceptable:
            selected = min(
                acceptable,
                key=lambda scenario: (
                    scenario.irrigation_mm,
                    scenario.deep_percolation_mm,
                    scenario.final_water_stress_index,
                ),
            )

            return self._build_result(
                scenario=selected,
                decision_type=(
                    "ACCEPTABLE_MINIMUM_WATER"
                ),
                reason_codes=[
                    "WATER_STRESS_CONTROLLED",
                    "DEEP_PERCOLATION_ACCEPTABLE",
                    "MINIMUM_ACCEPTABLE_IRRIGATION",
                ],
            )

        # Caso 3:
        # Ningún escenario cumple completamente
        # los criterios.
        selected = self._select_best_available(
            comparison.scenarios
        )

        reason_codes = [
            "NO_FULLY_ACCEPTABLE_SCENARIO",
            "BEST_AVAILABLE_SCENARIO",
        ]

        if (
            selected.final_water_stress_index
            >
            self.acceptable_stress_threshold
        ):
            reason_codes.append(
                "RESIDUAL_WATER_STRESS"
            )

        if (
            selected.deep_percolation_mm
            >
            self.max_deep_percolation_mm
        ):
            reason_codes.append(
                "DEEP_PERCOLATION_RISK"
            )

        return self._build_result(
            scenario=selected,
            decision_type="BEST_AVAILABLE",
            reason_codes=reason_codes,
        )

    def _is_acceptable(
        self,
        scenario: IrrigationScenario,
    ) -> bool:

        stress_ok = (
            scenario.final_water_stress_index
            <= self.acceptable_stress_threshold
        )

        percolation_ok = (
            scenario.deep_percolation_mm
            <= self.max_deep_percolation_mm
        )

        return stress_ok and percolation_ok

    def _select_best_available(
        self,
        scenarios: list[IrrigationScenario],
    ) -> IrrigationScenario:
        """
        Fallback cuando ningún escenario satisface
        todos los criterios.

        Prioridades:

        1. menor estrés,
        2. menor drenaje,
        3. menor cantidad de agua.
        """

        return min(
            scenarios,
            key=lambda scenario: (
                scenario.final_water_stress_index,
                scenario.deep_percolation_mm,
                scenario.irrigation_mm,
            ),
        )

    def _build_result(
        self,
        scenario: IrrigationScenario,
        decision_type: str,
        reason_codes: list[str],
    ) -> RecommendationResult:

        return RecommendationResult(
            recommended_irrigation_mm=(
                scenario.irrigation_mm
            ),

            selected_scenario_id=(
                scenario.scenario_id
            ),

            decision_type=decision_type,

            technical_status=(
                scenario.technical_status
            ),

            reason_codes=reason_codes,

            final_soil_moisture_pct=(
                scenario.final_soil_moisture_pct
            ),

            final_root_zone_depletion_mm=(
                scenario.final_root_zone_depletion_mm
            ),

            final_water_stress_index=(
                scenario.final_water_stress_index
            ),

            deep_percolation_mm=(
                scenario.deep_percolation_mm
            ),

            selected_scenario=scenario,
        )