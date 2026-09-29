import sys
from pathlib import Path

# Agregar la raíz del proyecto al PYTHONPATH
ROOT_DIR = Path(__file__).resolve().parent.parent

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


from datetime import date

from integrations.nasa_power import (
    NASAPowerClient,
)


client = NASAPowerClient()

weather_series = client.get_daily_weather(
    latitude=-6.77,
    longitude=-79.84,
    start_date=date(2026, 8, 1),
    end_date=date(2026, 8, 7),
)

weather_series = client.add_et0(
    weather_series=weather_series,
    latitude=-6.77,
    elevation_m=30.0,
)

def fmt(value, decimals=2):
    if value is None:
        return "N/D"
    return f"{value:.{decimals}f}"

print()
print("NASA POWER")
print("=" * 100)

print(
    f"{'Fecha':<12}"
    f"{'T media':>12}"
    f"{'T min':>12}"
    f"{'T max':>12}"
    f"{'HR':>10}"
    f"{'Lluvia':>12}"
    f"{'Viento':>12}"
    f"{'Radiación':>14}"
    f"{'ET0':>10}"
)

print("-" * 100)

for weather in weather_series:

    print(
        f"{weather.timestamp.date()!s:<12}"
        f"{fmt(weather.temperature_c):>12}"
        f"{fmt(weather.temperature_min_c):>12}"
        f"{fmt(weather.temperature_max_c):>12}"
        f"{fmt(weather.relative_humidity_pct, 1):>10}"
        f"{fmt(weather.rainfall_mm):>12}"
        f"{fmt(weather.wind_speed_m_s):>12}"
        f"{fmt(weather.solar_radiation_mj_m2_day):>14}"
        f"{fmt(weather.et0_mm_day):>10}"
    )

print("=" * 100)