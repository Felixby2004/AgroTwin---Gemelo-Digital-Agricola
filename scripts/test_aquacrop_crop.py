import sys
from pathlib import Path

import streamlit as st

# Agregar la raíz del proyecto al PYTHONPATH
ROOT_DIR = Path(__file__).resolve().parent.parent

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
    

from datetime import date

from engines.aquacrop_engine import (
    AquaCropEngine,
)


engine = AquaCropEngine()

for crop_name in [
    "Maíz",
    "Tomate",
    "Papa",
    "Arroz",
]:

    crop = engine.build_aquacrop_crop(
        crop_name=crop_name,
        planting_date=date(
            2026,
            7,
            1,
        ),
    )

    print(
        crop_name,
        "->",
        crop.Name,
        "| planting:",
        crop.planting_date,
    )