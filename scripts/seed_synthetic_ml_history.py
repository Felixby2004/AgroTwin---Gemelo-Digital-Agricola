from __future__ import annotations

from datetime import (
    datetime,
    timedelta,
    timezone,
)

from pathlib import Path
import sys
import uuid

import numpy as np

# ======================================================
# PROJECT ROOT
# ======================================================

PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parents[1]
)

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(
        0,
        str(PROJECT_ROOT),
    )


from database.session import (
    SessionLocal,
)

from database.models.evidence import (
    MachineEvidenceModel,
)


# ======================================================
# CONFIG
# ======================================================

PARCEL_ID = (
    "b201198e-56b5-422c-8375-82b76a745afe"
)

HOURS = 72

RANDOM_SEED = 42


# ======================================================
# HELPERS
# ======================================================

def evidence_id(
    variable: str,
    timestamp: datetime,
) -> str:

    stamp = timestamp.strftime(
        "%Y%m%d%H"
    )

    return (
        f"SYN-ML-"
        f"{variable.upper()}-"
        f"{stamp}-"
        f"{uuid.uuid4().hex[:6]}"
    )


def provenance_payload() -> dict:

    return {
        "source_type":
            "SYNTHETIC",

        "source_name":
            "Synthetic ML Demo Seeder",

        "description":
            (
                "Synthetic hourly series generated "
                "only for software integration testing."
            ),
    }


# ======================================================
# MAIN
# ======================================================

def main() -> None:

    rng = np.random.default_rng(
        RANDOM_SEED
    )

    end_time = (
        datetime.now(
            timezone.utc
        )
        .replace(
            minute=0,
            second=0,
            microsecond=0,
        )
    )

    start_time = (
        end_time
        - timedelta(
            hours=HOURS - 1
        )
    )


    rows = []


    # ==================================================
    # INITIAL CONDITIONS
    # ==================================================

    soil_moisture = 0.245

    cumulative_rain_effect = 0.0


    for hour_index in range(
        HOURS
    ):

        timestamp = (
            start_time
            + timedelta(
                hours=hour_index
            )
        )


        hour = timestamp.hour


        # ----------------------------------------------
        # AIR TEMPERATURE
        # ----------------------------------------------

        air_temperature = (
            24.0
            + 5.0
            * np.sin(
                2
                * np.pi
                * (
                    hour - 6
                )
                / 24
            )
            + rng.normal(
                0,
                0.4,
            )
        )


        # ----------------------------------------------
        # RELATIVE HUMIDITY
        # ----------------------------------------------

        relative_humidity = (
            62.0
            - 18.0
            * np.sin(
                2
                * np.pi
                * (
                    hour - 6
                )
                / 24
            )
            + rng.normal(
                0,
                2.0,
            )
        )

        relative_humidity = float(
            np.clip(
                relative_humidity,
                25.0,
                95.0,
            )
        )


        # ----------------------------------------------
        # SOLAR RADIATION
        # ----------------------------------------------

        solar_angle = np.sin(
            np.pi
            * (
                hour - 6
            )
            / 12
        )

        solar_radiation = max(
            0.0,
            700.0
            * solar_angle,
        )

        solar_radiation += (
            rng.normal(
                0,
                15,
            )
            if solar_radiation > 0
            else 0
        )

        solar_radiation = max(
            0.0,
            float(
                solar_radiation
            ),
        )


        # ----------------------------------------------
        # RAINFALL
        #
        # Small artificial events.
        # ----------------------------------------------

        rainfall = 0.0

        if hour_index in {
            14,
            15,
            16,
        }:

            rainfall = {
                14: 2.2,
                15: 4.5,
                16: 1.3,
            }[
                hour_index
            ]

        elif hour_index in {
            49,
            50,
        }:

            rainfall = {
                49: 3.4,
                50: 2.1,
            }[
                hour_index
            ]


        # ----------------------------------------------
        # SOIL TEMPERATURE
        # ----------------------------------------------

        soil_temperature = (
            23.0
            + 2.0
            * np.sin(
                2
                * np.pi
                * (
                    hour - 8
                )
                / 24
            )
            + rng.normal(
                0,
                0.2,
            )
        )


        # ----------------------------------------------
        # SYNTHETIC SOIL-WATER DYNAMICS
        # ----------------------------------------------

        cumulative_rain_effect *= 0.82

        cumulative_rain_effect += (
            rainfall
            * 0.0022
        )


        evaporative_loss = (
            0.00045
            + (
                air_temperature
                - 20.0
            )
            * 0.000025
            + solar_radiation
            * 0.00000035
        )


        soil_moisture = (
            soil_moisture
            - evaporative_loss
            + cumulative_rain_effect
            + rng.normal(
                0,
                0.00035,
            )
        )


        soil_moisture = float(
            np.clip(
                soil_moisture,
                0.12,
                0.38,
            )
        )


        # ----------------------------------------------
        # MACHINE EVIDENCE ROWS
        # ----------------------------------------------

        values = {
            "soil_moisture":
                {
                    "soil_moisture":
                        soil_moisture
                },

            "air_temperature":
                {
                    "value":
                        float(
                            air_temperature
                        )
                },

            "rainfall":
                {
                    "value":
                        float(
                            rainfall
                        )
                },

            "solar_radiation":
                {
                    "value":
                        float(
                            solar_radiation
                        )
                },

            "relative_humidity":
                {
                    "value":
                        relative_humidity
                },

            "soil_temperature":
                {
                    "value":
                        float(
                            soil_temperature
                        )
                },
        }


        units = {
            "soil_moisture":
                "m3/m3",

            "air_temperature":
                "degC",

            "rainfall":
                "mm",

            "solar_radiation":
                "W/m2",

            "relative_humidity":
                "%",

            "soil_temperature":
                "degC",
        }


        for (
            variable,
            value,
        ) in values.items():

            rows.append(
                MachineEvidenceModel(
                    id=evidence_id(
                        variable,
                        timestamp,
                    ),

                    parcel_id=(
                        PARCEL_ID
                    ),

                    variable=(
                        variable
                    ),

                    value=(
                        value
                    ),

                    unit=(
                        units[
                            variable
                        ]
                    ),

                    observed_at=(
                        timestamp
                    ),

                    status="ACTIVE",

                    quality_score=0.90,

                    uncertainty={
                        "type":
                            "SYNTHETIC_DEMO"
                    },

                    provenance=(
                        provenance_payload()
                    ),

                    metadata_json={
                        "synthetic":
                            True,

                        "purpose":
                            "ML_INTEGRATION_TEST",

                        "generator":
                            (
                                "seed_synthetic_ml_history.py"
                            ),
                    },

                    created_at=(
                        datetime.now(
                            timezone.utc
                        )
                    ),
                )
            )


    # ==================================================
    # SAVE
    # ==================================================

    with SessionLocal() as session:

        # Remove previous demo rows from this seeder
        # so script can be re-run safely.

        existing = (
            session.query(
                MachineEvidenceModel
            )
            .filter(
                MachineEvidenceModel.parcel_id
                == PARCEL_ID
            )
            .all()
        )


        deleted = 0


        for item in existing:

            metadata = (
                item.metadata_json
                or {}
            )


            if (
                metadata.get(
                    "purpose"
                )
                == "ML_INTEGRATION_TEST"
            ):

                session.delete(
                    item
                )

                deleted += 1


        session.flush()


        session.add_all(
            rows
        )

        session.commit()


    print()
    print(
        "=========================================="
    )
    print(
        "SYNTHETIC ML HISTORY SEEDED"
    )
    print(
        "=========================================="
    )

    print(
        f"Parcel: "
        f"{PARCEL_ID}"
    )

    print(
        f"Hours: "
        f"{HOURS}"
    )

    print(
        f"Variables/hour: "
        f"6"
    )

    print(
        f"Rows inserted: "
        f"{len(rows)}"
    )

    print(
        f"Previous demo rows removed: "
        f"{deleted}"
    )

    print(
        f"Start: "
        f"{start_time.isoformat()}"
    )

    print(
        f"End: "
        f"{end_time.isoformat()}"
    )

    print()
    print(
        "Data provenance: SYNTHETIC"
    )

    print(
        "Purpose: ML_INTEGRATION_TEST"
    )


if __name__ == "__main__":
    main()