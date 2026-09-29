import sys
from pathlib import Path

import streamlit as st

# Agregar la raíz del proyecto al PYTHONPATH
ROOT_DIR = Path(__file__).resolve().parent.parent

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


from integrations.soilgrids_wcs import (
    SoilGridsWCSClient,
    SoilGridsWCSError,
)


client = SoilGridsWCSClient()

try:

    result = client.get_value(
        property_name="sand",
        depth_top_cm=0,
        depth_bottom_cm=5,
        latitude=-6.77,
        longitude=-79.84,
    )

except SoilGridsWCSError as exc:

    print()
    print("ERROR SOILGRIDS WCS")
    print("=" * 80)
    print(exc)
    print("=" * 80)

    raise SystemExit(1)


print()
print("SOILGRIDS WCS VALUE")
print("=" * 80)

print(
    "Propiedad:",
    result.property_name,
)

print(
    "Profundidad:",
    f"{result.depth_top_cm}-"
    f"{result.depth_bottom_cm} cm",
)

print(
    "Valor crudo:",
    result.raw_value,
)

print(
    "Valor convertido:",
    result.converted_value,
)

print("=" * 80)


print(
    "Método:",
    result.sampling_method,
)

print(
    "Distancia píxeles:",
    result.distance_pixels,
)