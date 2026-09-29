from logging.config import fileConfig

from alembic import context

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from database.config import (
    DATABASE_URL,
)

from database.base import (
    Base,
)

import database.models


config = context.config


# =========================================================
# DATABASE URL
# =========================================================

config.set_main_option(
    "sqlalchemy.url",
    DATABASE_URL,
)


# =========================================================
# LOGGING
# =========================================================

if config.config_file_name is not None:

    fileConfig(
        config.config_file_name
    )


# =========================================================
# SQLALCHEMY METADATA
# =========================================================

target_metadata = (
    Base.metadata
)


# =========================================================
# IGNORAR OBJETOS INTERNOS DE POSTGIS
# =========================================================

POSTGIS_INTERNAL_TABLES = {
    "spatial_ref_sys",
    "geography_columns",
    "geometry_columns",
    "raster_columns",
    "raster_overviews",

    # postgis_tiger_geocoder
    "direction_lookup",
    "secondary_unit_lookup",
    "state_lookup",
    "street_type_lookup",
    "place_lookup",
    "county_lookup",
    "county",
    "state",
    "zip_lookup",
    "zip_lookup_all",
    "zip_state",
    "zip_state_loc",
    "loader_lookuptables",
    "loader_platform",
    "loader_variables",
}


# =========================================================
# SOLO TABLAS ADMINISTRADAS POR LA APLICACIÓN
# =========================================================

APPLICATION_TABLES = {
    "parcels",
    "machine_evidence",
    "farmer_knowledge",
    "decision_traces",
    "data_consents",
    "data_audit_events",
    "users",
    "parcel_memberships",
    "sensors",
}


def include_object(
    object_,
    name,
    type_,
    reflected,
    compare_to,
):

    # -----------------------------------------------------
    # TABLAS
    # -----------------------------------------------------

    if type_ == "table":

        return (
            name in APPLICATION_TABLES
        )

    # -----------------------------------------------------
    # ÍNDICES, COLUMNAS, FK, ETC.
    #
    # Solo se procesan si pertenecen a una tabla
    # administrada por nuestra aplicación.
    # -----------------------------------------------------

    parent = getattr(
        object_,
        "table",
        None,
    )

    if parent is not None:

        return (
            parent.name
            in APPLICATION_TABLES
        )

    return True


# =========================================================
# OFFLINE MIGRATIONS
# =========================================================

def run_migrations_offline():

    url = config.get_main_option(
        "sqlalchemy.url"
    )

    context.configure(
        url=url,

        target_metadata=(
            target_metadata
        ),

        literal_binds=True,

        dialect_opts={
            "paramstyle":
                "named"
        },

        compare_type=True,

        include_object=include_object,
    )

    with context.begin_transaction():

        context.run_migrations()


# =========================================================
# ONLINE MIGRATIONS
# =========================================================

def run_migrations_online():

    connectable = (
        engine_from_config(
            config.get_section(
                config.config_ini_section
            ),

            prefix="sqlalchemy.",

            poolclass=(
                pool.NullPool
            ),
        )
    )


    with connectable.connect() as connection:

        context.configure(
            connection=connection,

            target_metadata=(
                target_metadata
            ),

            compare_type=True,

            include_object=include_object,
        )


        with context.begin_transaction():

            context.run_migrations()


# =========================================================
# ENTRY POINT
# =========================================================

if context.is_offline_mode():

    run_migrations_offline()

else:

    run_migrations_online()
