from dataclasses import dataclass

import pandas as pd

from engines.aquacrop_engine import (
    AquaCropEngine,
)

from twin.biophysical import (
    BiophysicalScenarioResult,
)


@dataclass
class AquaCropScenarioResult:
    irrigation_mm: float
    actual_irrigation_mm: float

    dry_yield_t_ha: float
    yield_potential_t_ha: float

    yield_gain_t_ha: float
    yield_ratio: float

    deep_percolation_mm: float
    transpiration_mm: float
    soil_evaporation_mm: float

    marginal_yield_gain_t_ha: float | None = None
    marginal_gain_kg_ha_mm: float | None = None

    def to_biophysical(
        self,
    ) -> BiophysicalScenarioResult:

        return BiophysicalScenarioResult(
            irrigation_mm=self.irrigation_mm,

            dry_yield_t_ha=self.dry_yield_t_ha,

            yield_potential_t_ha=(
                self.yield_potential_t_ha
            ),

            yield_ratio=self.yield_ratio,

            transpiration_mm=(
                self.transpiration_mm
            ),

            soil_evaporation_mm=(
                self.soil_evaporation_mm
            ),

            deep_percolation_mm=(
                self.deep_percolation_mm
            ),

            marginal_gain_kg_ha_mm=(
                self.marginal_gain_kg_ha_mm
            ),
        )


@dataclass
class AquaCropScenarioComparison:
    scenarios: list[AquaCropScenarioResult]

    def to_dataframe(
        self,
    ) -> pd.DataFrame:

        return pd.DataFrame(
            [
                vars(scenario)
                for scenario
                in self.scenarios
            ]
        )

    def to_biophysical(
        self,
    ) -> list[BiophysicalScenarioResult]:

        return [
            scenario.to_biophysical()
            for scenario in self.scenarios
        ]

class AquaCropScenarioEngine:

    def __init__(
        self,
        aquacrop_engine: AquaCropEngine | None = None,
    ):

        self.aquacrop_engine = (
            aquacrop_engine
            or AquaCropEngine()
        )


    def compare_irrigation_amounts(
        self,
        *,
        irrigation_amounts_mm: list[float],
        irrigation_date,

        weather_series,
        soil,
        soil_profile,

        crop_name,
        planting_date,

        simulation_start_date,
        simulation_end_date,

        initial_soil_moisture,

        organic_carbon_g_kg=None,
    ) -> AquaCropScenarioComparison:

        if not irrigation_amounts_mm:
            raise ValueError(
                "irrigation_amounts_mm no puede estar vacío."
            )

        irrigation_amounts = sorted(
            set(
                float(value)
                for value
                in irrigation_amounts_mm
            )
        )

        if irrigation_amounts[0] < 0:
            raise ValueError(
                "El riego no puede ser negativo."
            )

        raw_results = []

        for irrigation_mm in irrigation_amounts:

            schedule = {}

            if irrigation_mm > 0:
                schedule = {
                    irrigation_date:
                        irrigation_mm
                }

            result = (
                self.aquacrop_engine.simulate(
                    weather_series=weather_series,

                    soil=soil,
                    soil_profile=soil_profile,

                    crop_name=crop_name,
                    planting_date=planting_date,

                    simulation_start_date=(
                        simulation_start_date
                    ),

                    simulation_end_date=(
                        simulation_end_date
                    ),

                    initial_soil_moisture=(
                        initial_soil_moisture
                    ),

                    irrigation_schedule=schedule,

                    organic_carbon_g_kg=(
                        organic_carbon_g_kg
                    ),
                )
            )

            final = (
                result
                .final_stats
                .iloc[0]
            )

            valid_flux = (
                result
                .water_flux[
                    result.water_flux[
                        "time_step_counter"
                    ] > 0
                ]
            )

            raw_results.append(
                {
                    "irrigation_mm":
                        irrigation_mm,

                    "actual_irrigation_mm":
                        float(
                            valid_flux[
                                "IrrDay"
                            ].sum()
                        ),

                    "dry_yield_t_ha":
                        float(
                            final[
                                "Dry yield (tonne/ha)"
                            ]
                        ),

                    "yield_potential_t_ha":
                        float(
                            final[
                                "Yield potential (tonne/ha)"
                            ]
                        ),

                    "deep_percolation_mm":
                        float(
                            valid_flux[
                                "DeepPerc"
                            ].sum()
                        ),

                    "transpiration_mm":
                        float(
                            valid_flux[
                                "Tr"
                            ].sum()
                        ),

                    "soil_evaporation_mm":
                        float(
                            valid_flux[
                                "Es"
                            ].sum()
                        ),
                }
            )

        baseline = raw_results[0][
            "dry_yield_t_ha"
        ]

        scenarios = []

        previous = None

        for item in raw_results:

            yield_gain = (
                item["dry_yield_t_ha"]
                - baseline
            )

            yield_ratio = (
                item["dry_yield_t_ha"]
                /
                item["yield_potential_t_ha"]
            )

            marginal_yield_gain = None
            marginal_gain_kg_ha_mm = None

            if previous is not None:

                delta_yield = (
                    item["dry_yield_t_ha"]
                    -
                    previous["dry_yield_t_ha"]
                )

                delta_water = (
                    item["irrigation_mm"]
                    -
                    previous["irrigation_mm"]
                )

                marginal_yield_gain = (
                    delta_yield
                )

                if delta_water > 0:

                    marginal_gain_kg_ha_mm = (
                        delta_yield
                        * 1000.0
                        / delta_water
                    )

            scenarios.append(
                AquaCropScenarioResult(
                    irrigation_mm=(
                        item["irrigation_mm"]
                    ),

                    actual_irrigation_mm=(
                        item[
                            "actual_irrigation_mm"
                        ]
                    ),

                    dry_yield_t_ha=(
                        item["dry_yield_t_ha"]
                    ),

                    yield_potential_t_ha=(
                        item[
                            "yield_potential_t_ha"
                        ]
                    ),

                    yield_gain_t_ha=(
                        yield_gain
                    ),

                    yield_ratio=(
                        yield_ratio
                    ),

                    deep_percolation_mm=(
                        item[
                            "deep_percolation_mm"
                        ]
                    ),

                    transpiration_mm=(
                        item[
                            "transpiration_mm"
                        ]
                    ),

                    soil_evaporation_mm=(
                        item[
                            "soil_evaporation_mm"
                        ]
                    ),

                    marginal_yield_gain_t_ha=(
                        marginal_yield_gain
                    ),

                    marginal_gain_kg_ha_mm=(
                        marginal_gain_kg_ha_mm
                    ),
                )
            )

            previous = item

        return AquaCropScenarioComparison(
            scenarios=scenarios
        )