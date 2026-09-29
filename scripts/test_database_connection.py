import sys
from pathlib import Path


ROOT_DIR = (
    Path(__file__)
    .resolve()
    .parent
    .parent
)

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(
        0,
        str(ROOT_DIR),
    )


from sqlalchemy import (
    text,
)

from database.session import (
    engine,
)


print()
print(
    "DATABASE CONNECTION TEST"
)

print("=" * 80)


with engine.connect() as connection:

    version = connection.execute(
        text(
            "SELECT version();"
        )
    ).scalar()


    postgis = connection.execute(
        text(
            "SELECT PostGIS_Version();"
        )
    ).scalar()


    print(
        "POSTGRESQL:",
        version,
    )

    print(
        "POSTGIS:",
        postgis,
    )


print("=" * 80)

print(
    "DATABASE CONNECTION: OK"
)