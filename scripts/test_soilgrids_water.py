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


client = SoilGridsWCSClient(
    timeout_seconds=90,
)


def show_result(result):

    print(
        f"{result.property_name:<10}"
        f"{result.depth_top_cm:>3}-"
        f"{result.depth_bottom_cm:<3} cm"
        f" | raw={result.raw_value}"
        f" | convertido={result.converted_value}"
        f" | método={result.sampling_method}"
        f" | distancia={result.distance_pixels}"
    )


print()
print("PROPIEDADES HÍDRICAS SOILGRIDS")
print("=" * 110)

for property_name in [
    "wv0033",
    "wv1500",
]:

    for top, bottom in client.DEPTHS:

        try:

            result = client.get_value(
                property_name=property_name,
                depth_top_cm=top,
                depth_bottom_cm=bottom,
                latitude=-6.77,
                longitude=-79.84,
            )

            show_result(
                result
            )

        except SoilGridsWCSError as exc:

            print(
                f"ERROR {property_name} "
                f"{top}-{bottom} cm: "
                f"{exc}"
            )

print("=" * 110)