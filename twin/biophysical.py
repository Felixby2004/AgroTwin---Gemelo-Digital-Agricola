from dataclasses import dataclass


@dataclass
class BiophysicalScenarioResult:
    irrigation_mm: float

    soil_water_deficit_mm: float | None = None
    projected_soil_moisture: float | None = None

    dry_yield_t_ha: float | None = None
    yield_potential_t_ha: float | None = None
    yield_ratio: float | None = None

    transpiration_mm: float | None = None
    soil_evaporation_mm: float | None = None
    deep_percolation_mm: float | None = None

    marginal_gain_kg_ha_mm: float | None = None