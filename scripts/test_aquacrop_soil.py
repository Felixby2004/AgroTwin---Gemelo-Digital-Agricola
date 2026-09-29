import sys
from pathlib import Path

import streamlit as st

# Agregar la raíz del proyecto al PYTHONPATH
ROOT_DIR = Path(__file__).resolve().parent.parent

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
    

from engines.aquacrop_engine import (
    AquaCropEngine,
)

from twin import Soil


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


engine = AquaCropEngine()

aqua_soil = (
    engine.build_aquacrop_soil(
        soil=soil,
        organic_carbon_g_kg=19.95,
    )
)


print()
print("AQUACROP CUSTOM SOIL")
print("=" * 100)

print(
    aqua_soil.profile[
        [
            "Layer",
            "dz",
            "dzsum",
            "th_wp",
            "th_fc",
            "th_s",
            "Ksat",
            "penetrability",
        ]
    ].to_string(
        index=False
    )
)

print("=" * 100)