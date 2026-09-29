import sys
from pathlib import Path
from datetime import date

ROOT_DIR = Path(__file__).resolve().parent.parent

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from engines.aquacrop_scenario import (
    AquaCropScenarioEngine,
)
from integrations.nasa_power import NASAPowerClient
from twin import Soil
from integrations.soilgrids_wcs import SoilGridsWCSClient


LATITUDE = -6.77
LONGITUDE = -79.84
ELEVATION_M = 30.0

SIM_START = date(2025, 1, 1)
SIM_END = date(2025, 6, 30)

PLANTING_DATE = date(2025, 1, 15)

IRRIGATION_DATE = date(2025, 3, 1)

# ---------------------------------------------------------
# Clima
# ---------------------------------------------------------

print()
print("DESCARGANDO NASA POWER...")
print("=" * 100)

nasa = NASAPowerClient()

weather = nasa.get_daily_weather(
    latitude=LATITUDE,
    longitude=LONGITUDE,
    start_date=SIM_START,
    end_date=SIM_END,
)

weather = nasa.add_et0(
    weather_series=weather,
    latitude=LATITUDE,
    elevation_m=ELEVATION_M,
)

print(
    f"Clima disponible: {len(weather)} días"
)


print()
print("DESCARGANDO PERFIL SOILGRIDS...")
print("=" * 100)

soilgrids_client = SoilGridsWCSClient(
    timeout_seconds=90
)

soil_profile = soilgrids_client.get_soil_profile(
    latitude=LATITUDE,
    longitude=LONGITUDE,
)

max_depth_cm = max(
    layer.depth_bottom_cm
    for layer in soil_profile.layers
)

assert len(soil_profile.layers) == 6
assert max_depth_cm == 200

print(
    f"Perfil SoilGrids: "
    f"{len(soil_profile.layers)} capas"
)

print(
    f"Profundidad máxima: "
    f"{max_depth_cm} cm"
)

# ---------------------------------------------------------
# Suelo
# ---------------------------------------------------------

soil = Soil(
    soil_type=None,

    sand_pct=61.37,
    silt_pct=18.95,
    clay_pct=19.68,

    field_capacity=0.252,
    wilting_point=0.096,

    saturation=None,

    bulk_density_g_cm3=1.35,

    root_zone_depth_m=0.30,
)


# ---------------------------------------------------------
# Escenarios
# ---------------------------------------------------------

irrigation_options = [
    0,
    20,
    40,
    60,
]

scenario_engine = (
    AquaCropScenarioEngine()
)

comparison = (
    scenario_engine
    .compare_irrigation_amounts(
        irrigation_amounts_mm=irrigation_options,

        irrigation_date=IRRIGATION_DATE,

        weather_series=weather,

        soil=soil,
        soil_profile=soil_profile,

        crop_name="Maíz",
        planting_date=PLANTING_DATE,

        simulation_start_date=SIM_START,
        simulation_end_date=SIM_END,

        initial_soil_moisture=0.22,

        organic_carbon_g_kg=19.95,
    )
)

df = comparison.to_dataframe()

biophysical_results = (
    comparison.to_biophysical()
)

print()
print("BIOPHYSICAL RESULTS")
print("=" * 100)

for item in biophysical_results:
    print(item)

print("=" * 100)

print()
print("AQUACROP SCENARIO ENGINE")
print("=" * 140)

print(
    df.to_string(
        index=False
    )
)

print("=" * 140)
