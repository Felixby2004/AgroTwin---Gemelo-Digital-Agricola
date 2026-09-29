from dataclasses import dataclass


@dataclass
class ScenarioDecisionMetrics:

    irrigation_mm: float

    yield_ratio: float

    dry_yield_t_ha: float

    potential_yield_t_ha: float | None

    water_productivity_kg_ha_mm: float | None

    marginal_yield_gain_kg_ha: float | None

    marginal_gain_kg_ha_mm: float | None

    irrigation_efficiency_score: float

    yield_preservation_score: float

    water_saving_score: float

    agronomic_score: float