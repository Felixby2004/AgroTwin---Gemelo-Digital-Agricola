import sys
from pathlib import Path

import streamlit as st

# Agregar la raíz del proyecto al PYTHONPATH
ROOT_DIR = Path(__file__).resolve().parent.parent

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from engines.recommendation import (
    RecommendationEngine,
)
from engines.scenario import ScenarioEngine
from tests.test_simulation import build_weather_series
from tests.test_water_balance import build_test_state


state = build_test_state()

weather_series = build_weather_series(
    days=5
)

scenario_engine = ScenarioEngine()

comparison = (
    scenario_engine.compare_irrigation_scenarios(
        initial_state=state,
        weather_series=weather_series,
        irrigation_options_mm=[
            0,
            5,
            10,
            15,
            20,
            25,
            30,
            35,
            40,
            45,
            50,
            60,
            70,
            80,
        ],
    )
)

recommendation_engine = (
    RecommendationEngine()
)

recommendation = (
    recommendation_engine.recommend(
        comparison
    )
)


print()
print("DIGITAL TWIN - RECOMMENDATION ENGINE")
print("=" * 95)

print(
    f"{'ID':<7}"
    f"{'Riego':>10}"
    f"{'Humedad':>14}"
    f"{'Déficit':>12}"
    f"{'Estrés':>12}"
    f"{'Drenaje':>12}"
    f"{'Estado':>20}"
)

print("-" * 95)

for scenario in comparison.scenarios:

    selected = (
        "*"
        if scenario.scenario_id
        == recommendation.selected_scenario_id
        else " "
    )

    print(
        f"{selected}{scenario.scenario_id:<6}"
        f"{scenario.irrigation_mm:>10.1f}"
        f"{scenario.final_soil_moisture_pct:>13.2f}%"
        f"{scenario.final_root_zone_depletion_mm:>12.2f}"
        f"{scenario.final_water_stress_index:>12.2f}"
        f"{scenario.deep_percolation_mm:>12.2f}"
        f"{scenario.technical_status:>20}"
    )

print("=" * 95)

print()
print("RECOMENDACIÓN")
print("-" * 40)

print(
    "Riego recomendado:",
    f"{recommendation.recommended_irrigation_mm:.1f} mm",
)

print(
    "Escenario:",
    recommendation.selected_scenario_id,
)

print(
    "Tipo de decisión:",
    recommendation.decision_type,
)

print(
    "Humedad final estimada:",
    f"{recommendation.final_soil_moisture_pct:.2f}%",
)

print(
    "Déficit final:",
    f"{recommendation.final_root_zone_depletion_mm:.2f} mm",
)

print(
    "Estrés final:",
    f"{recommendation.final_water_stress_index:.2f}",
)

print(
    "Drenaje:",
    f"{recommendation.deep_percolation_mm:.2f} mm",
)

print()
print("RAZONES")

for reason in recommendation.reason_codes:
    print(" -", reason)