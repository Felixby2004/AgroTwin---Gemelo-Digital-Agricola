import sys
from pathlib import Path

import streamlit as st

# Agregar la raíz del proyecto al PYTHONPATH
ROOT_DIR = Path(__file__).resolve().parent.parent

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
    

from datetime import date

from engines.aquacrop_engine import (
    AquaCropEngine,
)

from integrations.nasa_power import (
    NASAPowerClient,
)


latitude = -6.77
longitude = -79.84
elevation_m = 30.0


nasa = NASAPowerClient()

weather_series = nasa.get_daily_weather(
    latitude=latitude,
    longitude=longitude,
    start_date=date(
        2026,
        8,
        2,
    ),
    end_date=date(
        2026,
        8,
        7,
    ),
)

weather_series = nasa.add_et0(
    weather_series=weather_series,
    latitude=latitude,
    elevation_m=elevation_m,
)


engine = AquaCropEngine()

weather_df = engine.map_weather(
    weather_series
)


print()
print("AQUACROP WEATHER DATAFRAME")
print("=" * 90)

print(
    weather_df.to_string(
        index=False
    )
)

print("=" * 90)

print()
print(weather_df.dtypes)