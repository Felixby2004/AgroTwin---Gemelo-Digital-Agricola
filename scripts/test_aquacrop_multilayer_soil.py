import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(
        0,
        str(ROOT_DIR),
    )


from engines.aquacrop_engine import (
    AquaCropEngine,
)

from integrations.soilgrids_wcs import (
    SoilGridsWCSClient,
)


LATITUDE = -6.77
LONGITUDE = -79.84


print()
print("DESCARGANDO PERFIL SOILGRIDS...")
print("=" * 120)


client = SoilGridsWCSClient(
    timeout_seconds=90
)

profile = client.get_soil_profile(
    latitude=LATITUDE,
    longitude=LONGITUDE,
)


print(
    f"Capas SoilGrids: "
    f"{len(profile.layers)}"
)


# ---------------------------------------------------------
# Construcción AquaCrop
# ---------------------------------------------------------

engine = AquaCropEngine()

aqua_soil = (
    engine
    .build_aquacrop_soil_from_profile(
        profile
    )
)


# ---------------------------------------------------------
# Diagnóstico
# ---------------------------------------------------------

print()
print("PERFIL AQUACROP MULTICAPA")
print("=" * 140)

columns = [
    "Comp",
    "Layer",
    "dz",
    "dzsum",
    "th_wp",
    "th_fc",
    "th_s",
    "Ksat",
    "penetrability",
]

available_columns = [
    column
    for column in columns
    if column in aqua_soil.profile.columns
]

print(
    aqua_soil.profile[
        available_columns
    ].to_string(
        index=False
    )
)

print("=" * 140)


print()
print(
    "Profundidad total:",
    f"{aqua_soil.zSoil:.2f} m",
)

print(
    "Número de compartimentos:",
    aqua_soil.nComp,
)

print(
    "Número de capas:",
    aqua_soil.nLayer,
)