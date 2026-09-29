import sys
from pathlib import Path
from datetime import date

# ---------------------------------------------------------
# Agregar raíz del proyecto al PYTHONPATH
# ---------------------------------------------------------

ROOT_DIR = Path(__file__).resolve().parent.parent

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


# ---------------------------------------------------------
# Imports del proyecto
# ---------------------------------------------------------

from engines.aquacrop_engine import AquaCropEngine
from integrations.nasa_power import NASAPowerClient
from twin import Soil


# ---------------------------------------------------------
# Configuración
# ---------------------------------------------------------

LATITUDE = -6.77
LONGITUDE = -79.84
ELEVATION_M = 30.0

SIM_START = date(
    2025,
    1,
    1,
)

SIM_END = date(
    2025,
    6,
    30,
)

PLANTING_DATE = date(
    2025,
    1,
    15,
)


# ---------------------------------------------------------
# 1. Descargar clima NASA POWER
# ---------------------------------------------------------

print()
print("DESCARGANDO CLIMA NASA POWER...")
print("=" * 100)

nasa_client = NASAPowerClient()

weather_series = nasa_client.get_daily_weather(
    latitude=LATITUDE,
    longitude=LONGITUDE,
    start_date=SIM_START,
    end_date=SIM_END,
)

weather_series = nasa_client.add_et0(
    weather_series=weather_series,
    latitude=LATITUDE,
    elevation_m=ELEVATION_M,
)

print(
    f"Clima cargado: {len(weather_series)} días"
)


# ---------------------------------------------------------
# 2. Definir suelo
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
# 3. Ejecutar AquaCrop
# ---------------------------------------------------------

engine = AquaCropEngine()

print()
print("EJECUTANDO AQUACROP...")
print("=" * 100)

result = engine.simulate(
    weather_series=weather_series,

    soil=soil,

    crop_name="Maíz",

    planting_date=PLANTING_DATE,

    simulation_start_date=SIM_START,
    simulation_end_date=SIM_END,

    initial_soil_moisture=0.22,

    # IMPORTANTE:
    # escenario secano, sin riego programado
    irrigation_schedule={},

    organic_carbon_g_kg=19.95,
)


# ---------------------------------------------------------
# 4. Estadísticas finales
# ---------------------------------------------------------

print()
print("AQUACROP FINAL STATS")
print("=" * 120)

print(
    result.final_stats.to_string(
        index=False
    )
)

print("=" * 120)


# ---------------------------------------------------------
# 5. Filtrar únicamente filas válidas
# ---------------------------------------------------------

valid_water_flux = result.water_flux[
    result.water_flux[
        "time_step_counter"
    ] > 0
].copy()

valid_water_storage = result.water_storage[
    result.water_storage[
        "time_step_counter"
    ] > 0
].copy()

valid_crop_growth = result.crop_growth[
    result.crop_growth[
        "time_step_counter"
    ] > 0
].copy()


# ---------------------------------------------------------
# 6. Water Flux
# ---------------------------------------------------------

print()
print("WATER FLUX - ÚLTIMOS 10 DÍAS VÁLIDOS")
print("=" * 120)

print(
    valid_water_flux.tail(
        10
    ).to_string(
        index=False
    )
)

print("=" * 120)


# ---------------------------------------------------------
# 7. Water Storage
# ---------------------------------------------------------

print()
print("WATER STORAGE - ÚLTIMOS 10 DÍAS VÁLIDOS")
print("=" * 120)

print(
    valid_water_storage.tail(
        10
    ).to_string(
        index=False
    )
)

print("=" * 120)


# ---------------------------------------------------------
# 8. Crop Growth
# ---------------------------------------------------------

print()
print("CROP GROWTH - ÚLTIMOS 10 DÍAS VÁLIDOS")
print("=" * 120)

print(
    valid_crop_growth.tail(
        10
    ).to_string(
        index=False
    )
)

print("=" * 120)


# ---------------------------------------------------------
# 9. Diagnóstico de riego realmente aplicado
# ---------------------------------------------------------

irrigation_days = valid_water_flux[
    valid_water_flux[
        "IrrDay"
    ] > 0
].copy()

print()
print("DÍAS CON RIEGO REALMENTE APLICADO")
print("=" * 120)

if irrigation_days.empty:

    print(
        "No se aplicó riego."
    )

    total_irrigation_mm = 0.0

else:

    print(
        irrigation_days[
            [
                "time_step_counter",
                "dap",
                "IrrDay",
                "Infl",
                "DeepPerc",
            ]
        ].to_string(
            index=False
        )
    )

    total_irrigation_mm = float(
        irrigation_days[
            "IrrDay"
        ].sum()
    )

print()
print(
    "Riego acumulado según water_flux:",
    f"{total_irrigation_mm:.2f} mm",
)

print("=" * 120)


# ---------------------------------------------------------
# 10. Diagnóstico de filas
# ---------------------------------------------------------

print()
print("DIAGNÓSTICO DE SALIDAS")
print("=" * 120)

print(
    "Filas water_flux:",
    len(result.water_flux),
)

print(
    "Filas válidas water_flux:",
    len(valid_water_flux),
)

print(
    "Filas water_storage:",
    len(result.water_storage),
)

print(
    "Filas válidas water_storage:",
    len(valid_water_storage),
)

print(
    "Filas crop_growth:",
    len(result.crop_growth),
)

print(
    "Filas válidas crop_growth:",
    len(valid_crop_growth),
)

print("=" * 120)