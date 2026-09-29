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


client = SoilGridsWCSClient()

try:

    xml = client.get_capabilities(
        "sand"
    )

except SoilGridsWCSError as exc:

    print()
    print("ERROR SOILGRIDS WCS")
    print("=" * 80)
    print(exc)
    print("=" * 80)

    raise SystemExit(1)


print()
print("SOILGRIDS WCS CAPABILITIES")
print("=" * 80)

for line in xml.splitlines():
    if "CoverageId" in line:
        print(line.strip())

print()
print("=" * 80)