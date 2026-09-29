import sys
from pathlib import Path

# Agregar la raíz del proyecto al PYTHONPATH
ROOT_DIR = Path(__file__).resolve().parent.parent

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

    
from integrations.soilgrids_wcs import (
    SoilGridsWCSClient,
)


client = SoilGridsWCSClient()

xml = client.describe_coverage(
    property_name="sand",
    depth_top_cm=0,
    depth_bottom_cm=5,
)

print()
print("SOILGRIDS DESCRIBE COVERAGE")
print("=" * 80)

for line in xml.splitlines():

    if (
        "Envelope" in line
        or "axisLabels" in line
        or "srsName" in line
        or "lowerCorner" in line
        or "upperCorner" in line
    ):
        print(line.strip())

print("=" * 80)