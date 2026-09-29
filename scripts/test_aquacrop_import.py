import os

os.environ.setdefault(
    "DEVELOPMENT",
    "DEVELOPMENT",
)

from aquacrop import (
    AquaCropModel,
    Crop,
    InitialWaterContent,
    IrrigationManagement,
    Soil,
)


print()
print("AQUACROP")
print("=" * 80)

print("AquaCropModel:", AquaCropModel)
print("Soil:", Soil)
print("Crop:", Crop)
print(
    "InitialWaterContent:",
    InitialWaterContent,
)
print(
    "IrrigationManagement:",
    IrrigationManagement,
)

print("=" * 80)
print("IMPORTACIÓN CORRECTA")