import sys
from pathlib import Path

import streamlit as st

# Agregar la raíz del proyecto al PYTHONPATH
ROOT_DIR = Path(__file__).resolve().parent.parent

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
    
from datetime import date

from engines.scenario import ScenarioEngine
from tests.test_simulation import build_weather_series
from tests.test_water_balance import build_test_state


state = build_test_state()

weather_series = build_weather_series(
    days=7
)

engine = ScenarioEngine()

result = engine.compare_irrigation_scenarios(
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
    ],
    irrigation_day=date(
        2026,
        9,
        8,
    ),
)


print()
print("DIGITAL TWIN - COMPARACIÓN DE ESCENARIOS")
print("=" * 92)

print(
    f"{'ID':<7}"
    f"{'Riego':>10}"
    f"{'Humedad final':>18}"
    f"{'Déficit':>12}"
    f"{'Estrés':>12}"
    f"{'Drenaje':>12}"
)

print("-" * 92)

for scenario in result.scenarios:

    print(
        f"{scenario.scenario_id:<7}"
        f"{scenario.irrigation_mm:>9.1f} "
        f"{scenario.final_soil_moisture_pct:>16.2f}%"
        f"{scenario.final_root_zone_depletion_mm:>12.2f}"
        f"{scenario.final_water_stress_index:>12.2f}"
        f"{scenario.deep_percolation_mm:>12.2f}"
    )

print("=" * 92)