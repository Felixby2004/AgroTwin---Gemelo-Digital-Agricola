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

for property_name in [
    "wv0033",
    "wv1500",
]:

    print()
    print(
        f"SOILGRIDS {property_name.upper()}"
    )
    print("=" * 80)

    try:

        xml = client.get_capabilities(
            property_name
        )

    except SoilGridsWCSError as exc:

        print(exc)
        continue

    for line in xml.splitlines():

        if (
            "CoverageId" in line
            and "_mean" in line
        ):
            print(
                line.strip()
            )