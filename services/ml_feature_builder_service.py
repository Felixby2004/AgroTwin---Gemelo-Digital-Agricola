from __future__ import annotations

from datetime import (
    datetime,
    timedelta,
    timezone,
)

import math

import numpy as np
import pandas as pd

from sqlalchemy.orm import (
    Session,
)

from database.repositories.machine_evidence_repository import (
    MachineEvidenceRepository,
)


# ======================================================
# VARIABLE ALIASES
#
# Allows current system naming + conventional IoT names.
# ======================================================

VARIABLE_ALIASES = {

    "soil_moisture": {
        "soil_moisture",
        "soil_water_state",
    },

    "air_temperature": {
        "air_temperature",
        "temperature",
    },

    "rainfall": {
        "rainfall",
        "precipitation",
    },

    "solar_radiation": {
        "solar_radiation",
        "solarad",
    },

    "relative_humidity": {
        "relative_humidity",
        "humidity",
    },

    "soil_temperature": {
        "soil_temperature",
    },
}


class InsufficientMLHistoryError(
    ValueError
):
    pass


class MLFeatureBuilderService:

    def __init__(
        self,
        session: Session,
    ) -> None:

        self.repository = (
            MachineEvidenceRepository(
                session
            )
        )


    # ==================================================
    # JSON VALUE → FLOAT
    # ==================================================

    @staticmethod
    def _extract_numeric_value(
        variable: str,
        value,
    ) -> float | None:

        if value is None:
            return None


        # ----------------------------------------------
        # Plain number
        # ----------------------------------------------

        if isinstance(
            value,
            (
                int,
                float,
            ),
        ):

            numeric = float(
                value
            )

            if math.isfinite(
                numeric
            ):

                return numeric

            return None


        # ----------------------------------------------
        # JSON dictionary
        # ----------------------------------------------

        if isinstance(
            value,
            dict,
        ):

            # Special shape already used by TwinState:
            #
            # {
            #   "soil_moisture": 0.23
            # }

            preferred_keys = [
                variable,
                "value",
            ]


            if variable == (
                "soil_water_state"
            ):

                preferred_keys.insert(
                    0,
                    "soil_moisture",
                )


            for key in preferred_keys:

                candidate = (
                    value.get(
                        key
                    )
                )

                if isinstance(
                    candidate,
                    (
                        int,
                        float,
                    ),
                ):

                    numeric = float(
                        candidate
                    )

                    if math.isfinite(
                        numeric
                    ):

                        return numeric


            # Last safe fallback:
            # exactly one numeric field.

            numeric_values = [
                float(item)
                for item
                in value.values()
                if isinstance(
                    item,
                    (
                        int,
                        float,
                    ),
                )
                and math.isfinite(
                    float(item)
                )
            ]


            if len(
                numeric_values
            ) == 1:

                return (
                    numeric_values[0]
                )


        return None


    # ==================================================
    # CANONICAL VARIABLE
    # ==================================================

    @staticmethod
    def _canonical_variable(
        variable: str,
    ) -> str | None:

        normalized = (
            variable
            .strip()
            .lower()
        )


        for (
            canonical,
            aliases,
        ) in (
            VARIABLE_ALIASES
            .items()
        ):

            if normalized in aliases:

                return canonical


        return None


    # ==================================================
    # BUILD DATAFRAME
    # ==================================================

    def _history_dataframe(
        self,
        parcel_id: str,
    ) -> pd.DataFrame:

        now = datetime.now(
            timezone.utc
        )


        # 72 h gives enough history for:
        #
        # - t-24 h
        # - rainfall 48 h
        # - interpolation/resampling margins

        start_at = (
            now
            - timedelta(
                hours=72
            )
        )


        aliases = sorted(
            {
                alias

                for values
                in VARIABLE_ALIASES.values()

                for alias
                in values
            }
        )


        evidence = (
            self.repository
            .list_parcel_history(
                parcel_id=parcel_id,
                start_at=start_at,
                variables=aliases,
                active_only=True,
            )
        )


        rows = []


        for item in evidence:

            if item.observed_at is None:
                continue


            canonical = (
                self._canonical_variable(
                    item.variable
                )
            )


            if canonical is None:
                continue


            numeric = (
                self._extract_numeric_value(
                    item.variable,
                    item.value,
                )
            )


            if numeric is None:
                continue


            timestamp = pd.Timestamp(
                item.observed_at
            )


            if timestamp.tzinfo is None:

                timestamp = (
                    timestamp.tz_localize(
                        "UTC"
                    )
                )

            else:

                timestamp = (
                    timestamp.tz_convert(
                        "UTC"
                    )
                )


            rows.append(
                {
                    "timestamp":
                        timestamp,

                    "variable":
                        canonical,

                    "value":
                        numeric,
                }
            )


        if not rows:

            raise (
                InsufficientMLHistoryError(
                    "No usable historical "
                    "machine evidence was found "
                    "for this parcel."
                )
            )


        dataframe = pd.DataFrame(
            rows
        )


        # Latest measurement wins if there
        # are duplicates during the same hour.

        dataframe[
            "timestamp"
        ] = (
            dataframe[
                "timestamp"
            ]
            .dt.floor(
                "h"
            )
        )


        dataframe = (
            dataframe
            .sort_values(
                "timestamp"
            )
            .drop_duplicates(
                subset=[
                    "timestamp",
                    "variable",
                ],
                keep="last",
            )
        )


        wide = dataframe.pivot(
            index="timestamp",
            columns="variable",
            values="value",
        )


        # Continuous hourly index.
        # We DO NOT manufacture measurements here.
        # Missing values remain NaN.

        complete_index = (
            pd.date_range(
                start=wide.index.min(),
                end=wide.index.max(),
                freq="h",
                tz="UTC",
            )
        )


        wide = wide.reindex(
            complete_index
        )


        wide.index.name = (
            "timestamp"
        )


        return wide


    # ==================================================
    # LAG VALUE
    # ==================================================

    @staticmethod
    def _lag(
        series: pd.Series,
        hours: int,
    ) -> float | None:

        if len(series) <= hours:
            return None


        value = series.iloc[
            -(hours + 1)
        ]


        if pd.isna(
            value
        ):

            return None


        return float(
            value
        )


    # ==================================================
    # CURRENT VALUE
    # ==================================================

    @staticmethod
    def _latest(
        series: pd.Series,
    ) -> float | None:

        clean = series.dropna()


        if clean.empty:
            return None


        return float(
            clean.iloc[-1]
        )


    # ==================================================
    # ROLLING SUM
    # ==================================================

    @staticmethod
    def _sum_last(
        series: pd.Series,
        hours: int,
    ) -> float | None:

        values = series.tail(
            hours
        )


        if values.dropna().empty:
            return None


        return float(
            values.sum(
                skipna=True
            )
        )


    # ==================================================
    # ROLLING MEAN
    # ==================================================

    @staticmethod
    def _mean_last(
        series: pd.Series,
        hours: int,
    ) -> float | None:

        values = series.tail(
            hours
        )


        if values.dropna().empty:
            return None


        return float(
            values.mean(
                skipna=True
            )
        )


    # ==================================================
    # BUILD FEATURES
    # ==================================================

    def build(
        self,
        parcel_id: str,
    ) -> dict:

        dataframe = (
            self._history_dataframe(
                parcel_id
            )
        )


        if "soil_moisture" not in (
            dataframe.columns
        ):

            raise (
                InsufficientMLHistoryError(
                    "The parcel has no historical "
                    "soil-moisture observations."
                )
            )


        soil = dataframe[
            "soil_moisture"
        ]


        current = (
            self._latest(
                soil
            )
        )


        if current is None:

            raise (
                InsufficientMLHistoryError(
                    "No current soil-moisture "
                    "observation is available."
                )
            )


        # At least 24 h history is required
        # for a meaningful residual RF input.

        first_valid = (
            soil
            .first_valid_index()
        )

        last_valid = (
            soil
            .last_valid_index()
        )


        if (
            first_valid is None
            or last_valid is None
            or (
                last_valid
                - first_valid
            )
            < pd.Timedelta(
                hours=24
            )
        ):

            raise (
                InsufficientMLHistoryError(
                    "At least 24 hours of "
                    "soil-moisture history "
                    "are required."
                )
            )


        lag_1 = self._lag(
            soil,
            1,
        )

        lag_3 = self._lag(
            soil,
            3,
        )

        lag_6 = self._lag(
            soil,
            6,
        )

        lag_12 = self._lag(
            soil,
            12,
        )

        lag_24 = self._lag(
            soil,
            24,
        )


        def change(
            lag: float | None,
        ) -> float | None:

            if lag is None:
                return None

            return (
                current
                - lag
            )


        # ----------------------------------------------
        # Other variables
        # ----------------------------------------------

        def column(
            name: str,
        ) -> pd.Series:

            if name in dataframe.columns:

                return dataframe[
                    name
                ]

            return pd.Series(
                index=dataframe.index,
                dtype=float,
            )


        air_temperature = column(
            "air_temperature"
        )

        rainfall = column(
            "rainfall"
        )

        solar = column(
            "solar_radiation"
        )

        humidity = column(
            "relative_humidity"
        )

        soil_temperature = column(
            "soil_temperature"
        )


        reference_time = (
            soil
            .last_valid_index()
        )


        hour = (
            reference_time.hour
        )

        day_of_year = (
            reference_time.dayofyear
        )


        features = {

            "soil_moisture":
                current,

            "soil_moisture_lag_1h":
                lag_1,

            "soil_moisture_lag_3h":
                lag_3,

            "soil_moisture_lag_6h":
                lag_6,

            "soil_moisture_lag_12h":
                lag_12,

            "soil_moisture_lag_24h":
                lag_24,

            "soil_moisture_change_1h":
                change(
                    lag_1
                ),

            "soil_moisture_change_6h":
                change(
                    lag_6
                ),

            "soil_moisture_change_12h":
                change(
                    lag_12
                ),

            "soil_moisture_change_previous_24h":
                change(
                    lag_24
                ),

            "air_temperature":
                self._latest(
                    air_temperature
                ),

            "rainfall":
                self._latest(
                    rainfall
                ),

            "solar_radiation":
                self._latest(
                    solar
                ),

            "relative_humidity":
                self._latest(
                    humidity
                ),

            "soil_temperature":
                self._latest(
                    soil_temperature
                ),

            "rainfall_6h":
                self._sum_last(
                    rainfall,
                    6,
                ),

            "rainfall_24h":
                self._sum_last(
                    rainfall,
                    24,
                ),

            "rainfall_48h":
                self._sum_last(
                    rainfall,
                    48,
                ),

            "temperature_6h_mean":
                self._mean_last(
                    air_temperature,
                    6,
                ),

            "solar_6h_mean":
                self._mean_last(
                    solar,
                    6,
                ),

            "humidity_6h_mean":
                self._mean_last(
                    humidity,
                    6,
                ),

            "hour_sin":
                float(
                    np.sin(
                        2
                        * np.pi
                        * hour
                        / 24
                    )
                ),

            "hour_cos":
                float(
                    np.cos(
                        2
                        * np.pi
                        * hour
                        / 24
                    )
                ),

            "doy_sin":
                float(
                    np.sin(
                        2
                        * np.pi
                        * day_of_year
                        / 365.25
                    )
                ),

            "doy_cos":
                float(
                    np.cos(
                        2
                        * np.pi
                        * day_of_year
                        / 365.25
                    )
                ),
        }


        available_count = sum(
            value is not None
            for value
            in features.values()
        )


        missing_features = [
            key
            for key, value
            in features.items()
            if value is None
        ]


        return {
            "parcel_id":
                parcel_id,

            "reference_timestamp":
                reference_time.isoformat(),

            "features":
                features,

            "feature_availability": {
                "available":
                    available_count,

                "total":
                    len(features),

                "missing":
                    missing_features,
            },
        }