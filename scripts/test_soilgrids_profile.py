import sys
from pathlib import Path

# Agregar la raíz del proyecto al PYTHONPATH
ROOT_DIR = Path(__file__).resolve().parent.parent

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


from integrations.soilgrids_wcs import (
    SoilGridsWCSClient,
    SoilGridsWCSError,
)


client = SoilGridsWCSClient(
    timeout_seconds=90,
)

try:

    profile = client.get_soil_profile(
        latitude=-6.77,
        longitude=-79.84,
    )

except SoilGridsWCSError as exc:

    print()
    print("ERROR SOILGRIDS WCS")
    print("=" * 100)
    print(exc)
    print("=" * 100)

    raise SystemExit(1)


print()
print("SOILGRIDS WCS PROFILE")
print("=" * 110)

print(
    f"{'Profundidad':<15}"
    f"{'Arena %':>12}"
    f"{'Limo %':>12}"
    f"{'Arcilla %':>12}"
    f"{'Densidad':>14}"
    f"{'SOC':>12}"
    f"{'pH':>10}"
    f"{'WV33 %':>12}"
    f"{'WV1500 %':>12}"
)

print("-" * 110)

for layer in profile.layers:

    depth = (
        f"{layer.depth_top_cm}-"
        f"{layer.depth_bottom_cm} cm"
    )

    def fmt(value):
        if value is None:
            return "N/D"
        return f"{value:.2f}"

    print(
        f"{depth:<15}"
        f"{fmt(layer.sand_pct):>12}"
        f"{fmt(layer.silt_pct):>12}"
        f"{fmt(layer.clay_pct):>12}"
        f"{fmt(layer.bulk_density_g_cm3):>14}"
        f"{fmt(layer.organic_carbon_g_kg):>12}"
        f"{fmt(layer.ph_h2o):>10}"
        f"{fmt(layer.water_content_33kpa_pct):>12}"
        f"{fmt(layer.water_content_1500kpa_pct):>12}"
    )

print("=" * 110)

summary = profile.summarize(
    max_depth_cm=30
)

print()
print("RESUMEN PONDERADO 0-30 cm")
print("=" * 70)

print(
    "Arena:",
    (
        f"{summary.sand_pct:.2f}%"
        if summary.sand_pct is not None
        else "N/D"
    ),
)

print(
    "Limo:",
    (
        f"{summary.silt_pct:.2f}%"
        if summary.silt_pct is not None
        else "N/D"
    ),
)

print(
    "Arcilla:",
    (
        f"{summary.clay_pct:.2f}%"
        if summary.clay_pct is not None
        else "N/D"
    ),
)

print(
    "Densidad:",
    (
        f"{summary.bulk_density_g_cm3:.2f} g/cm³"
        if summary.bulk_density_g_cm3 is not None
        else "N/D"
    ),
)

print(
    "SOC:",
    (
        f"{summary.organic_carbon_g_kg:.2f} g/kg"
        if summary.organic_carbon_g_kg is not None
        else "N/D"
    ),
)

print(
    "pH:",
    (
        f"{summary.ph_h2o:.2f}"
        if summary.ph_h2o is not None
        else "N/D"
    ),
)

print(
    "WV33:",
    fmt(
        summary.water_content_33kpa_pct
    ),
    "%",
)

print(
    "WV1500:",
    fmt(
        summary.water_content_1500kpa_pct
    ),
    "%",
)

print("=" * 70)