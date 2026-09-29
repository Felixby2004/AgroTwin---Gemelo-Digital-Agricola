from dataclasses import dataclass
from datetime import date

from engines.water_balance import (
    WaterBalanceEngine,
    WaterBalanceResult,
)
from twin import TwinState, WeatherState


@dataclass
class DailySimulationRecord:
    day: date

    irrigation_mm: float

    initial_soil_moisture: float
    final_soil_moisture: float

    et0_mm: float
    etc_mm: float

    rainfall_mm: float
    effective_rainfall_mm: float

    effective_irrigation_mm: float

    root_zone_depletion_mm: float
    water_stress_index: float

    deep_percolation_mm: float
    runoff_mm: float


@dataclass
class TemporalSimulationResult:
    initial_state: TwinState
    final_state: TwinState
    records: list[DailySimulationRecord]

    @property
    def days_simulated(self) -> int:
        return len(self.records)

    @property
    def total_irrigation_mm(self) -> float:
        return sum(
            record.irrigation_mm
            for record in self.records
        )

    @property
    def total_rainfall_mm(self) -> float:
        return sum(
            record.rainfall_mm
            for record in self.records
        )

    @property
    def total_etc_mm(self) -> float:
        return sum(
            record.etc_mm
            for record in self.records
        )

    def to_dicts(self) -> list[dict]:
        return [
            {
                "date": record.day,
                "irrigation_mm": record.irrigation_mm,
                "rainfall_mm": record.rainfall_mm,
                "et0_mm": record.et0_mm,
                "etc_mm": record.etc_mm,
                "soil_moisture": (
                    record.final_soil_moisture
                ),
                "soil_moisture_pct": (
                    record.final_soil_moisture * 100
                ),
                "root_zone_depletion_mm": (
                    record.root_zone_depletion_mm
                ),
                "water_stress_index": (
                    record.water_stress_index
                ),
                "deep_percolation_mm": (
                    record.deep_percolation_mm
                ),
            }
            for record in self.records
        ]


class TemporalSimulator:
    """
    Simulador temporal del gemelo digital.

    Evoluciona el TwinState día por día utilizando
    una serie meteorológica y un calendario de riego.
    """

    def __init__(
        self,
        water_balance_engine: WaterBalanceEngine | None = None,
    ):
        self.water_balance_engine = (
            water_balance_engine
            or WaterBalanceEngine()
        )

    def simulate(
        self,
        initial_state: TwinState,
        weather_series: list[WeatherState],
        irrigation_schedule: dict[date, float] | None = None,
        irrigation_efficiency: float = 0.85,
        rainfall_efficiency: float = 0.90,
    ) -> TemporalSimulationResult:

        if not weather_series:
            raise ValueError(
                "weather_series no puede estar vacío."
            )

        irrigation_schedule = irrigation_schedule or {}

        # Ordenar cronológicamente
        weather_series = sorted(
            weather_series,
            key=lambda weather: weather.timestamp,
        )

        current_state = initial_state

        records: list[DailySimulationRecord] = []

        for weather in weather_series:

            simulation_day = weather.timestamp.date()

            irrigation_mm = irrigation_schedule.get(
                simulation_day,
                0.0,
            )

            # Actualizamos el estado con el clima
            # correspondiente al día simulado.
            current_state = current_state.model_copy(
                update={
                    "timestamp": weather.timestamp,
                    "weather": weather,
                }
            )

            balance_result = (
                self.water_balance_engine.step(
                    state=current_state,
                    irrigation_mm=irrigation_mm,
                    irrigation_efficiency=(
                        irrigation_efficiency
                    ),
                    rainfall_efficiency=(
                        rainfall_efficiency
                    ),
                )
            )

            new_state = (
                self.water_balance_engine.update_state(
                    current_state,
                    balance_result,
                )
            )

            days_since_irrigation = (
                self._calculate_days_since_irrigation(
                    current_state=current_state,
                    irrigation_mm=irrigation_mm,
                )
            )

            new_state = new_state.model_copy(
                update={
                    "timestamp": weather.timestamp,
                    "weather": weather,
                    "days_since_irrigation": (
                        days_since_irrigation
                    ),
                }
            )

            records.append(
                self._build_record(
                    simulation_day=simulation_day,
                    irrigation_mm=irrigation_mm,
                    result=balance_result,
                )
            )

            current_state = new_state

        return TemporalSimulationResult(
            initial_state=initial_state,
            final_state=current_state,
            records=records,
        )

    def _calculate_days_since_irrigation(
        self,
        current_state: TwinState,
        irrigation_mm: float,
    ) -> int:

        if irrigation_mm > 0:
            return 0

        if current_state.days_since_irrigation is None:
            return 1

        return current_state.days_since_irrigation + 1

    def _build_record(
        self,
        simulation_day: date,
        irrigation_mm: float,
        result: WaterBalanceResult,
    ) -> DailySimulationRecord:

        return DailySimulationRecord(
            day=simulation_day,

            irrigation_mm=irrigation_mm,

            initial_soil_moisture=(
                result.initial_soil_moisture
            ),

            final_soil_moisture=(
                result.final_soil_moisture
            ),

            et0_mm=result.et0_mm,
            etc_mm=result.etc_mm,

            rainfall_mm=result.rainfall_mm,

            effective_rainfall_mm=(
                result.effective_rainfall_mm
            ),

            effective_irrigation_mm=(
                result.effective_irrigation_mm
            ),

            root_zone_depletion_mm=(
                result.root_zone_depletion_mm
            ),

            water_stress_index=(
                result.water_stress_index
            ),

            deep_percolation_mm=(
                result.deep_percolation_mm
            ),

            runoff_mm=result.runoff_mm,
        )


    def to_dicts(self) -> list[dict]:
        return [
            {
                "date": record.day,
                "irrigation_mm": (
                    record.irrigation_mm
                ),
                "rainfall_mm": (
                    record.rainfall_mm
                ),
                "et0_mm": record.et0_mm,
                "etc_mm": record.etc_mm,
                "soil_moisture": (
                    record.final_soil_moisture
                ),
                "soil_moisture_pct": (
                    record.final_soil_moisture
                    * 100
                ),
                "root_zone_depletion_mm": (
                    record.root_zone_depletion_mm
                ),
                "water_stress_index": (
                    record.water_stress_index
                ),
                "deep_percolation_mm": (
                    record.deep_percolation_mm
                ),
            }
            for record in self.records
        ]