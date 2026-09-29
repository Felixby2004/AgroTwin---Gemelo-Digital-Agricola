from dataclasses import dataclass
from datetime import date

from engines.simulation import (
    TemporalSimulationResult,
    TemporalSimulator,
)
from tests.test_simulation import build_weather_series
from twin import TwinState, WeatherState


@dataclass
class IrrigationScenario:
    scenario_id: str
    irrigation_mm: float
    irrigation_day: date

    final_soil_moisture: float
    final_root_zone_depletion_mm: float
    final_water_stress_index: float

    total_etc_mm: float
    total_rainfall_mm: float
    total_irrigation_mm: float

    deep_percolation_mm: float

    simulation: TemporalSimulationResult

    @property
    def final_soil_moisture_pct(self) -> float:
        return self.final_soil_moisture * 100

    @property
    def has_water_stress(self) -> bool:
        return self.final_water_stress_index > 0

    @property
    def has_severe_water_stress(self) -> bool:
        return self.final_water_stress_index >= 0.70

    @property
    def has_deep_percolation(self) -> bool:
        return self.deep_percolation_mm > 0

    @property
    def technical_status(self) -> str:

        if self.deep_percolation_mm > 1.0:
            return "EXCESS"

        if self.final_water_stress_index >= 0.70:
            return "SEVERE_STRESS"

        if self.final_water_stress_index >= 0.30:
            return "MODERATE_STRESS"

        return "ACCEPTABLE"


@dataclass
class ScenarioComparisonResult:
    scenarios: list[IrrigationScenario]

    @property
    def scenario_count(self) -> int:
        return len(self.scenarios)

    def get_by_irrigation(
        self,
        irrigation_mm: float,
    ) -> IrrigationScenario | None:

        for scenario in self.scenarios:
            if scenario.irrigation_mm == irrigation_mm:
                return scenario

        return None

    def to_dicts(self) -> list[dict]:
        return [
            {
                "scenario_id": scenario.scenario_id,
                "irrigation_mm": scenario.irrigation_mm,
                "irrigation_day": scenario.irrigation_day,
                "final_soil_moisture_pct": (
                    scenario.final_soil_moisture_pct
                ),
                "root_zone_depletion_mm": (
                    scenario.final_root_zone_depletion_mm
                ),
                "water_stress_index": (
                    scenario.final_water_stress_index
                ),
                "total_etc_mm": scenario.total_etc_mm,
                "total_rainfall_mm": (
                    scenario.total_rainfall_mm
                ),
                "deep_percolation_mm": (
                    scenario.deep_percolation_mm
                ),
                "technical_status": (
                    scenario.technical_status
                ),
            }
            for scenario in self.scenarios
        ]


    def acceptable_scenarios(
        self,
    ) -> list[IrrigationScenario]:

        return [
            scenario
            for scenario in self.scenarios
            if scenario.technical_status
            == "ACCEPTABLE"
        ]


    def scenarios_without_percolation(
        self,
    ) -> list[IrrigationScenario]:

        return [
            scenario
            for scenario in self.scenarios
            if not scenario.has_deep_percolation
        ]




class ScenarioEngine:
    """
    Motor para comparar alternativas de riego.

    Cada escenario parte exactamente del mismo TwinState
    y de la misma serie meteorológica.
    """

    def __init__(
        self,
        simulator: TemporalSimulator | None = None,
    ):
        self.simulator = simulator or TemporalSimulator()

    def compare_irrigation_scenarios(
        self,
        initial_state: TwinState,
        weather_series: list[WeatherState],
        irrigation_options_mm: list[float],
        irrigation_day: date | None = None,
        irrigation_efficiency: float = 0.85,
        rainfall_efficiency: float = 0.90,
    ) -> ScenarioComparisonResult:

        if not weather_series:
            raise ValueError(
                "weather_series no puede estar vacío."
            )

        if not irrigation_options_mm:
            raise ValueError(
                "irrigation_options_mm no puede estar vacío."
            )

        if any(
            irrigation_mm < 0
            for irrigation_mm in irrigation_options_mm
        ):
            raise ValueError(
                "Las cantidades de riego no pueden ser negativas."
            )

        weather_series = sorted(
            weather_series,
            key=lambda weather: weather.timestamp,
        )

        if irrigation_day is None:
            irrigation_day = (
                weather_series[0].timestamp.date()
            )

        available_days = {
            weather.timestamp.date()
            for weather in weather_series
        }

        if irrigation_day not in available_days:
            raise ValueError(
                "irrigation_day debe pertenecer al período simulado."
            )

        scenarios: list[IrrigationScenario] = []

        for index, irrigation_mm in enumerate(
            irrigation_options_mm,
            start=1,
        ):

            irrigation_schedule = {}

            if irrigation_mm > 0:
                irrigation_schedule[
                    irrigation_day
                ] = irrigation_mm

            simulation = self.simulator.simulate(
                initial_state=initial_state,
                weather_series=weather_series,
                irrigation_schedule=irrigation_schedule,
                irrigation_efficiency=(
                    irrigation_efficiency
                ),
                rainfall_efficiency=(
                    rainfall_efficiency
                ),
            )

            final_state = simulation.final_state

            total_deep_percolation = sum(
                record.deep_percolation_mm
                for record in simulation.records
            )

            scenario = IrrigationScenario(
                scenario_id=f"S{index:03d}",
                irrigation_mm=irrigation_mm,
                irrigation_day=irrigation_day,

                final_soil_moisture=(
                    final_state.soil_moisture
                ),

                final_root_zone_depletion_mm=(
                    final_state.root_zone_depletion_mm
                    or 0.0
                ),

                final_water_stress_index=(
                    final_state.water_stress_index
                    or 0.0
                ),

                total_etc_mm=simulation.total_etc_mm,

                total_rainfall_mm=(
                    simulation.total_rainfall_mm
                ),

                total_irrigation_mm=(
                    simulation.total_irrigation_mm
                ),

                deep_percolation_mm=(
                    total_deep_percolation
                ),

                simulation=simulation,
            )

            scenarios.append(scenario)

        return ScenarioComparisonResult(
            scenarios=scenarios
        )