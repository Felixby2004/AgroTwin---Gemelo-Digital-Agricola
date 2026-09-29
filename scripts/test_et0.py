import sys
from pathlib import Path

# Agregar la raíz del proyecto al PYTHONPATH
ROOT_DIR = Path(__file__).resolve().parent.parent

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


from datetime import date

from engines.et0 import (
    ET0Calculator,
    ET0Input,
)


calculator = ET0Calculator()

data = ET0Input(
    calculation_date=date(
        2026,
        8,
        1,
    ),

    latitude_deg=-6.77,
    elevation_m=30.0,

    temperature_mean_c=25.5,
    temperature_min_c=20.0,
    temperature_max_c=31.0,

    relative_humidity_pct=65.0,

    solar_radiation_mj_m2_day=18.5,

    wind_speed_m_s=2.0,
)

result = calculator.calculate(
    data
)


print()
print("FAO-56 PENMAN-MONTEITH")
print("=" * 60)

print(
    "ET0:",
    f"{result.et0_mm_day:.3f} mm/día",
)

print(
    "Radiación neta:",
    f"{result.net_radiation_mj_m2_day:.3f} MJ/m²/día",
)

print(
    "Presión vapor saturación:",
    f"{result.saturation_vapor_pressure_kpa:.3f} kPa",
)

print(
    "Presión vapor real:",
    f"{result.actual_vapor_pressure_kpa:.3f} kPa",
)

print(
    "Déficit presión vapor:",
    f"{result.vapor_pressure_deficit_kpa:.3f} kPa",
)

print("=" * 60)