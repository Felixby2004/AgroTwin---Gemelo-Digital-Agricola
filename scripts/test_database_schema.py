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
    inspect,
    text,
)

from database.session import (
    engine,
)


print()
print(
    "DATABASE SCHEMA TEST"
)

print("=" * 100)


inspector = inspect(
    engine
)


tables = sorted(
    inspector.get_table_names()
)


print(
    "TABLES:"
)


for table in tables:

    print(
        " -",
        table
    )


required_tables = {
    "parcels",
    "machine_evidence",
    "farmer_knowledge",
    "decision_traces",
    "alembic_version",
}


missing = (
    required_tables
    - set(tables)
)


print("-" * 100)


if missing:

    print(
        "MISSING TABLES:",
        sorted(
            missing
        )
    )

    raise RuntimeError(
        "Database schema is incomplete."
    )


with engine.connect() as connection:

    postgis = connection.execute(
        text(
            """
            SELECT EXISTS (
                SELECT 1
                FROM pg_extension
                WHERE extname = 'postgis'
            );
            """
        )
    ).scalar()


print(
    "POSTGIS ENABLED:",
    postgis,
)


if not postgis:

    raise RuntimeError(
        "PostGIS extension is not enabled."
    )


print("=" * 100)

print(
    "DATABASE SCHEMA: OK"
)