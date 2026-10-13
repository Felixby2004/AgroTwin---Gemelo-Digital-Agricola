from __future__ import annotations

from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd


# =========================================================
# PROJECT PATHS
# =========================================================

PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parent
    .parent
)


DEFAULT_DATASET_PATH = (
    PROJECT_ROOT
    / "data"
    / "ml"
    / "soil_moisture_training.csv"
)


DEFAULT_RAW_DIR = (
    PROJECT_ROOT
    / "data"
    / "ml"
    / "uscrn_raw"
)


# =========================================================
# DATASET METADATA
# =========================================================

EXPECTED_STATION = (
    "AZ_Yuma_27_ENE"
)


TIMESTAMP_COLUMN = (
    "timestamp"
)


CURRENT_SOIL_MOISTURE = (
    "soil_moisture"
)


FUTURE_SOIL_MOISTURE = (
    "future_soil_moisture_24h"
)


DELTA_TARGET = (
    "soil_moisture_change_24h"
)


PREDICTION_HORIZON_HOURS = 24


# =========================================================
# CORE RAW VARIABLES
# =========================================================

RAW_VARIABLES = [

    "soil_moisture",

    "air_temperature",

    "rainfall",

    "solar_radiation",

    "relative_humidity",

    "soil_temperature",
]


# =========================================================
# TEMPORAL / ENGINEERED VARIABLES
# =========================================================

TEMPORAL_VARIABLES = [

    "hour",

    "day_of_year",

    "hour_sin",

    "hour_cos",

    "doy_sin",

    "doy_cos",
]


LAG_VARIABLES = [

    "soil_moisture_lag_1h",

    "soil_moisture_lag_3h",

    "soil_moisture_lag_6h",

    "soil_moisture_lag_12h",

    "soil_moisture_lag_24h",
]


CHANGE_VARIABLES = [

    "soil_moisture_change_1h",

    "soil_moisture_change_6h",

    "soil_moisture_change_12h",

    "soil_moisture_change_previous_24h",
]


ROLLING_VARIABLES = [

    "rainfall_6h",

    "rainfall_24h",

    "rainfall_48h",

    "temperature_6h_mean",

    "solar_6h_mean",

    "humidity_6h_mean",
]


# =========================================================
# EXPECTED MODEL PREDICTORS
# =========================================================

MODEL_PREDICTORS = [

    "soil_moisture",

    "soil_moisture_lag_1h",

    "soil_moisture_lag_3h",

    "soil_moisture_lag_6h",

    "soil_moisture_lag_12h",

    "soil_moisture_lag_24h",

    "soil_moisture_change_1h",

    "soil_moisture_change_6h",

    "soil_moisture_change_12h",

    "soil_moisture_change_previous_24h",

    "air_temperature",

    "rainfall",

    "solar_radiation",

    "relative_humidity",

    "soil_temperature",

    "rainfall_6h",

    "rainfall_24h",

    "rainfall_48h",

    "temperature_6h_mean",

    "solar_6h_mean",

    "humidity_6h_mean",

    "hour_sin",

    "hour_cos",

    "doy_sin",

    "doy_cos",
]


# =========================================================
# REQUIRED DATASET COLUMNS
# =========================================================

REQUIRED_COLUMNS = [

    "timestamp",

    "station_id",

    "soil_moisture",

    "air_temperature",

    "rainfall",

    "solar_radiation",

    "relative_humidity",

    "soil_temperature",

    "future_soil_moisture_24h",

    "soil_moisture_change_24h",
]


# =========================================================
# LEAKAGE COLUMNS
#
# They can exist in the dataset for evaluation,
# but must NOT be used as model predictors.
# =========================================================

LEAKAGE_COLUMNS = [

    FUTURE_SOIL_MOISTURE,

    DELTA_TARGET,
]


# =========================================================
# LOAD DATASET
# =========================================================

def load_training_dataset(
    path: str | Path | None = None,
    strict: bool = True,
) -> pd.DataFrame:
    """
    Load the prepared NOAA USCRN soil-moisture dataset.

    No imputation or silent repair is performed here.
    This function is intentionally conservative because
    CRISP-DM data understanding must expose data-quality
    problems instead of hiding them.
    """

    dataset_path = (
        Path(path)
        if path is not None
        else DEFAULT_DATASET_PATH
    )


    if not dataset_path.exists():

        raise FileNotFoundError(
            "Dataset not found: "
            f"{dataset_path}"
        )


    dataframe = pd.read_csv(
        dataset_path,
        low_memory=False,
    )


    if strict:

        missing_columns = [

            column

            for column
            in REQUIRED_COLUMNS

            if column
            not in dataframe.columns
        ]


        if missing_columns:

            raise ValueError(
                "Dataset is missing required columns: "
                + ", ".join(
                    missing_columns
                )
            )


    if (
        TIMESTAMP_COLUMN
        in dataframe.columns
    ):

        dataframe[
            TIMESTAMP_COLUMN
        ] = pd.to_datetime(
            dataframe[
                TIMESTAMP_COLUMN
            ],
            errors="coerce",
            utc=True,
        )


        dataframe = (
            dataframe
            .sort_values(
                TIMESTAMP_COLUMN
            )
            .reset_index(
                drop=True
            )
        )


        # -----------------------------------------------
        # Reconstruct descriptive temporal columns only
        # when absent.
        # -----------------------------------------------

        if (
            "year"
            not in dataframe.columns
        ):

            dataframe[
                "year"
            ] = (
                dataframe[
                    TIMESTAMP_COLUMN
                ]
                .dt
                .year
            )


        if (
            "month"
            not in dataframe.columns
        ):

            dataframe[
                "month"
            ] = (
                dataframe[
                    TIMESTAMP_COLUMN
                ]
                .dt
                .month
            )


        if (
            "hour"
            not in dataframe.columns
        ):

            dataframe[
                "hour"
            ] = (
                dataframe[
                    TIMESTAMP_COLUMN
                ]
                .dt
                .hour
            )


        if (
            "day_of_year"
            not in dataframe.columns
        ):

            dataframe[
                "day_of_year"
            ] = (
                dataframe[
                    TIMESTAMP_COLUMN
                ]
                .dt
                .dayofyear
            )


    return dataframe


# =========================================================
# SCHEMA AUDIT
# =========================================================

def schema_audit(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:

    rows = []


    expected_columns = list(
        dict.fromkeys(
            REQUIRED_COLUMNS
            + MODEL_PREDICTORS
            + [
                "latitude",
                "longitude",
                "year",
            ]
        )
    )


    for column in expected_columns:

        exists = (
            column
            in dataframe.columns
        )


        rows.append(
            {
                "column":
                    column,

                "required":
                    column
                    in REQUIRED_COLUMNS,

                "model_predictor":
                    column
                    in MODEL_PREDICTORS,

                "exists":
                    exists,

                "dtype":
                    str(
                        dataframe[
                            column
                        ].dtype
                    )
                    if exists
                    else None,

                "missing_count":
                    int(
                        dataframe[
                            column
                        ]
                        .isna()
                        .sum()
                    )
                    if exists
                    else None,

                "missing_percent":
                    float(
                        dataframe[
                            column
                        ]
                        .isna()
                        .mean()
                        * 100
                    )
                    if (
                        exists
                        and
                        len(
                            dataframe
                        ) > 0
                    )
                    else None,
            }
        )


    return pd.DataFrame(
        rows
    )


# =========================================================
# GENERAL OVERVIEW
# =========================================================

def dataset_overview(
    dataframe: pd.DataFrame,
) -> dict:

    timestamps = (
        dataframe[
            TIMESTAMP_COLUMN
        ]
        if TIMESTAMP_COLUMN
        in dataframe.columns
        else pd.Series(
            dtype="datetime64[ns]"
        )
    )


    valid_timestamps = (
        timestamps
        .dropna()
    )


    years = []

    if not valid_timestamps.empty:

        years = sorted(
            valid_timestamps
            .dt
            .year
            .unique()
            .tolist()
        )


    stations = []

    if (
        "station_id"
        in dataframe.columns
    ):

        stations = (
            dataframe[
                "station_id"
            ]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )


    duplicate_timestamps = 0

    if (
        TIMESTAMP_COLUMN
        in dataframe.columns
    ):

        duplicate_timestamps = int(
            dataframe[
                TIMESTAMP_COLUMN
            ]
            .duplicated()
            .sum()
        )


    return {

        "rows":
            int(
                len(
                    dataframe
                )
            ),

        "columns":
            int(
                len(
                    dataframe.columns
                )
            ),

        "start":
            (
                valid_timestamps
                .min()
                .isoformat()
                if not
                valid_timestamps.empty
                else None
            ),

        "end":
            (
                valid_timestamps
                .max()
                .isoformat()
                if not
                valid_timestamps.empty
                else None
            ),

        "years":
            years,

        "stations":
            stations,

        "expected_station":
            EXPECTED_STATION,

        "prediction_horizon_hours":
            PREDICTION_HORIZON_HOURS,

        "current_variable":
            CURRENT_SOIL_MOISTURE,

        "future_target":
            FUTURE_SOIL_MOISTURE,

        "delta_target":
            DELTA_TARGET,

        "duplicate_timestamps":
            duplicate_timestamps,

        "missing_timestamp_count":
            (
                int(
                    timestamps
                    .isna()
                    .sum()
                )
                if TIMESTAMP_COLUMN
                in dataframe.columns
                else None
            ),
    }


# =========================================================
# MISSING VALUES
# =========================================================

def missing_values_table(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:

    if dataframe.empty:

        return pd.DataFrame(
            columns=[
                "column",
                "missing_count",
                "missing_percent",
                "dtype",
            ]
        )


    result = pd.DataFrame(
        {
            "column":
                dataframe.columns,

            "missing_count":
                [
                    int(
                        dataframe[
                            column
                        ]
                        .isna()
                        .sum()
                    )
                    for column
                    in dataframe.columns
                ],

            "missing_percent":
                [
                    float(
                        dataframe[
                            column
                        ]
                        .isna()
                        .mean()
                        * 100
                    )
                    for column
                    in dataframe.columns
                ],

            "dtype":
                [
                    str(
                        dataframe[
                            column
                        ].dtype
                    )
                    for column
                    in dataframe.columns
                ],
        }
    )


    return (
        result
        .sort_values(
            [
                "missing_count",
                "column",
            ],
            ascending=[
                False,
                True,
            ],
        )
        .reset_index(
            drop=True
        )
    )


# =========================================================
# DUPLICATE TIMESTAMPS
# =========================================================

def duplicate_timestamp_table(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:

    if (
        TIMESTAMP_COLUMN
        not in dataframe.columns
    ):

        return pd.DataFrame()


    duplicated = dataframe[
        dataframe[
            TIMESTAMP_COLUMN
        ]
        .duplicated(
            keep=False
        )
    ].copy()


    return duplicated.sort_values(
        TIMESTAMP_COLUMN
    )


# =========================================================
# TEMPORAL GAPS
# =========================================================

def temporal_gap_table(
    dataframe: pd.DataFrame,
    expected_frequency_hours: int = 1,
) -> pd.DataFrame:

    if (
        TIMESTAMP_COLUMN
        not in dataframe.columns
    ):

        return pd.DataFrame(
            columns=[
                "previous_timestamp",
                "timestamp",
                "gap_hours",
            ]
        )


    timestamps = (
        dataframe[
            TIMESTAMP_COLUMN
        ]
        .dropna()
        .drop_duplicates()
        .sort_values()
        .reset_index(
            drop=True
        )
    )


    if len(
        timestamps
    ) < 2:

        return pd.DataFrame(
            columns=[
                "previous_timestamp",
                "timestamp",
                "gap_hours",
            ]
        )


    previous = timestamps.shift(1)


    gap_hours = (
        timestamps
        -
        previous
    ).dt.total_seconds() / 3600.0


    gaps = pd.DataFrame(
        {
            "previous_timestamp":
                previous,

            "timestamp":
                timestamps,

            "gap_hours":
                gap_hours,
        }
    )


    gaps = gaps[
        gaps[
            "gap_hours"
        ]
        >
        expected_frequency_hours
    ]


    return gaps.reset_index(
        drop=True
    )


# =========================================================
# TEMPORAL COVERAGE BY YEAR
# =========================================================

def temporal_coverage_by_year(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:

    if (
        TIMESTAMP_COLUMN
        not in dataframe.columns
    ):

        return pd.DataFrame()


    data = dataframe[
        [
            TIMESTAMP_COLUMN,
        ]
    ].copy()


    data = data.dropna(
        subset=[
            TIMESTAMP_COLUMN,
        ]
    )


    data[
        "year"
    ] = (
        data[
            TIMESTAMP_COLUMN
        ]
        .dt
        .year
    )


    rows = []


    for year, group in (
        data.groupby(
            "year"
        )
    ):

        unique_timestamps = (
            group[
                TIMESTAMP_COLUMN
            ]
            .drop_duplicates()
        )


        start = pd.Timestamp(
            year=int(
                year
            ),
            month=1,
            day=1,
            tz="UTC",
        )


        end = pd.Timestamp(
            year=int(
                year
            )
            + 1,
            month=1,
            day=1,
            tz="UTC",
        )


        expected_hours = int(
            (
                end
                -
                start
            )
            .total_seconds()
            /
            3600
        )


        observed_hours = int(
            len(
                unique_timestamps
            )
        )


        rows.append(
            {
                "year":
                    int(
                        year
                    ),

                "observed_rows":
                    int(
                        len(
                            group
                        )
                    ),

                "unique_timestamps":
                    observed_hours,

                "expected_hours_full_year":
                    expected_hours,

                "coverage_percent":
                    float(
                        observed_hours
                        /
                        expected_hours
                        *
                        100
                    ),

                "start":
                    (
                        unique_timestamps
                        .min()
                    ),

                "end":
                    (
                        unique_timestamps
                        .max()
                    ),
            }
        )


    return pd.DataFrame(
        rows
    )


# =========================================================
# NUMERIC SUMMARY
# =========================================================

def numeric_summary(
    dataframe: pd.DataFrame,
    columns: Iterable[str] | None = None,
) -> pd.DataFrame:

    if columns is None:

        columns = (
            dataframe
            .select_dtypes(
                include=[
                    np.number,
                ]
            )
            .columns
            .tolist()
        )


    rows = []


    for column in columns:

        if (
            column
            not in dataframe.columns
        ):
            continue


        series = pd.to_numeric(
            dataframe[
                column
            ],
            errors="coerce",
        )


        valid = (
            series
            .dropna()
        )


        if valid.empty:

            rows.append(
                {
                    "variable":
                        column,

                    "count":
                        0,

                    "missing":
                        int(
                            series
                            .isna()
                            .sum()
                        ),

                    "mean":
                        np.nan,

                    "std":
                        np.nan,

                    "min":
                        np.nan,

                    "p01":
                        np.nan,

                    "p25":
                        np.nan,

                    "median":
                        np.nan,

                    "p75":
                        np.nan,

                    "p99":
                        np.nan,

                    "max":
                        np.nan,
                }
            )

            continue


        rows.append(
            {
                "variable":
                    column,

                "count":
                    int(
                        valid.count()
                    ),

                "missing":
                    int(
                        series
                        .isna()
                        .sum()
                    ),

                "mean":
                    float(
                        valid.mean()
                    ),

                "std":
                    float(
                        valid.std()
                    ),

                "min":
                    float(
                        valid.min()
                    ),

                "p01":
                    float(
                        valid.quantile(
                            0.01
                        )
                    ),

                "p25":
                    float(
                        valid.quantile(
                            0.25
                        )
                    ),

                "median":
                    float(
                        valid.median()
                    ),

                "p75":
                    float(
                        valid.quantile(
                            0.75
                        )
                    ),

                "p99":
                    float(
                        valid.quantile(
                            0.99
                        )
                    ),

                "max":
                    float(
                        valid.max()
                    ),
            }
        )


    return pd.DataFrame(
        rows
    )


# =========================================================
# IQR OUTLIER SUMMARY
# =========================================================

def outlier_summary_iqr(
    dataframe: pd.DataFrame,
    columns: Iterable[str] | None = None,
) -> pd.DataFrame:

    if columns is None:

        columns = [

            column

            for column
            in RAW_VARIABLES

            if column
            in dataframe.columns
        ]


    rows = []


    for column in columns:

        if (
            column
            not in dataframe.columns
        ):
            continue


        series = pd.to_numeric(
            dataframe[
                column
            ],
            errors="coerce",
        )


        valid = (
            series
            .dropna()
        )


        if valid.empty:

            continue


        q1 = float(
            valid.quantile(
                0.25
            )
        )


        q3 = float(
            valid.quantile(
                0.75
            )
        )


        iqr = (
            q3
            -
            q1
        )


        lower = (
            q1
            -
            1.5
            *
            iqr
        )


        upper = (
            q3
            +
            1.5
            *
            iqr
        )


        outlier_mask = (
            (
                valid
                <
                lower
            )
            |
            (
                valid
                >
                upper
            )
        )


        outlier_count = int(
            outlier_mask
            .sum()
        )


        rows.append(
            {
                "variable":
                    column,

                "q1":
                    q1,

                "q3":
                    q3,

                "iqr":
                    iqr,

                "lower_bound":
                    float(
                        lower
                    ),

                "upper_bound":
                    float(
                        upper
                    ),

                "outlier_count":
                    outlier_count,

                "outlier_percent":
                    float(
                        outlier_count
                        /
                        len(
                            valid
                        )
                        *
                        100
                    ),
            }
        )


    return pd.DataFrame(
        rows
    )


# =========================================================
# PHYSICAL / QUALITY CHECKS
# =========================================================

def physical_quality_checks(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:

    rows = []


    def add_check(
        name: str,
        column: str,
        invalid_mask: pd.Series,
        expected: str,
    ) -> None:

        count = int(
            invalid_mask
            .fillna(
                False
            )
            .sum()
        )


        rows.append(
            {
                "check":
                    name,

                "column":
                    column,

                "invalid_count":
                    count,

                "invalid_percent":
                    float(
                        count
                        /
                        len(
                            dataframe
                        )
                        *
                        100
                    )
                    if len(
                        dataframe
                    ) > 0
                    else 0.0,

                "expected":
                    expected,

                "status":
                    (
                        "PASS"
                        if count == 0
                        else "REVIEW"
                    ),
            }
        )


    if (
        CURRENT_SOIL_MOISTURE
        in dataframe.columns
    ):

        series = pd.to_numeric(
            dataframe[
                CURRENT_SOIL_MOISTURE
            ],
            errors="coerce",
        )


        add_check(
            name=
                "Current soil moisture physical range",

            column=
                CURRENT_SOIL_MOISTURE,

            invalid_mask=
                (
                    (
                        series
                        <
                        0
                    )
                    |
                    (
                        series
                        >
                        0.8
                    )
                ),

            expected=
                "0.0 <= soil_moisture <= 0.8",
        )


    if (
        FUTURE_SOIL_MOISTURE
        in dataframe.columns
    ):

        series = pd.to_numeric(
            dataframe[
                FUTURE_SOIL_MOISTURE
            ],
            errors="coerce",
        )


        add_check(
            name=
                "Future soil moisture physical range",

            column=
                FUTURE_SOIL_MOISTURE,

            invalid_mask=
                (
                    (
                        series
                        <
                        0
                    )
                    |
                    (
                        series
                        >
                        0.8
                    )
                ),

            expected=
                "0.0 <= future_soil_moisture_24h <= 0.8",
        )


    if (
        "relative_humidity"
        in dataframe.columns
    ):

        series = pd.to_numeric(
            dataframe[
                "relative_humidity"
            ],
            errors="coerce",
        )


        add_check(
            name=
                "Relative humidity range",

            column=
                "relative_humidity",

            invalid_mask=
                (
                    (
                        series
                        <
                        0
                    )
                    |
                    (
                        series
                        >
                        100
                    )
                ),

            expected=
                "0 <= relative_humidity <= 100",
        )


    if (
        "rainfall"
        in dataframe.columns
    ):

        series = pd.to_numeric(
            dataframe[
                "rainfall"
            ],
            errors="coerce",
        )


        add_check(
            name=
                "Rainfall non-negative",

            column=
                "rainfall",

            invalid_mask=
                (
                    series
                    <
                    0
                ),

            expected=
                "rainfall >= 0",
        )


    if (
        "solar_radiation"
        in dataframe.columns
    ):

        series = pd.to_numeric(
            dataframe[
                "solar_radiation"
            ],
            errors="coerce",
        )


        add_check(
            name=
                "Solar radiation non-negative",

            column=
                "solar_radiation",

            invalid_mask=
                (
                    series
                    <
                    0
                ),

            expected=
                "solar_radiation >= 0",
        )


    return pd.DataFrame(
        rows
    )


# =========================================================
# DATA QUALITY ISSUES
# =========================================================

def data_quality_issues(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """
    Detect structural issues without repairing them.
    """

    issues = []


    # -----------------------------------------------------
    # Entirely missing columns
    # -----------------------------------------------------

    for column in dataframe.columns:

        if (
            dataframe[
                column
            ]
            .isna()
            .all()
        ):

            issues.append(
                {
                    "severity":
                        "HIGH",

                    "issue":
                        "ALL_VALUES_MISSING",

                    "column":
                        column,

                    "detail":
                        (
                            "The column contains no usable "
                            "values in the processed dataset."
                        ),
                }
            )


    # -----------------------------------------------------
    # Duplicate timestamps
    # -----------------------------------------------------

    if (
        TIMESTAMP_COLUMN
        in dataframe.columns
    ):

        duplicate_count = int(
            dataframe[
                TIMESTAMP_COLUMN
            ]
            .duplicated()
            .sum()
        )


        if (
            duplicate_count
            >
            0
        ):

            issues.append(
                {
                    "severity":
                        "HIGH",

                    "issue":
                        "DUPLICATE_TIMESTAMPS",

                    "column":
                        TIMESTAMP_COLUMN,

                    "detail":
                        (
                            f"{duplicate_count} duplicated "
                            "timestamps were detected."
                        ),
                }
            )


    # -----------------------------------------------------
    # Unexpected station
    # -----------------------------------------------------

    if (
        "station_id"
        in dataframe.columns
    ):

        stations = set(
            dataframe[
                "station_id"
            ]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )


        if (
            stations
            and
            stations !=
            {
                EXPECTED_STATION
            }
        ):

            issues.append(
                {
                    "severity":
                        "HIGH",

                    "issue":
                        "UNEXPECTED_STATION",

                    "column":
                        "station_id",

                    "detail":
                        (
                            "Expected station "
                            f"{EXPECTED_STATION}; "
                            f"found {sorted(stations)}."
                        ),
                }
            )


    # -----------------------------------------------------
    # Missing predictors
    # -----------------------------------------------------

    missing_predictors = [

        column

        for column
        in MODEL_PREDICTORS

        if column
        not in dataframe.columns
    ]


    if (
        missing_predictors
    ):

        issues.append(
            {
                "severity":
                    "HIGH",

                "issue":
                    "MISSING_MODEL_PREDICTORS",

                "column":
                    ", ".join(
                        missing_predictors
                    ),

                "detail":
                    (
                        "One or more expected predictor "
                        "columns are absent."
                    ),
            }
        )


    # -----------------------------------------------------
    # Target availability
    # -----------------------------------------------------

    for target in [
        FUTURE_SOIL_MOISTURE,
        DELTA_TARGET,
    ]:

        if (
            target
            not in dataframe.columns
        ):

            issues.append(
                {
                    "severity":
                        "HIGH",

                    "issue":
                        "MISSING_TARGET",

                    "column":
                        target,

                    "detail":
                        (
                            "The supervised-learning target "
                            "is not available."
                        ),
                }
            )


    if not issues:

        issues.append(
            {
                "severity":
                    "INFO",

                "issue":
                    "NO_STRUCTURAL_ISSUES",

                "column":
                    None,

                "detail":
                    (
                        "No structural data-quality issue "
                        "was detected by the current checks."
                    ),
            }
        )


    return pd.DataFrame(
        issues
    )


# =========================================================
# CORRELATION MATRIX
# =========================================================

def correlation_matrix(
    dataframe: pd.DataFrame,
    columns: Iterable[str] | None = None,
) -> pd.DataFrame:

    if columns is None:

        columns = [

            column

            for column
            in (
                MODEL_PREDICTORS
                + [
                    DELTA_TARGET,
                    FUTURE_SOIL_MOISTURE,
                ]
            )

            if column
            in dataframe.columns
        ]


    selected = [

        column

        for column
        in columns

        if column
        in dataframe.columns
    ]


    if not selected:

        return pd.DataFrame()


    numeric = (
        dataframe[
            selected
        ]
        .apply(
            pd.to_numeric,
            errors="coerce",
        )
    )


    return numeric.corr(
        method="pearson"
    )


# =========================================================
# PREDICTOR/TARGET CORRELATIONS
# =========================================================

def predictor_target_correlations(
    dataframe: pd.DataFrame,
    target: str = DELTA_TARGET,
) -> pd.DataFrame:
    """
    Descriptive correlation only.

    This is NOT model feature importance and does not
    establish causality.
    """

    if (
        target
        not in dataframe.columns
    ):

        return pd.DataFrame(
            columns=[
                "feature",
                "correlation",
                "absolute_correlation",
            ]
        )


    rows = []


    target_series = pd.to_numeric(
        dataframe[
            target
        ],
        errors="coerce",
    )


    for feature in MODEL_PREDICTORS:

        if (
            feature
            not in dataframe.columns
        ):
            continue


        feature_series = pd.to_numeric(
            dataframe[
                feature
            ],
            errors="coerce",
        )


        correlation = (
            feature_series
            .corr(
                target_series
            )
        )


        if (
            pd.isna(
                correlation
            )
        ):
            continue


        rows.append(
            {
                "feature":
                    feature,

                "correlation":
                    float(
                        correlation
                    ),

                "absolute_correlation":
                    float(
                        abs(
                            correlation
                        )
                    ),
            }
        )


    return (
        pd.DataFrame(
            rows
        )
        .sort_values(
            "absolute_correlation",
            ascending=False,
        )
        .reset_index(
            drop=True
        )
    )


# =========================================================
# ANNUAL SUMMARY
# =========================================================

def annual_summary(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:

    if (
        TIMESTAMP_COLUMN
        not in dataframe.columns
    ):

        return pd.DataFrame()


    data = dataframe.copy()


    data[
        "year"
    ] = (
        data[
            TIMESTAMP_COLUMN
        ]
        .dt
        .year
    )


    aggregations = {}


    if (
        "soil_moisture"
        in data.columns
    ):

        aggregations[
            "soil_moisture"
        ] = [
            "mean",
            "std",
            "min",
            "max",
        ]


    if (
        "air_temperature"
        in data.columns
    ):

        aggregations[
            "air_temperature"
        ] = [
            "mean",
            "min",
            "max",
        ]


    if (
        "rainfall"
        in data.columns
    ):

        aggregations[
            "rainfall"
        ] = [
            "sum",
            "mean",
        ]


    if (
        DELTA_TARGET
        in data.columns
    ):

        aggregations[
            DELTA_TARGET
        ] = [
            "mean",
            "std",
        ]


    if not aggregations:

        return pd.DataFrame()


    result = (
        data
        .groupby(
            "year"
        )
        .agg(
            aggregations
        )
    )


    result.columns = [

        "_".join(
            [
                str(part)

                for part
                in column

                if part
            ]
        )

        for column
        in result.columns
    ]


    return (
        result
        .reset_index()
    )


# =========================================================
# MONTHLY SUMMARY
# =========================================================

def monthly_summary(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:

    if (
        TIMESTAMP_COLUMN
        not in dataframe.columns
    ):

        return pd.DataFrame()


    columns = [
        TIMESTAMP_COLUMN,
    ]


    for column in [

        "soil_moisture",

        "air_temperature",

        "rainfall",

        "solar_radiation",

        "relative_humidity",

        "soil_temperature",

        DELTA_TARGET,
    ]:

        if (
            column
            in dataframe.columns
        ):

            columns.append(
                column
            )


    data = (
        dataframe[
            columns
        ]
        .copy()
        .dropna(
            subset=[
                TIMESTAMP_COLUMN,
            ]
        )
        .set_index(
            TIMESTAMP_COLUMN
        )
    )


    aggregations = {}


    for column in [

        "soil_moisture",

        "air_temperature",

        "solar_radiation",

        "relative_humidity",

        "soil_temperature",

        DELTA_TARGET,
    ]:

        if (
            column
            in data.columns
        ):

            aggregations[
                column
            ] = "mean"


    if (
        "rainfall"
        in data.columns
    ):

        aggregations[
            "rainfall"
        ] = "sum"


    if not aggregations:

        return pd.DataFrame()


    result = (
        data
        .resample(
            "MS"
        )
        .agg(
            aggregations
        )
        .reset_index()
    )


    result[
        "year"
    ] = (
        result[
            TIMESTAMP_COLUMN
        ]
        .dt
        .year
    )


    result[
        "month"
    ] = (
        result[
            TIMESTAMP_COLUMN
        ]
        .dt
        .month
    )


    return result


# =========================================================
# HOURLY PROFILE
# =========================================================

def hourly_profile(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:

    if (
        TIMESTAMP_COLUMN
        not in dataframe.columns
    ):

        return pd.DataFrame()


    data = dataframe.copy()


    data[
        "hour_of_day"
    ] = (
        data[
            TIMESTAMP_COLUMN
        ]
        .dt
        .hour
    )


    columns = [

        column

        for column
        in [

            "soil_moisture",

            "air_temperature",

            "solar_radiation",

            "relative_humidity",

            "soil_temperature",

            DELTA_TARGET,
        ]

        if column
        in data.columns
    ]


    if not columns:

        return pd.DataFrame()


    result = (
        data
        .groupby(
            "hour_of_day"
        )[
            columns
        ]
        .mean()
        .reset_index()
    )


    return result


# =========================================================
# TARGET DISTRIBUTION SUMMARY
# =========================================================

def target_distribution_summary(
    dataframe: pd.DataFrame,
    target: str = DELTA_TARGET,
) -> dict:

    if (
        target
        not in dataframe.columns
    ):

        return {}


    series = pd.to_numeric(
        dataframe[
            target
        ],
        errors="coerce",
    ).dropna()


    if series.empty:

        return {}


    return {

        "target":
            target,

        "count":
            int(
                series.count()
            ),

        "mean":
            float(
                series.mean()
            ),

        "median":
            float(
                series.median()
            ),

        "std":
            float(
                series.std()
            ),

        "min":
            float(
                series.min()
            ),

        "p05":
            float(
                series.quantile(
                    0.05
                )
            ),

        "p25":
            float(
                series.quantile(
                    0.25
                )
            ),

        "p75":
            float(
                series.quantile(
                    0.75
                )
            ),

        "p95":
            float(
                series.quantile(
                    0.95
                )
            ),

        "max":
            float(
                series.max()
            ),

        "negative_percent":
            float(
                (
                    series
                    <
                    0
                )
                .mean()
                *
                100
            ),

        "positive_percent":
            float(
                (
                    series
                    >
                    0
                )
                .mean()
                *
                100
            ),

        "zero_percent":
            float(
                (
                    series
                    ==
                    0
                )
                .mean()
                *
                100
            ),
    }


# =========================================================
# DYNAMIC EDA INTERPRETATIONS
# =========================================================

def build_eda_interpretations(
    dataframe: pd.DataFrame,
) -> dict[str, str]:
    """
    Generate conservative textual interpretations.

    These texts are descriptive only.
    They do not claim causality or model superiority.
    """

    interpretations: dict[
        str,
        str
    ] = {}


    overview = dataset_overview(
        dataframe
    )


    years = overview.get(
        "years",
        [],
    )


    interpretations[
        "dataset"
    ] = (
        "El conjunto analizado contiene "
        f"{overview['rows']:,} observaciones y "
        f"{overview['columns']} variables. "
        "El período temporal disponible es "
        f"{overview['start']} a {overview['end']}. "
        "Los años presentes son "
        f"{years}. "
        "Esta estructura permite una evaluación "
        "temporal del modelo sin mezclar aleatoriamente "
        "observaciones futuras con el entrenamiento."
    )


    missing = missing_values_table(
        dataframe
    )


    all_missing = missing[
        missing[
            "missing_percent"
        ]
        >=
        100.0
    ]


    if not all_missing.empty:

        columns = ", ".join(
            all_missing[
                "column"
            ]
            .astype(str)
            .tolist()
        )


        interpretations[
            "missingness"
        ] = (
            "Se detectaron variables completamente "
            "vacías en el conjunto procesado: "
            f"{columns}. "
            "Estas variables deben revisarse en la "
            "etapa de preparación de datos y no deben "
            "ser imputadas silenciosamente sin justificar "
            "su origen."
        )

    else:

        highest_missing = (
            missing
            .head(
                3
            )
        )


        detail = "; ".join(
            (
                f"{row.column}: "
                f"{row.missing_percent:.2f}%"
            )

            for row
            in highest_missing.itertuples()
        )


        interpretations[
            "missingness"
        ] = (
            "No se detectaron columnas completamente "
            "vacías. Las mayores proporciones de datos "
            "faltantes son: "
            f"{detail}. "
            "La necesidad de imputación deberá evaluarse "
            "por variable dentro del pipeline de modelado."
        )


    gaps = temporal_gap_table(
        dataframe
    )


    interpretations[
        "temporal"
    ] = (
        "Se detectaron "
        f"{len(gaps)} interrupciones internas "
        "mayores a una hora en la secuencia temporal. "
        "La validación posterior debe conservar el orden "
        "cronológico y utilizar particiones temporales."
    )


    target = target_distribution_summary(
        dataframe
    )


    if target:

        interpretations[
            "target"
        ] = (
            "La variable objetivo representa el cambio "
            "de humedad del suelo a +24 horas. "
            f"Su media es {target['mean']:.6f}, "
            f"la mediana {target['median']:.6f} y "
            f"la desviación estándar {target['std']:.6f}. "
            f"El {target['negative_percent']:.2f}% de las "
            "observaciones presenta disminución y "
            f"el {target['positive_percent']:.2f}% "
            "presenta incremento. "
            "Esta descripción caracteriza la distribución "
            "del objetivo, pero no implica por sí sola "
            "capacidad predictiva."
        )


    correlations = (
        predictor_target_correlations(
            dataframe
        )
    )


    if not correlations.empty:

        top = (
            correlations
            .head(
                5
            )
        )


        detail = "; ".join(
            (
                f"{row.feature}: "
                f"{row.correlation:+.3f}"
            )

            for row
            in top.itertuples()
        )


        interpretations[
            "correlation"
        ] = (
            "Las mayores correlaciones lineales absolutas "
            "con el cambio de humedad a +24 h son: "
            f"{detail}. "
            "Estas asociaciones son descriptivas; "
            "correlación no significa causalidad y tampoco "
            "sustituye métodos de explicabilidad como "
            "Permutation Importance o SHAP."
        )


    return interpretations


# =========================================================
# COMPLETE EDA PACKAGE
# =========================================================

def build_eda_package(
    dataframe: pd.DataFrame,
) -> dict:

    return {

        "overview":
            dataset_overview(
                dataframe
            ),

        "schema":
            schema_audit(
                dataframe
            ),

        "missing":
            missing_values_table(
                dataframe
            ),

        "quality_issues":
            data_quality_issues(
                dataframe
            ),

        "physical_checks":
            physical_quality_checks(
                dataframe
            ),

        "temporal_coverage":
            temporal_coverage_by_year(
                dataframe
            ),

        "temporal_gaps":
            temporal_gap_table(
                dataframe
            ),

        "numeric_summary":
            numeric_summary(
                dataframe,
                columns=(
                    RAW_VARIABLES
                    + [
                        FUTURE_SOIL_MOISTURE,
                        DELTA_TARGET,
                    ]
                ),
            ),

        "outliers":
            outlier_summary_iqr(
                dataframe
            ),

        "annual_summary":
            annual_summary(
                dataframe
            ),

        "monthly_summary":
            monthly_summary(
                dataframe
            ),

        "hourly_profile":
            hourly_profile(
                dataframe
            ),

        "correlation_matrix":
            correlation_matrix(
                dataframe
            ),

        "target_correlations":
            predictor_target_correlations(
                dataframe
            ),

        "target_distribution":
            target_distribution_summary(
                dataframe
            ),

        "interpretations":
            build_eda_interpretations(
                dataframe
            ),
    }


# =========================================================
# COMMAND-LINE AUDIT
# =========================================================

def main() -> None:

    print()
    print(
        "=" * 72
    )

    print(
        "AGROTWIN · CRISP-DM DATA AUDIT"
    )

    print(
        "=" * 72
    )


    dataframe = (
        load_training_dataset()
    )


    package = (
        build_eda_package(
            dataframe
        )
    )


    overview = (
        package[
            "overview"
        ]
    )


    print()
    print(
        "DATASET"
    )

    print(
        "-" * 72
    )


    for key, value in (
        overview.items()
    ):

        print(
            f"{key}: {value}"
        )


    print()
    print(
        "QUALITY ISSUES"
    )

    print(
        "-" * 72
    )

    print(
        package[
            "quality_issues"
        ].to_string(
            index=False
        )
    )


    print()
    print(
        "PHYSICAL CHECKS"
    )

    print(
        "-" * 72
    )

    print(
        package[
            "physical_checks"
        ].to_string(
            index=False
        )
    )


    print()
    print(
        "TEMPORAL COVERAGE"
    )

    print(
        "-" * 72
    )

    print(
        package[
            "temporal_coverage"
        ].to_string(
            index=False
        )
    )


    print()
    print(
        "TOP MISSING VALUES"
    )

    print(
        "-" * 72
    )

    print(
        package[
            "missing"
        ]
        .head(
            10
        )
        .to_string(
            index=False
        )
    )


    print()
    print(
        "TARGET CORRELATIONS"
    )

    print(
        "-" * 72
    )

    print(
        package[
            "target_correlations"
        ]
        .head(
            10
        )
        .to_string(
            index=False
        )
    )


    print()
    print(
        "INTERPRETATIONS"
    )

    print(
        "-" * 72
    )


    for key, text in (
        package[
            "interpretations"
        ]
        .items()
    ):

        print()
        print(
            f"[{key.upper()}]"
        )

        print(
            text
        )


    print()
    print(
        "=" * 72
    )

    print(
        "AUDIT COMPLETE"
    )

    print(
        "=" * 72
    )


if __name__ == "__main__":

    main()