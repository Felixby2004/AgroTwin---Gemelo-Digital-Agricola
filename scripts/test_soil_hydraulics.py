import sys
from pathlib import Path

# Agregar la raíz del proyecto al PYTHONPATH
ROOT_DIR = Path(__file__).resolve().parent.parent

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


from integrations.soilgrids_wcs import (
    SoilGridsWCSClient,
)

from engines.soil_hydraulics import (
    SoilHydraulicEstimator,
)


client = SoilGridsWCSClient(
    timeout_seconds=90,
)

profile = client.get_soil_profile(
    latitude=-6.77,
    longitude=-79.84,
)

estimator = SoilHydraulicEstimator()

hydraulic = estimator.from_soilgrids(
    profile=profile,
    max_depth_cm=30,
)

soil = estimator.build_soil(
    profile=profile,
    root_zone_depth_m=0.30,
)


print()
print("SOIL HYDRAULICS")
print("=" * 80)

print(
    "Field capacity:",
    f"{hydraulic.field_capacity:.3f}",
)

print(
    "Wilting point:",
    f"{hydraulic.wilting_point:.3f}",
)

print(
    "Available water:",
    f"{hydraulic.available_water_capacity:.3f}",
)

print(
    "Fuente:",
    hydraulic.source,
)

print()
print("SOIL GENERADO")
print("=" * 80)

print(
    "Arena:",
    soil.sand_pct,
)

print(
    "Limo:",
    soil.silt_pct,
)

print(
    "Arcilla:",
    soil.clay_pct,
)

print(
    "FC:",
    soil.field_capacity,
)

print(
    "WP:",
    soil.wilting_point,
)

print(
    "Bulk density:",
    soil.bulk_density_g_cm3,
)

print(
    "Root zone:",
    soil.root_zone_depth_m,
)

print("=" * 80)