import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(
        0,
        str(ROOT_DIR),
    )


from integrations.soilgrids_wcs import (
    SoilGridsWCSClient,
)


LATITUDE = -6.77
LONGITUDE = -79.84


client = SoilGridsWCSClient(
    timeout_seconds=90
)

profile = client.get_soil_profile(
    latitude=LATITUDE,
    longitude=LONGITUDE,
)


print()
print("PERFIL SOILGRIDS")
print("=" * 120)

for layer in profile.layers:

    print(
        f"{layer.depth_top_cm:>3}-"
        f"{layer.depth_bottom_cm:<3} cm | "
        f"Arena={layer.sand_pct:6.2f}% | "
        f"Limo={layer.silt_pct:6.2f}% | "
        f"Arcilla={layer.clay_pct:6.2f}% | "
        f"FC≈{layer.water_content_33kpa_pct:6.2f}% | "
        f"WP≈{layer.water_content_1500kpa_pct:6.2f}%"
    )


print("=" * 120)


for depth in [
    30,
    60,
    100,
    200,
]:

    summary = profile.summarize(
        max_depth_cm=depth
    )

    print()
    print(
        f"RESUMEN 0-{depth} cm"
    )

    print(
        f"Arena:   "
        f"{summary.sand_pct:.2f}%"
    )

    print(
        f"Limo:    "
        f"{summary.silt_pct:.2f}%"
    )

    print(
        f"Arcilla: "
        f"{summary.clay_pct:.2f}%"
    )

    print(
        f"WV33:    "
        f"{summary.water_content_33kpa_pct:.2f}%"
    )

    print(
        f"WV1500:  "
        f"{summary.water_content_1500kpa_pct:.2f}%"
    )