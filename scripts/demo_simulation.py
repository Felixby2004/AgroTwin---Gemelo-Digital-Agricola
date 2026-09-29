import sys
from pathlib import Path

# Agregar la raíz del proyecto al PYTHONPATH
ROOT_DIR = Path(__file__).resolve().parent.parent

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from datetime import date

from engines.simulation import TemporalSimulator
from tests.test_simulation import build_weather_series
from tests.test_water_balance import build_test_state


initial_state = build_test_state()

weather_series = build_weather_series(
    days=7
)

irrigation_schedule = {
    date(2026, 9, 10): 20.0,
}

simulator = TemporalSimulator()

result = simulator.simulate(
    initial_state=initial_state,
    weather_series=weather_series,
    irrigation_schedule=irrigation_schedule,
)


print()
print("DIGITAL TWIN - SIMULACIÓN TEMPORAL")
print("=" * 72)

print(
    f"{'Fecha':<12}"
    f"{'Riego':>10}"
    f"{'Lluvia':>10}"
    f"{'ETc':>10}"
    f"{'Humedad':>12}"
    f"{'Déficit':>10}"
    f"{'Estrés':>10}"
)

print("-" * 72)

for record in result.records:

    print(
        f"{record.day!s:<12}"
        f"{record.irrigation_mm:>10.1f}"
        f"{record.rainfall_mm:>10.1f}"
        f"{record.etc_mm:>10.2f}"
        f"{record.final_soil_moisture * 100:>11.2f}%"
        f"{record.root_zone_depletion_mm:>10.2f}"
        f"{record.water_stress_index:>10.2f}"
    )

print("-" * 72)

print(
    "Humedad final:",
    f"{result.final_state.soil_moisture * 100:.2f}%",
)

print(
    "Riego total:",
    f"{result.total_irrigation_mm:.1f} mm",
)

print(
    "ETc total:",
    f"{result.total_etc_mm:.2f} mm",
)