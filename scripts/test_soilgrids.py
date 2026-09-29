import sys
from pathlib import Path

# Agregar la raíz del proyecto al PYTHONPATH
ROOT_DIR = Path(__file__).resolve().parent.parent

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


from integrations.soilgrids import (
    SoilGridsClient,
    SoilGridsError,
)


client = SoilGridsClient()

try:

    profile = client.get_soil_profile(
        latitude=-6.77,
        longitude=-79.84,
    )

except SoilGridsError as exc:

    print()
    print("ERROR SOILGRIDS")
    print("=" * 70)
    print(exc)
    print("=" * 70)

    raise SystemExit(1)


print()
print("SOILGRIDS")
print("=" * 110)

print(
    f"{'Profundidad':<15}"
    f"{'Arena %':>12}"
    f"{'Limo %':>12}"
    f"{'Arcilla %':>12}"
    f"{'Densidad':>14}"
    f"{'SOC':>12}"
    f"{'pH':>10}"
)

print("-" * 110)

for layer in profile.layers:

    depth = (
        f"{layer.depth_top_cm}-"
        f"{layer.depth_bottom_cm} cm"
    )

    print(
        f"{depth:<15}"
        f"{(layer.sand_pct or 0):>12.2f}"
        f"{(layer.silt_pct or 0):>12.2f}"
        f"{(layer.clay_pct or 0):>12.2f}"
        f"{(layer.bulk_density_g_cm3 or 0):>14.2f}"
        f"{(layer.organic_carbon_g_kg or 0):>12.2f}"
        f"{(layer.ph_h2o or 0):>10.2f}"
    )

print("=" * 110)