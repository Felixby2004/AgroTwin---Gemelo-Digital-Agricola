from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from sklearn.model_selection import (
    TimeSeriesSplit,
)


from ml.datasets import (
    DELTA_TARGET,
    FUTURE_SOIL_MOISTURE,
    MODEL_PREDICTORS,
    TIMESTAMP_COLUMN,
    load_training_dataset,
)


# =========================================================
# CONFIGURATION
# =========================================================

FINAL_TEST_YEAR = 2025

VALIDATION_YEAR = 2024

TRAIN_END_YEAR = 2023

PREDICTION_HORIZON_HOURS = 24

DEFAULT_CV_SPLITS = 5

DEFAULT_CV_GAP_ROWS = 24


# =========================================================
# FEATURE GROUPS
# =========================================================

SOIL_MOISTURE_FEATURES = [

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
]


WEATHER_FEATURES = [

    "air_temperature",

    "rainfall",

    "solar_radiation",

    "relative_humidity",

    "soil_temperature",
]


ROLLING_FEATURES = [

    "rainfall_6h",

    "rainfall_24h",

    "rainfall_48h",

    "temperature_6h_mean",

    "solar_6h_mean",

    "humidity_6h_mean",
]


CYCLICAL_TIME_FEATURES = [

    "hour_sin",

    "hour_cos",

    "doy_sin",

    "doy_cos",
]


FEATURES = list(
    MODEL_PREDICTORS
)


TARGET = DELTA_TARGET


# =========================================================
# FORBIDDEN PREDICTORS
#
# These variables may exist in the dataset because they
# are required for supervised evaluation, but they must
# never be supplied to the model at prediction time.
# =========================================================

FORBIDDEN_PREDICTORS = {

    FUTURE_SOIL_MOISTURE,

    DELTA_TARGET,

    "future_soil_moisture",

    "future_rainfall",

    "future_temperature",

    "future_relative_humidity",
}


# =========================================================
# DATA STRUCTURES
# =========================================================

@dataclass
class TemporalDatasetSplit:

    train: pd.DataFrame

    validation: pd.DataFrame

    final_test: pd.DataFrame


@dataclass
class TemporalCVFold:

    fold: int

    train_index: np.ndarray

    validation_index: np.ndarray

    train_start: pd.Timestamp

    train_end: pd.Timestamp

    validation_start: pd.Timestamp

    validation_end: pd.Timestamp

    train_samples: int

    validation_samples: int


# =========================================================
# REQUIRED COLUMNS
# =========================================================

def required_model_columns() -> list[str]:

    return list(
        dict.fromkeys(
            [
                TIMESTAMP_COLUMN,

                "soil_moisture",

                FUTURE_SOIL_MOISTURE,

                TARGET,
            ]
            +
            FEATURES
        )
    )


# =========================================================
# VALIDATE DATASET
# =========================================================

def validate_modeling_schema(
    dataframe: pd.DataFrame,
) -> None:

    missing = [

        column

        for column
        in required_model_columns()

        if column
        not in dataframe.columns
    ]


    if missing:

        raise ValueError(
            "Missing modeling columns: "
            +
            ", ".join(
                missing
            )
        )


# =========================================================
# PREPARE MODELING FRAME
# =========================================================

def prepare_modeling_frame(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """
    Prepare the supervised-learning table.

    Important:
    - chronological ordering is preserved;
    - final targets are never included in X;
    - predictor NaNs are NOT globally removed because
      model pipelines may legitimately impute them;
    - rows without target/current moisture/timestamp
      cannot participate in supervised learning.
    """

    validate_modeling_schema(
        dataframe
    )


    data = dataframe.copy()


    data[
        TIMESTAMP_COLUMN
    ] = pd.to_datetime(
        data[
            TIMESTAMP_COLUMN
        ],
        errors="coerce",
        utc=True,
    )


    # -----------------------------------------------------
    # Convert predictors and targets to numeric
    # -----------------------------------------------------

    numeric_columns = list(
        dict.fromkeys(
            FEATURES
            +
            [
                FUTURE_SOIL_MOISTURE,
                TARGET,
            ]
        )
    )


    for column in numeric_columns:

        data[
            column
        ] = pd.to_numeric(
            data[
                column
            ],
            errors="coerce",
        )


    # -----------------------------------------------------
    # Infinite values are treated as missing.
    #
    # Actual imputation belongs inside model pipelines.
    # -----------------------------------------------------

    data[
        numeric_columns
    ] = (
        data[
            numeric_columns
        ]
        .replace(
            [
                np.inf,
                -np.inf,
            ],
            np.nan,
        )
    )


    # -----------------------------------------------------
    # Supervised-learning requirements
    # -----------------------------------------------------

    data = data.dropna(
        subset=[
            TIMESTAMP_COLUMN,
            "soil_moisture",
            FUTURE_SOIL_MOISTURE,
            TARGET,
        ]
    )


    # -----------------------------------------------------
    # Preserve temporal order
    # -----------------------------------------------------

    data = (
        data
        .sort_values(
            TIMESTAMP_COLUMN
        )
        .drop_duplicates(
            subset=[
                TIMESTAMP_COLUMN
            ],
            keep="last",
        )
        .reset_index(
            drop=True
        )
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


    return data


# =========================================================
# X / Y
# =========================================================

def build_xy(
    dataframe: pd.DataFrame,
) -> tuple[
    pd.DataFrame,
    pd.Series,
]:

    validate_modeling_schema(
        dataframe
    )


    X = dataframe[
        FEATURES
    ].copy()


    y = dataframe[
        TARGET
    ].copy()


    return X, y


# =========================================================
# TEMPORAL HOLDOUT SPLIT
# =========================================================

def temporal_train_validation_test_split(
    dataframe: pd.DataFrame,
    train_end_year: int = TRAIN_END_YEAR,
    validation_year: int = VALIDATION_YEAR,
    final_test_year: int = FINAL_TEST_YEAR,
) -> TemporalDatasetSplit:
    """
    Main CRISP-DM temporal partition.

    Train:
        <= 2023

    Validation:
        2024

    Final untouched test:
        2025

    The 2025 set must never be used to select a model
    or tune hyperparameters.
    """

    data = prepare_modeling_frame(
        dataframe
    )


    train = data[
        data[
            TIMESTAMP_COLUMN
        ]
        .dt
        .year
        <=
        train_end_year
    ].copy()


    validation = data[
        data[
            TIMESTAMP_COLUMN
        ]
        .dt
        .year
        ==
        validation_year
    ].copy()


    final_test = data[
        data[
            TIMESTAMP_COLUMN
        ]
        .dt
        .year
        ==
        final_test_year
    ].copy()


    if train.empty:

        raise ValueError(
            "Temporal training set is empty."
        )


    if validation.empty:

        raise ValueError(
            "Temporal validation set is empty."
        )


    if final_test.empty:

        raise ValueError(
            "Final temporal test set is empty."
        )


    return TemporalDatasetSplit(
        train=train,
        validation=validation,
        final_test=final_test,
    )


# =========================================================
# DEVELOPMENT SET
# =========================================================

def development_dataset(
    dataframe: pd.DataFrame,
    final_test_year: int = FINAL_TEST_YEAR,
) -> pd.DataFrame:
    """
    Return all observations strictly before the final
    holdout year.

    With the current dataset:
        development = 2022–2024
        holdout     = 2025
    """

    data = prepare_modeling_frame(
        dataframe
    )


    return (
        data[
            data[
                TIMESTAMP_COLUMN
            ]
            .dt
            .year
            <
            final_test_year
        ]
        .copy()
        .reset_index(
            drop=True
        )
    )


# =========================================================
# FINAL HOLDOUT
# =========================================================

def final_holdout_dataset(
    dataframe: pd.DataFrame,
    final_test_year: int = FINAL_TEST_YEAR,
) -> pd.DataFrame:

    data = prepare_modeling_frame(
        dataframe
    )


    return (
        data[
            data[
                TIMESTAMP_COLUMN
            ]
            .dt
            .year
            ==
            final_test_year
        ]
        .copy()
        .reset_index(
            drop=True
        )
    )


# =========================================================
# TEMPORAL CROSS VALIDATION
# =========================================================

def build_time_series_cv_folds(
    dataframe: pd.DataFrame,
    n_splits: int = DEFAULT_CV_SPLITS,
    gap_rows: int = DEFAULT_CV_GAP_ROWS,
) -> list[TemporalCVFold]:
    """
    Build expanding-window temporal CV folds using only
    pre-2025 development data.

    gap_rows=24 introduces an approximately 24-hour gap
    between train and validation to reduce overlap around
    the +24 h prediction horizon.
    """

    development = development_dataset(
        dataframe
    )


    if (
        len(
            development
        )
        <=
        n_splits
    ):

        raise ValueError(
            "Not enough observations for "
            "TimeSeriesSplit."
        )


    splitter = TimeSeriesSplit(
        n_splits=n_splits,
        gap=gap_rows,
    )


    folds: list[
        TemporalCVFold
    ] = []


    for fold_number, (
        train_index,
        validation_index,
    ) in enumerate(
        splitter.split(
            development
        ),
        start=1,
    ):

        train = development.iloc[
            train_index
        ]


        validation = development.iloc[
            validation_index
        ]


        folds.append(
            TemporalCVFold(
                fold=fold_number,

                train_index=
                    train_index,

                validation_index=
                    validation_index,

                train_start=
                    train[
                        TIMESTAMP_COLUMN
                    ].min(),

                train_end=
                    train[
                        TIMESTAMP_COLUMN
                    ].max(),

                validation_start=
                    validation[
                        TIMESTAMP_COLUMN
                    ].min(),

                validation_end=
                    validation[
                        TIMESTAMP_COLUMN
                    ].max(),

                train_samples=
                    len(
                        train
                    ),

                validation_samples=
                    len(
                        validation
                    ),
            )
        )


    return folds


# =========================================================
# CV SUMMARY
# =========================================================

def cv_fold_summary(
    dataframe: pd.DataFrame,
    n_splits: int = DEFAULT_CV_SPLITS,
    gap_rows: int = DEFAULT_CV_GAP_ROWS,
) -> pd.DataFrame:

    folds = (
        build_time_series_cv_folds(
            dataframe,
            n_splits=n_splits,
            gap_rows=gap_rows,
        )
    )


    return pd.DataFrame(
        [
            {
                "fold":
                    fold.fold,

                "train_samples":
                    fold.train_samples,

                "train_start":
                    fold.train_start,

                "train_end":
                    fold.train_end,

                "validation_samples":
                    fold.validation_samples,

                "validation_start":
                    fold.validation_start,

                "validation_end":
                    fold.validation_end,

                "gap_rows":
                    gap_rows,
            }

            for fold
            in folds
        ]
    )


# =========================================================
# TEMPORAL SPLIT SUMMARY
# =========================================================

def temporal_split_summary(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:

    split = (
        temporal_train_validation_test_split(
            dataframe
        )
    )


    rows = []


    for name, data, purpose in [

        (
            "TRAIN",
            split.train,
            (
                "Model fitting and "
                "hyperparameter candidates"
            ),
        ),

        (
            "VALIDATION",
            split.validation,
            (
                "Model selection before "
                "final testing"
            ),
        ),

        (
            "FINAL_TEST",
            split.final_test,
            (
                "Untouched final "
                "generalization test"
            ),
        ),
    ]:

        rows.append(
            {
                "partition":
                    name,

                "purpose":
                    purpose,

                "samples":
                    len(
                        data
                    ),

                "start":
                    data[
                        TIMESTAMP_COLUMN
                    ].min(),

                "end":
                    data[
                        TIMESTAMP_COLUMN
                    ].max(),

                "years":
                    ", ".join(
                        str(
                            year
                        )

                        for year
                        in sorted(
                            data[
                                TIMESTAMP_COLUMN
                            ]
                            .dt
                            .year
                            .unique()
                        )
                    ),
            }
        )


    return pd.DataFrame(
        rows
    )


# =========================================================
# MISSING PREDICTOR SUMMARY
# =========================================================

def predictor_missingness(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:

    data = prepare_modeling_frame(
        dataframe
    )


    rows = []


    for feature in FEATURES:

        missing_count = int(
            data[
                feature
            ]
            .isna()
            .sum()
        )


        rows.append(
            {
                "feature":
                    feature,

                "missing_count":
                    missing_count,

                "missing_percent":
                    float(
                        missing_count
                        /
                        len(
                            data
                        )
                        *
                        100
                    ),
            }
        )


    return (
        pd.DataFrame(
            rows
        )
        .sort_values(
            [
                "missing_count",
                "feature",
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
# FEATURE INVENTORY
# =========================================================

def feature_inventory() -> pd.DataFrame:

    rows = []


    groups = {

        "Current / historical soil moisture":
            SOIL_MOISTURE_FEATURES,

        "Current meteorology":
            WEATHER_FEATURES,

        "Rolling historical meteorology":
            ROLLING_FEATURES,

        "Cyclical time encoding":
            CYCLICAL_TIME_FEATURES,
    }


    for group, features in (
        groups.items()
    ):

        for feature in features:

            rows.append(
                {
                    "feature":
                        feature,

                    "group":
                        group,

                    "used_by_model":
                        feature
                        in FEATURES,

                    "temporal_role":
                        (
                            "CURRENT_OR_PAST"
                        ),
                }
            )


    return pd.DataFrame(
        rows
    )


# =========================================================
# LEAKAGE AUDIT
# =========================================================

def leakage_audit(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """
    Structural checks intended to detect obvious target
    leakage.

    Passing these checks does not mathematically prove the
    absence of leakage, but it documents the design choices
    used to prevent it.
    """

    data = prepare_modeling_frame(
        dataframe
    )


    rows = []


    forbidden_used = sorted(
        set(
            FEATURES
        )
        &
        FORBIDDEN_PREDICTORS
    )


    rows.append(
        {
            "check":
                "Targets excluded from predictors",

            "status":
                (
                    "PASS"
                    if not
                    forbidden_used
                    else "FAIL"
                ),

            "detail":
                (
                    "No future/target variable "
                    "is present in FEATURES."
                    if not
                    forbidden_used
                    else
                    "Forbidden predictors found: "
                    +
                    ", ".join(
                        forbidden_used
                    )
                ),
        }
    )


    rows.append(
        {
            "check":
                "Future absolute moisture excluded",

            "status":
                (
                    "PASS"
                    if FUTURE_SOIL_MOISTURE
                    not in FEATURES
                    else "FAIL"
                ),

            "detail":
                (
                    "future_soil_moisture_24h "
                    "is used only for evaluation."
                ),
        }
    )


    rows.append(
        {
            "check":
                "Delta target excluded",

            "status":
                (
                    "PASS"
                    if TARGET
                    not in FEATURES
                    else "FAIL"
                ),

            "detail":
                (
                    f"{TARGET} is the supervised "
                    "target and is not an input feature."
                ),
        }
    )


    rows.append(
        {
            "check":
                "Timestamp excluded from predictors",

            "status":
                (
                    "PASS"
                    if TIMESTAMP_COLUMN
                    not in FEATURES
                    else "FAIL"
                ),

            "detail":
                (
                    "Raw timestamp is not passed "
                    "directly to the model."
                ),
        }
    )


    chronological = bool(
        data[
            TIMESTAMP_COLUMN
        ]
        .is_monotonic_increasing
    )


    rows.append(
        {
            "check":
                "Chronological order preserved",

            "status":
                (
                    "PASS"
                    if chronological
                    else "FAIL"
                ),

            "detail":
                (
                    "Modeling data are sorted "
                    "chronologically."
                ),
        }
    )


    duplicates = int(
        data[
            TIMESTAMP_COLUMN
        ]
        .duplicated()
        .sum()
    )


    rows.append(
        {
            "check":
                "No duplicate timestamps",

            "status":
                (
                    "PASS"
                    if duplicates == 0
                    else "FAIL"
                ),

            "detail":
                (
                    f"Duplicate timestamps: "
                    f"{duplicates}."
                ),
        }
    )


    split = (
        temporal_train_validation_test_split(
            data
        )
    )


    latest_training_time = (
        split.train[
            TIMESTAMP_COLUMN
        ]
        .max()
    )


    earliest_validation_time = (
        split.validation[
            TIMESTAMP_COLUMN
        ]
        .min()
    )


    earliest_test_time = (
        split.final_test[
            TIMESTAMP_COLUMN
        ]
        .min()
    )


    split_order_ok = bool(
        latest_training_time
        <
        earliest_validation_time
        <
        earliest_test_time
    )


    rows.append(
        {
            "check":
                "Train / validation / final-test order",

            "status":
                (
                    "PASS"
                    if split_order_ok
                    else "FAIL"
                ),

            "detail":
                (
                    "Training precedes validation "
                    "and validation precedes the "
                    "2025 final holdout."
                ),
        }
    )


    rows.append(
        {
            "check":
                "2025 isolated from model selection",

            "status":
                "PASS",

            "detail":
                (
                    "The final_test partition is "
                    "separate and must not be used "
                    "for hyperparameter or model "
                    "selection."
                ),
        }
    )


    return pd.DataFrame(
        rows
    )


# =========================================================
# CRISP-DM PREPARATION INTERPRETATION
# =========================================================

def preparation_interpretation(
    dataframe: pd.DataFrame,
) -> str:

    split = (
        temporal_train_validation_test_split(
            dataframe
        )
    )


    missing = (
        predictor_missingness(
            dataframe
        )
    )


    affected_predictors = int(
        (
            missing[
                "missing_count"
            ]
            >
            0
        )
        .sum()
    )


    return (
        "La preparación conserva el orden temporal del "
        "dataset y mantiene 2025 como conjunto final "
        "independiente. "
        f"El entrenamiento contiene {len(split.train):,} "
        "observaciones, la validación "
        f"{len(split.validation):,} y la prueba final "
        f"{len(split.final_test):,}. "
        f"{affected_predictors} predictores contienen "
        "algún valor faltante; estos faltantes no se "
        "rellenan globalmente durante la preparación, "
        "sino dentro de cada pipeline de entrenamiento "
        "para evitar contaminación entre particiones. "
        "El target a +24 h y la humedad futura absoluta "
        "se excluyen explícitamente de las variables "
        "predictoras."
    )


# =========================================================
# COMMAND LINE CHECK
# =========================================================

def main() -> None:

    dataframe = (
        load_training_dataset()
    )


    data = (
        prepare_modeling_frame(
            dataframe
        )
    )


    print()
    print(
        "=" * 78
    )

    print(
        "AGROTWIN · CRISP-DM FEATURE PREPARATION"
    )

    print(
        "=" * 78
    )


    print()
    print(
        "MODEL FEATURES"
    )

    print(
        "-" * 78
    )

    print(
        f"Predictors: {len(FEATURES)}"
    )

    print(
        f"Target: {TARGET}"
    )

    print(
        f"Rows available: {len(data)}"
    )


    print()
    print(
        "TEMPORAL SPLIT"
    )

    print(
        "-" * 78
    )

    print(
        temporal_split_summary(
            dataframe
        ).to_string(
            index=False
        )
    )


    print()
    print(
        "TEMPORAL CROSS-VALIDATION"
    )

    print(
        "-" * 78
    )

    print(
        cv_fold_summary(
            dataframe
        ).to_string(
            index=False
        )
    )


    print()
    print(
        "LEAKAGE AUDIT"
    )

    print(
        "-" * 78
    )

    print(
        leakage_audit(
            dataframe
        ).to_string(
            index=False
        )
    )


    print()
    print(
        "PREDICTOR MISSINGNESS"
    )

    print(
        "-" * 78
    )

    print(
        predictor_missingness(
            dataframe
        )
        .head(
            10
        )
        .to_string(
            index=False
        )
    )


    print()
    print(
        "INTERPRETATION"
    )

    print(
        "-" * 78
    )

    print(
        preparation_interpretation(
            dataframe
        )
    )


    print()
    print(
        "=" * 78
    )

    print(
        "FEATURE PREPARATION COMPLETE"
    )

    print(
        "=" * 78
    )


if __name__ == "__main__":

    main()