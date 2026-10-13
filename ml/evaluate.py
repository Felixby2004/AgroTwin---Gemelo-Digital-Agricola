from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
import json

import joblib
import numpy as np
import pandas as pd

from scipy.stats import (
    friedmanchisquare,
    kurtosis,
    norm,
    normaltest,
    skew,
    wilcoxon,
)

from sklearn.pipeline import Pipeline


from ml.datasets import (
    FUTURE_SOIL_MOISTURE,
    TIMESTAMP_COLUMN,
    load_training_dataset,
)

from ml.features import (
    FEATURES,
    TARGET,
    build_time_series_cv_folds,
    development_dataset,
    final_holdout_dataset,
)

from ml.train import (
    RANDOM_STATE,
    RegressionMetrics,
    build_candidates,
    calculate_metrics,
    reconstruct_future_moisture,
)


# =========================================================
# PATHS
# =========================================================

PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parent
    .parent
)


EXPERIMENT_DIR = (
    PROJECT_ROOT
    / "artifacts"
    / "ml"
    / "crisp_dm"
)


MODEL_SELECTION_METADATA_PATH = (
    EXPERIMENT_DIR
    / "model_selection_metadata.json"
)


CV_METRICS_PATH = (
    EXPERIMENT_DIR
    / "cv_fold_metrics.csv"
)


CV_PREDICTIONS_PATH = (
    EXPERIMENT_DIR
    / "cv_predictions.csv"
)


FRIEDMAN_PATH = (
    EXPERIMENT_DIR
    / "friedman_test.json"
)


PAIRWISE_TESTS_PATH = (
    EXPERIMENT_DIR
    / "pairwise_statistical_tests.csv"
)


FINAL_TEST_METRICS_PATH = (
    EXPERIMENT_DIR
    / "final_test_metrics.csv"
)


FINAL_TEST_PREDICTIONS_PATH = (
    EXPERIMENT_DIR
    / "final_test_predictions.csv"
)


BOOTSTRAP_PATH = (
    EXPERIMENT_DIR
    / "bootstrap_confidence_intervals.json"
)


RESIDUAL_DIAGNOSTICS_PATH = (
    EXPERIMENT_DIR
    / "residual_diagnostics.json"
)


FINAL_SELECTED_MODEL_PATH = (
    EXPERIMENT_DIR
    / "final_selected_model.joblib"
)


EVALUATION_SUMMARY_PATH = (
    EXPERIMENT_DIR
    / "evaluation_summary.json"
)


# =========================================================
# CONFIGURATION
# =========================================================

N_CV_SPLITS = 5

CV_GAP_ROWS = 24

DM_HAC_LAG = 24

BOOTSTRAP_ITERATIONS = 2000

BOOTSTRAP_CONFIDENCE = 0.95


# =========================================================
# HELPERS
# =========================================================

def safe_model_name(
    model_name: str,
) -> str:

    return (
        model_name
        .lower()
        .replace(
            " ",
            "_",
        )
        .replace(
            "-",
            "_",
        )
    )


def load_selected_model_name() -> str:

    if not MODEL_SELECTION_METADATA_PATH.exists():

        raise FileNotFoundError(
            "Model-selection metadata was not found. "
            "Run `python -m ml.train` first."
        )


    metadata = json.loads(
        MODEL_SELECTION_METADATA_PATH.read_text(
            encoding="utf-8",
        )
    )


    selected_model = metadata.get(
        "selected_model"
    )


    if not selected_model:

        raise ValueError(
            "selected_model is missing from "
            "model_selection_metadata.json."
        )


    return str(
        selected_model
    )


# =========================================================
# EVALUATE ONE MODEL
# =========================================================

def evaluate_pipeline(
    pipeline: Pipeline,
    train: pd.DataFrame,
    test: pd.DataFrame,
) -> tuple[
    RegressionMetrics,
    np.ndarray,
]:

    X_train = train[
        FEATURES
    ]


    y_train = train[
        TARGET
    ]


    X_test = test[
        FEATURES
    ]


    pipeline.fit(
        X_train,
        y_train,
    )


    predicted_delta = (
        pipeline.predict(
            X_test
        )
    )


    current_moisture = (
        test[
            "soil_moisture"
        ]
        .to_numpy(
            dtype=float,
        )
    )


    predicted_future = (
        reconstruct_future_moisture(
            current_moisture=
                current_moisture,

            predicted_delta=
                predicted_delta,
        )
    )


    observed_future = (
        test[
            FUTURE_SOIL_MOISTURE
        ]
        .to_numpy(
            dtype=float,
        )
    )


    metrics = (
        calculate_metrics(
            observed_future,
            predicted_future,
        )
    )


    return (
        metrics,
        predicted_future,
    )


# =========================================================
# TEMPORAL CROSS VALIDATION
# =========================================================

def run_temporal_cross_validation(
    dataframe: pd.DataFrame,
) -> tuple[
    pd.DataFrame,
    pd.DataFrame,
]:

    development = (
        development_dataset(
            dataframe
        )
    )


    folds = (
        build_time_series_cv_folds(
            dataframe,
            n_splits=N_CV_SPLITS,
            gap_rows=CV_GAP_ROWS,
        )
    )


    metric_rows = []

    prediction_frames = []


    for fold in folds:

        train = development.iloc[
            fold.train_index
        ].copy()


        validation = development.iloc[
            fold.validation_index
        ].copy()


        observed = (
            validation[
                FUTURE_SOIL_MOISTURE
            ]
            .to_numpy(
                dtype=float,
            )
        )


        current = (
            validation[
                "soil_moisture"
            ]
            .to_numpy(
                dtype=float,
            )
        )


        # -------------------------------------------------
        # Persistence baseline
        # -------------------------------------------------

        persistence_predictions = (
            current.copy()
        )


        persistence_metrics = (
            calculate_metrics(
                observed,
                persistence_predictions,
            )
        )


        metric_rows.append(
            {
                "fold":
                    fold.fold,

                "model_name":
                    "Persistence",

                **asdict(
                    persistence_metrics
                ),

                "train_samples":
                    fold.train_samples,

                "validation_samples":
                    fold.validation_samples,

                "train_start":
                    fold.train_start,

                "train_end":
                    fold.train_end,

                "validation_start":
                    fold.validation_start,

                "validation_end":
                    fold.validation_end,
            }
        )


        prediction_table = pd.DataFrame(
            {
                "fold":
                    fold.fold,

                "timestamp":
                    validation[
                        TIMESTAMP_COLUMN
                    ]
                    .reset_index(
                        drop=True
                    ),

                "observed":
                    observed,

                "current_soil_moisture":
                    current,

                "persistence_prediction":
                    persistence_predictions,

                "persistence_absolute_error":
                    np.abs(
                        observed
                        -
                        persistence_predictions
                    ),

                "persistence_squared_error":
                    (
                        observed
                        -
                        persistence_predictions
                    )
                    ** 2,
            }
        )


        # -------------------------------------------------
        # ML candidates
        # -------------------------------------------------

        candidates = (
            build_candidates()
        )


        for (
            model_name,
            pipeline,
        ) in candidates.items():

            (
                metrics,
                predictions,
            ) = evaluate_pipeline(
                pipeline=
                    pipeline,

                train=
                    train,

                test=
                    validation,
            )


            metric_rows.append(
                {
                    "fold":
                        fold.fold,

                    "model_name":
                        model_name,

                    **asdict(
                        metrics
                    ),

                    "train_samples":
                        fold.train_samples,

                    "validation_samples":
                        fold.validation_samples,

                    "train_start":
                        fold.train_start,

                    "train_end":
                        fold.train_end,

                    "validation_start":
                        fold.validation_start,

                    "validation_end":
                        fold.validation_end,
                }
            )


            safe_name = (
                safe_model_name(
                    model_name
                )
            )


            prediction_table[
                f"{safe_name}_prediction"
            ] = predictions


            prediction_table[
                f"{safe_name}_absolute_error"
            ] = np.abs(
                observed
                -
                predictions
            )


            prediction_table[
                f"{safe_name}_squared_error"
            ] = (
                observed
                -
                predictions
            ) ** 2


        prediction_frames.append(
            prediction_table
        )


    metrics_table = pd.DataFrame(
        metric_rows
    )


    predictions_table = pd.concat(
        prediction_frames,
        ignore_index=True,
    )


    return (
        metrics_table,
        predictions_table,
    )


# =========================================================
# CROSS-VALIDATION SUMMARY
# =========================================================

def summarize_cv_metrics(
    metrics: pd.DataFrame,
) -> pd.DataFrame:

    summary = (
        metrics
        .groupby(
            "model_name",
            as_index=False,
        )
        .agg(
            mae_mean=(
                "mae",
                "mean",
            ),
            mae_std=(
                "mae",
                "std",
            ),
            rmse_mean=(
                "rmse",
                "mean",
            ),
            rmse_std=(
                "rmse",
                "std",
            ),
            r2_mean=(
                "r2",
                "mean",
            ),
            r2_std=(
                "r2",
                "std",
            ),
            bias_mean=(
                "bias",
                "mean",
            ),
        )
    )


    return (
        summary
        .sort_values(
            [
                "mae_mean",
                "rmse_mean",
            ]
        )
        .reset_index(
            drop=True
        )
    )


# =========================================================
# DAILY BLOCK ERRORS
#
# Statistical tests use daily blocks rather than treating
# every hourly sample as independent.
# =========================================================

def build_daily_error_table(
    predictions: pd.DataFrame,
) -> pd.DataFrame:

    data = predictions.copy()


    data[
        "date"
    ] = (
        pd.to_datetime(
            data[
                "timestamp"
            ],
            utc=True,
        )
        .dt
        .floor(
            "D"
        )
    )


    error_columns = [

        column

        for column
        in data.columns

        if column.endswith(
            "_absolute_error"
        )
    ]


    daily = (
        data
        .groupby(
            "date",
            as_index=False,
        )[
            error_columns
        ]
        .mean()
    )


    return daily


# =========================================================
# FRIEDMAN TEST
# =========================================================

def run_friedman_test(
    predictions: pd.DataFrame,
) -> dict:

    daily = (
        build_daily_error_table(
            predictions
        )
    )


    error_columns = [

        column

        for column
        in daily.columns

        if column.endswith(
            "_absolute_error"
        )
    ]


    complete = (
        daily[
            error_columns
        ]
        .dropna()
    )


    if (
        len(
            error_columns
        )
        <
        3
        or
        len(
            complete
        )
        <
        5
    ):

        return {
            "test":
                "Friedman",

            "status":
                "NOT_ENOUGH_DATA",

            "statistic":
                None,

            "p_value":
                None,

            "alpha":
                0.05,

            "significant":
                None,

            "blocks":
                int(
                    len(
                        complete
                    )
                ),

            "models":
                error_columns,
        }


    arrays = [

        complete[
            column
        ]
        .to_numpy(
            dtype=float
        )

        for column
        in error_columns
    ]


    result = (
        friedmanchisquare(
            *arrays
        )
    )


    p_value = float(
        result.pvalue
    )


    return {
        "test":
            "Friedman",

        "unit_of_analysis":
            "daily mean absolute error",

        "statistic":
            float(
                result.statistic
            ),

        "p_value":
            p_value,

        "alpha":
            0.05,

        "significant":
            bool(
                p_value
                <
                0.05
            ),

        "blocks":
            int(
                len(
                    complete
                )
            ),

        "models":
            error_columns,

        "interpretation":
            (
                "The null hypothesis states that all "
                "forecasting methods have the same "
                "error distribution across daily blocks."
            ),
    }


# =========================================================
# HOLM CORRECTION
# =========================================================

def holm_adjust(
    p_values: list[float],
) -> list[float]:

    if not p_values:
        return []


    p_array = np.asarray(
        p_values,
        dtype=float,
    )


    order = np.argsort(
        p_array
    )


    adjusted = np.empty_like(
        p_array
    )


    running_max = 0.0

    m = len(
        p_array
    )


    for rank, index in enumerate(
        order
    ):

        multiplier = (
            m
            -
            rank
        )


        corrected = min(
            1.0,
            float(
                p_array[
                    index
                ]
                *
                multiplier
            ),
        )


        running_max = max(
            running_max,
            corrected,
        )


        adjusted[
            index
        ] = running_max


    return adjusted.tolist()


# =========================================================
# WILCOXON
# =========================================================

def wilcoxon_pair(
    selected_errors: np.ndarray,
    comparator_errors: np.ndarray,
) -> tuple[
    float,
    float,
]:

    selected = np.asarray(
        selected_errors,
        dtype=float,
    )


    comparator = np.asarray(
        comparator_errors,
        dtype=float,
    )


    difference = (
        selected
        -
        comparator
    )


    if np.allclose(
        difference,
        0.0,
    ):

        return (
            0.0,
            1.0,
        )


    result = wilcoxon(
        selected,
        comparator,
        alternative="two-sided",
        zero_method="pratt",
        method="auto",
    )


    return (
        float(
            result.statistic
        ),
        float(
            result.pvalue
        ),
    )


# =========================================================
# DIEBOLD-MARIANO TEST
#
# Uses a Newey-West / HAC estimate to account for serial
# dependence in forecast-loss differentials.
# =========================================================

def diebold_mariano_test(
    selected_loss: np.ndarray,
    comparator_loss: np.ndarray,
    hac_lag: int = DM_HAC_LAG,
) -> dict:

    selected = np.asarray(
        selected_loss,
        dtype=float,
    )


    comparator = np.asarray(
        comparator_loss,
        dtype=float,
    )


    valid = (
        np.isfinite(
            selected
        )
        &
        np.isfinite(
            comparator
        )
    )


    selected = selected[
        valid
    ]


    comparator = comparator[
        valid
    ]


    loss_difference = (
        selected
        -
        comparator
    )


    n = len(
        loss_difference
    )


    if n < 30:

        return {
            "statistic":
                None,

            "p_value":
                None,

            "mean_loss_difference":
                None,

            "status":
                "NOT_ENOUGH_DATA",
        }


    mean_difference = float(
        np.mean(
            loss_difference
        )
    )


    centered = (
        loss_difference
        -
        mean_difference
    )


    # -----------------------------------------------------
    # Newey-West long-run variance
    # -----------------------------------------------------

    gamma_zero = float(
        np.dot(
            centered,
            centered,
        )
        /
        n
    )


    long_run_variance = (
        gamma_zero
    )


    max_lag = min(
        hac_lag,
        n - 1,
    )


    for lag in range(
        1,
        max_lag + 1,
    ):

        covariance = float(
            np.dot(
                centered[
                    lag:
                ],
                centered[
                    :-lag
                ],
            )
            /
            n
        )


        weight = (
            1.0
            -
            lag
            /
            (
                max_lag
                +
                1
            )
        )


        long_run_variance += (
            2.0
            *
            weight
            *
            covariance
        )


    variance_of_mean = (
        long_run_variance
        /
        n
    )


    if (
        variance_of_mean
        <=
        0
        or
        not np.isfinite(
            variance_of_mean
        )
    ):

        return {
            "statistic":
                None,

            "p_value":
                None,

            "mean_loss_difference":
                mean_difference,

            "status":
                "INVALID_VARIANCE",
        }


    statistic = (
        mean_difference
        /
        np.sqrt(
            variance_of_mean
        )
    )


    p_value = float(
        2.0
        *
        norm.sf(
            abs(
                statistic
            )
        )
    )


    return {
        "statistic":
            float(
                statistic
            ),

        "p_value":
            p_value,

        "mean_loss_difference":
            mean_difference,

        "status":
            "OK",

        "selected_better_direction":
            (
                mean_difference
                <
                0
            ),
    }


# =========================================================
# PAIRWISE STATISTICAL TESTS
# =========================================================

def run_pairwise_tests(
    predictions: pd.DataFrame,
    selected_model_name: str,
) -> pd.DataFrame:

    daily = (
        build_daily_error_table(
            predictions
        )
    )


    selected_safe = (
        safe_model_name(
            selected_model_name
        )
    )


    selected_daily_column = (
        f"{selected_safe}_absolute_error"
    )


    selected_hourly_column = (
        f"{selected_safe}_absolute_error"
    )


    if (
        selected_daily_column
        not in daily.columns
    ):

        raise ValueError(
            "Selected model errors are missing "
            "from CV predictions."
        )


    comparator_columns = [

        column

        for column
        in daily.columns

        if (
            column.endswith(
                "_absolute_error"
            )
            and
            column !=
            selected_daily_column
        )
    ]


    rows = []


    for comparator_column in comparator_columns:

        comparator_name = (
            comparator_column
            .replace(
                "_absolute_error",
                "",
            )
        )


        pair = (
            daily[
                [
                    selected_daily_column,
                    comparator_column,
                ]
            ]
            .dropna()
        )


        selected_daily = (
            pair[
                selected_daily_column
            ]
            .to_numpy(
                dtype=float,
            )
        )


        comparator_daily = (
            pair[
                comparator_column
            ]
            .to_numpy(
                dtype=float,
            )
        )


        (
            wilcoxon_statistic,
            wilcoxon_p_value,
        ) = wilcoxon_pair(
            selected_daily,
            comparator_daily,
        )


        # -------------------------------------------------
        # Hourly loss series for Diebold-Mariano
        # -------------------------------------------------

        selected_hourly = (
            predictions[
                selected_hourly_column
            ]
            .to_numpy(
                dtype=float,
            )
        )


        comparator_hourly_column = (
            comparator_column
        )


        comparator_hourly = (
            predictions[
                comparator_hourly_column
            ]
            .to_numpy(
                dtype=float,
            )
        )


        dm = (
            diebold_mariano_test(
                selected_loss=
                    selected_hourly,

                comparator_loss=
                    comparator_hourly,

                hac_lag=
                    DM_HAC_LAG,
            )
        )


        rows.append(
            {
                "selected_model":
                    selected_model_name,

                "comparator":
                    comparator_name,

                "daily_blocks":
                    len(
                        pair
                    ),

                "selected_daily_mae":
                    float(
                        np.mean(
                            selected_daily
                        )
                    ),

                "comparator_daily_mae":
                    float(
                        np.mean(
                            comparator_daily
                        )
                    ),

                "mean_daily_difference":
                    float(
                        np.mean(
                            selected_daily
                            -
                            comparator_daily
                        )
                    ),

                "median_daily_difference":
                    float(
                        np.median(
                            selected_daily
                            -
                            comparator_daily
                        )
                    ),

                "selected_daily_win_rate_percent":
                    float(
                        np.mean(
                            selected_daily
                            <
                            comparator_daily
                        )
                        *
                        100
                    ),

                "wilcoxon_statistic":
                    wilcoxon_statistic,

                "wilcoxon_p_value":
                    wilcoxon_p_value,

                "dm_statistic":
                    dm[
                        "statistic"
                    ],

                "dm_p_value":
                    dm[
                        "p_value"
                    ],

                "dm_mean_loss_difference":
                    dm[
                        "mean_loss_difference"
                    ],

                "dm_status":
                    dm[
                        "status"
                    ],
            }
        )


    result = pd.DataFrame(
        rows
    )


    if result.empty:

        return result


    result[
        "wilcoxon_p_holm"
    ] = holm_adjust(
        result[
            "wilcoxon_p_value"
        ]
        .fillna(
            1.0
        )
        .tolist()
    )


    result[
        "dm_p_holm"
    ] = holm_adjust(
        result[
            "dm_p_value"
        ]
        .fillna(
            1.0
        )
        .tolist()
    )


    result[
        "wilcoxon_significant_005"
    ] = (
        result[
            "wilcoxon_p_holm"
        ]
        <
        0.05
    )


    result[
        "dm_significant_005"
    ] = (
        result[
            "dm_p_holm"
        ]
        <
        0.05
    )


    return result


# =========================================================
# FINAL 2025 TEST
# =========================================================

def run_final_holdout_test(
    dataframe: pd.DataFrame,
    selected_model_name: str,
) -> tuple[
    pd.DataFrame,
    pd.DataFrame,
    Pipeline,
]:

    development = (
        development_dataset(
            dataframe
        )
    )


    final_test = (
        final_holdout_dataset(
            dataframe
        )
    )


    candidates = (
        build_candidates()
    )


    if (
        selected_model_name
        not in candidates
    ):

        raise ValueError(
            "Selected model is not present "
            "in build_candidates()."
        )


    selected_pipeline = (
        candidates[
            selected_model_name
        ]
    )


    (
        selected_metrics,
        selected_predictions,
    ) = evaluate_pipeline(
        pipeline=
            selected_pipeline,

        train=
            development,

        test=
            final_test,
    )


    observed = (
        final_test[
            FUTURE_SOIL_MOISTURE
        ]
        .to_numpy(
            dtype=float,
        )
    )


    current = (
        final_test[
            "soil_moisture"
        ]
        .to_numpy(
            dtype=float,
        )
    )


    persistence_predictions = (
        current.copy()
    )


    persistence_metrics = (
        calculate_metrics(
            observed,
            persistence_predictions,
        )
    )


    metrics = pd.DataFrame(
        [
            {
                "model_name":
                    selected_model_name,

                **asdict(
                    selected_metrics
                ),
            },
            {
                "model_name":
                    "Persistence",

                **asdict(
                    persistence_metrics
                ),
            },
        ]
    )


    predictions = pd.DataFrame(
        {
            "timestamp":
                final_test[
                    TIMESTAMP_COLUMN
                ]
                .reset_index(
                    drop=True
                ),

            "observed":
                observed,

            "current_soil_moisture":
                current,

            "selected_model":
                selected_model_name,

            "selected_prediction":
                selected_predictions,

            "selected_residual":
                selected_predictions
                -
                observed,

            "selected_absolute_error":
                np.abs(
                    selected_predictions
                    -
                    observed
                ),

            "selected_squared_error":
                (
                    selected_predictions
                    -
                    observed
                )
                ** 2,

            "persistence_prediction":
                persistence_predictions,

            "persistence_absolute_error":
                np.abs(
                    persistence_predictions
                    -
                    observed
                ),

            "persistence_squared_error":
                (
                    persistence_predictions
                    -
                    observed
                )
                ** 2,
        }
    )


    return (
        metrics,
        predictions,
        selected_pipeline,
    )


# =========================================================
# BLOCK BOOTSTRAP
#
# Resampling is done by day so hourly observations within
# each selected day remain together.
# =========================================================

def run_block_bootstrap(
    final_predictions: pd.DataFrame,
    iterations: int = BOOTSTRAP_ITERATIONS,
    confidence: float = BOOTSTRAP_CONFIDENCE,
) -> dict:

    data = final_predictions.copy()


    data[
        "date"
    ] = (
        pd.to_datetime(
            data[
                "timestamp"
            ],
            utc=True,
        )
        .dt
        .floor(
            "D"
        )
    )


    dates = (
        data[
            "date"
        ]
        .dropna()
        .drop_duplicates()
        .to_numpy()
    )


    if len(
        dates
    ) < 10:

        raise ValueError(
            "Not enough daily blocks for bootstrap."
        )


    groups = {

        date:
            data[
                data[
                    "date"
                ]
                ==
                date
            ]

        for date
        in dates
    }


    rng = np.random.default_rng(
        RANDOM_STATE
    )


    selected_mae_values = []

    selected_rmse_values = []

    persistence_mae_values = []

    persistence_rmse_values = []

    mae_difference_values = []

    rmse_difference_values = []


    for _ in range(
        iterations
    ):

        sampled_dates = (
            rng.choice(
                dates,
                size=len(
                    dates
                ),
                replace=True,
            )
        )


        sample = pd.concat(
            [
                groups[
                    date
                ]

                for date
                in sampled_dates
            ],
            ignore_index=True,
        )


        observed = (
            sample[
                "observed"
            ]
            .to_numpy(
                dtype=float,
            )
        )


        selected = (
            sample[
                "selected_prediction"
            ]
            .to_numpy(
                dtype=float,
            )
        )


        persistence = (
            sample[
                "persistence_prediction"
            ]
            .to_numpy(
                dtype=float,
            )
        )


        selected_metrics = (
            calculate_metrics(
                observed,
                selected,
            )
        )


        persistence_metrics = (
            calculate_metrics(
                observed,
                persistence,
            )
        )


        selected_mae_values.append(
            selected_metrics.mae
        )


        selected_rmse_values.append(
            selected_metrics.rmse
        )


        persistence_mae_values.append(
            persistence_metrics.mae
        )


        persistence_rmse_values.append(
            persistence_metrics.rmse
        )


        mae_difference_values.append(
            selected_metrics.mae
            -
            persistence_metrics.mae
        )


        rmse_difference_values.append(
            selected_metrics.rmse
            -
            persistence_metrics.rmse
        )


    alpha = (
        1.0
        -
        confidence
    )


    lower_quantile = (
        alpha
        /
        2.0
    )


    upper_quantile = (
        1.0
        -
        lower_quantile
    )


    def interval(
        values: list[float],
    ) -> dict:

        array = np.asarray(
            values,
            dtype=float,
        )


        return {
            "mean":
                float(
                    np.mean(
                        array
                    )
                ),

            "lower":
                float(
                    np.quantile(
                        array,
                        lower_quantile,
                    )
                ),

            "upper":
                float(
                    np.quantile(
                        array,
                        upper_quantile,
                    )
                ),
        }


    return {
        "method":
            "daily_block_bootstrap",

        "iterations":
            iterations,

        "confidence":
            confidence,

        "daily_blocks":
            int(
                len(
                    dates
                )
            ),

        "selected_mae":
            interval(
                selected_mae_values
            ),

        "selected_rmse":
            interval(
                selected_rmse_values
            ),

        "persistence_mae":
            interval(
                persistence_mae_values
            ),

        "persistence_rmse":
            interval(
                persistence_rmse_values
            ),

        "mae_difference_selected_minus_persistence":
            interval(
                mae_difference_values
            ),

        "rmse_difference_selected_minus_persistence":
            interval(
                rmse_difference_values
            ),
    }


# =========================================================
# RESIDUAL DIAGNOSTICS
# =========================================================

def residual_diagnostics(
    final_predictions: pd.DataFrame,
) -> dict:

    residuals = (
        final_predictions[
            "selected_residual"
        ]
        .dropna()
        .to_numpy(
            dtype=float,
        )
    )


    n = len(
        residuals
    )


    if n == 0:

        raise ValueError(
            "No residuals available."
        )


    mean_residual = float(
        np.mean(
            residuals
        )
    )


    std_residual = float(
        np.std(
            residuals,
            ddof=1,
        )
    )


    median_residual = float(
        np.median(
            residuals
        )
    )


    skewness = float(
        skew(
            residuals,
            bias=False,
        )
    )


    excess_kurtosis = float(
        kurtosis(
            residuals,
            fisher=True,
            bias=False,
        )
    )


    # -----------------------------------------------------
    # D'Agostino-Pearson normality test
    # -----------------------------------------------------

    if n >= 20:

        normality = normaltest(
            residuals
        )


        normality_statistic = float(
            normality.statistic
        )


        normality_p_value = float(
            normality.pvalue
        )


    else:

        normality_statistic = None

        normality_p_value = None


    # -----------------------------------------------------
    # Lag-1 residual autocorrelation
    # -----------------------------------------------------

    if n >= 2:

        lag1_autocorrelation = float(
            np.corrcoef(
                residuals[
                    1:
                ],
                residuals[
                    :-1
                ],
            )[
                0,
                1
            ]
        )


    else:

        lag1_autocorrelation = None


    # -----------------------------------------------------
    # Durbin-Watson descriptive statistic
    # -----------------------------------------------------

    denominator = float(
        np.sum(
            residuals
            ** 2
        )
    )


    if denominator > 0:

        durbin_watson = float(
            np.sum(
                np.diff(
                    residuals
                )
                ** 2
            )
            /
            denominator
        )


    else:

        durbin_watson = None


    return {
        "n":
            n,

        "mean_residual":
            mean_residual,

        "median_residual":
            median_residual,

        "std_residual":
            std_residual,

        "skewness":
            skewness,

        "excess_kurtosis":
            excess_kurtosis,

        "normality_test":
            {
                "name":
                    "D'Agostino-Pearson",

                "statistic":
                    normality_statistic,

                "p_value":
                    normality_p_value,

                "normal_at_alpha_005":
                    (
                        bool(
                            normality_p_value
                            >=
                            0.05
                        )
                        if normality_p_value
                        is not None
                        else None
                    ),
            },

        "lag1_autocorrelation":
            lag1_autocorrelation,

        "durbin_watson":
            durbin_watson,

        "interpretation_note":
            (
                "Residual normality is diagnostic only. "
                "Forecasting accuracy does not require "
                "normally distributed residuals. "
                "Temporal autocorrelation should be "
                "considered when interpreting conventional "
                "independence-based statistical tests."
            ),
    }


# =========================================================
# FINAL HOLDOUT STATISTICAL COMPARISON
# =========================================================

def final_selected_vs_persistence_test(
    final_predictions: pd.DataFrame,
) -> dict:

    selected_loss = (
        final_predictions[
            "selected_absolute_error"
        ]
        .to_numpy(
            dtype=float,
        )
    )


    persistence_loss = (
        final_predictions[
            "persistence_absolute_error"
        ]
        .to_numpy(
            dtype=float,
        )
    )


    dm = (
        diebold_mariano_test(
            selected_loss=
                selected_loss,

            comparator_loss=
                persistence_loss,

            hac_lag=
                DM_HAC_LAG,
        )
    )


    daily = (
        final_predictions.copy()
    )


    daily[
        "date"
    ] = (
        pd.to_datetime(
            daily[
                "timestamp"
            ],
            utc=True,
        )
        .dt
        .floor(
            "D"
        )
    )


    daily = (
        daily
        .groupby(
            "date",
            as_index=False,
        )[
            [
                "selected_absolute_error",
                "persistence_absolute_error",
            ]
        ]
        .mean()
    )


    (
        wilcoxon_statistic,
        wilcoxon_p_value,
    ) = wilcoxon_pair(
        daily[
            "selected_absolute_error"
        ]
        .to_numpy(
            dtype=float,
        ),

        daily[
            "persistence_absolute_error"
        ]
        .to_numpy(
            dtype=float,
        ),
    )


    return {
        "comparison":
            "selected_model_vs_persistence",

        "hourly_samples":
            int(
                len(
                    final_predictions
                )
            ),

        "daily_blocks":
            int(
                len(
                    daily
                )
            ),

        "selected_daily_mae":
            float(
                daily[
                    "selected_absolute_error"
                ]
                .mean()
            ),

        "persistence_daily_mae":
            float(
                daily[
                    "persistence_absolute_error"
                ]
                .mean()
            ),

        "selected_daily_win_rate_percent":
            float(
                (
                    daily[
                        "selected_absolute_error"
                    ]
                    <
                    daily[
                        "persistence_absolute_error"
                    ]
                )
                .mean()
                *
                100
            ),

        "wilcoxon":
            {
                "statistic":
                    wilcoxon_statistic,

                "p_value":
                    wilcoxon_p_value,

                "significant_005":
                    bool(
                        wilcoxon_p_value
                        <
                        0.05
                    ),
            },

        "diebold_mariano":
            dm,
    }


# =========================================================
# EVALUATION INTERPRETATION
# =========================================================

def build_evaluation_interpretation(
    selected_model_name: str,
    cv_summary: pd.DataFrame,
    friedman: dict,
    pairwise: pd.DataFrame,
    final_metrics: pd.DataFrame,
    final_comparison: dict,
    bootstrap: dict,
) -> dict:

    selected_cv = (
        cv_summary[
            cv_summary[
                "model_name"
            ]
            ==
            selected_model_name
        ]
    )


    persistence_cv = (
        cv_summary[
            cv_summary[
                "model_name"
            ]
            ==
            "Persistence"
        ]
    )


    if (
        not selected_cv.empty
        and
        not persistence_cv.empty
    ):

        selected_cv_mae = float(
            selected_cv.iloc[0][
                "mae_mean"
            ]
        )


        persistence_cv_mae = float(
            persistence_cv.iloc[0][
                "mae_mean"
            ]
        )


        cv_direction = (
            "lower"
            if selected_cv_mae
            <
            persistence_cv_mae
            else "higher"
        )


        cv_text = (
            f"Across temporal cross-validation, "
            f"{selected_model_name} has a mean MAE of "
            f"{selected_cv_mae:.6f}, which is "
            f"{cv_direction} than the persistence "
            f"benchmark MAE of "
            f"{persistence_cv_mae:.6f}."
        )


    else:

        cv_text = (
            "Cross-validation comparison could not "
            "be summarized."
        )


    selected_final = (
        final_metrics[
            final_metrics[
                "model_name"
            ]
            ==
            selected_model_name
        ]
        .iloc[0]
    )


    persistence_final = (
        final_metrics[
            final_metrics[
                "model_name"
            ]
            ==
            "Persistence"
        ]
        .iloc[0]
    )


    final_text = (
        f"On the untouched 2025 holdout, "
        f"{selected_model_name} obtained "
        f"MAE={selected_final['mae']:.6f}, "
        f"RMSE={selected_final['rmse']:.6f}, "
        f"R²={selected_final['r2']:.6f}. "
        f"Persistence obtained "
        f"MAE={persistence_final['mae']:.6f}, "
        f"RMSE={persistence_final['rmse']:.6f}, "
        f"R²={persistence_final['r2']:.6f}."
    )


    friedman_text = (
        (
            "The Friedman test detected statistically "
            "significant differences among forecasting "
            "methods across daily temporal blocks."
        )
        if friedman.get(
            "significant"
        )
        else
        (
            "The Friedman test did not detect statistically "
            "significant differences among all forecasting "
            "methods at alpha=0.05."
        )
    )


    final_dm = (
        final_comparison[
            "diebold_mariano"
        ]
    )


    final_wilcoxon = (
        final_comparison[
            "wilcoxon"
        ]
    )


    if (
        final_dm.get(
            "p_value"
        )
        is not None
    ):

        dm_text = (
            "The final Diebold-Mariano comparison "
            f"produced p={final_dm['p_value']:.6g}. "
        )


        if (
            final_dm[
                "p_value"
            ]
            <
            0.05
        ):

            if (
                final_dm[
                    "mean_loss_difference"
                ]
                <
                0
            ):

                dm_text += (
                    "The selected model has a statistically "
                    "lower absolute forecast loss than "
                    "persistence under the HAC-adjusted test."
                )


            else:

                dm_text += (
                    "Persistence has a statistically lower "
                    "absolute forecast loss than the "
                    "selected model under the HAC-adjusted "
                    "test."
                )


        else:

            dm_text += (
                "The test does not establish a significant "
                "difference in predictive loss at "
                "alpha=0.05."
            )


    else:

        dm_text = (
            "The final Diebold-Mariano test could not "
            "be evaluated."
        )


    wilcoxon_text = (
        "The daily-block Wilcoxon test produced "
        f"p={final_wilcoxon['p_value']:.6g}. "
    )


    if (
        final_wilcoxon[
            "p_value"
        ]
        <
        0.05
    ):

        wilcoxon_text += (
            "Daily absolute-error distributions differ "
            "significantly at alpha=0.05."
        )


    else:

        wilcoxon_text += (
            "No significant daily-block difference was "
            "detected at alpha=0.05."
        )


    mae_difference_interval = (
        bootstrap[
            "mae_difference_selected_minus_persistence"
        ]
    )


    rmse_difference_interval = (
        bootstrap[
            "rmse_difference_selected_minus_persistence"
        ]
    )


    bootstrap_text = (
        "The 95% daily-block bootstrap interval for "
        "selected-minus-persistence MAE is "
        f"[{mae_difference_interval['lower']:.6f}, "
        f"{mae_difference_interval['upper']:.6f}], "
        "and for RMSE is "
        f"[{rmse_difference_interval['lower']:.6f}, "
        f"{rmse_difference_interval['upper']:.6f}]. "
        "Intervals entirely below zero favor the selected "
        "model; intervals entirely above zero favor "
        "persistence."
    )


    return {
        "cross_validation":
            cv_text,

        "friedman":
            friedman_text,

        "final_holdout":
            final_text,

        "diebold_mariano":
            dm_text,

        "wilcoxon":
            wilcoxon_text,

        "bootstrap":
            bootstrap_text,

        "architectural_scope":
            (
                "These results evaluate only the "
                "complementary soil-moisture prediction "
                "module. They do not evaluate or replace "
                "AgroTwin's inference and decision engine."
            ),
    }


# =========================================================
# SAVE FINAL EXPERIMENTAL MODEL
# =========================================================

def save_final_experimental_model(
    selected_model_name: str,
    pipeline: Pipeline,
) -> None:

    bundle = {
        "pipeline":
            pipeline,

        "model_name":
            selected_model_name,

        "features":
            FEATURES,

        "target":
            TARGET,

        "prediction_horizon_hours":
            24,

        "training_period":
            "2022-2024",

        "final_test_period":
            "2025",

        "methodology":
            "CRISP-DM",

        "purpose":
            "COMPLEMENTARY_PREDICTION",

        "provenance":
            "MODEL_DERIVED",

        "decision_authority":
            False,

        "modifies_trusted_state":
            False,

        "modifies_recommendation":
            False,
    }


    joblib.dump(
        bundle,
        FINAL_SELECTED_MODEL_PATH,
    )


# =========================================================
# MAIN
# =========================================================

def main() -> None:

    print()
    print(
        "=" * 96
    )

    print(
        "AGROTWIN · CRISP-DM MODEL EVALUATION"
    )

    print(
        "=" * 96
    )


    EXPERIMENT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )


    dataframe = (
        load_training_dataset()
    )


    selected_model_name = (
        load_selected_model_name()
    )


    print()
    print(
        "SELECTED CANDIDATE FROM MODELING STAGE"
    )

    print(
        "-" * 96
    )

    print(
        selected_model_name
    )


    # =====================================================
    # TEMPORAL CROSS VALIDATION
    # =====================================================

    print()
    print(
        "TEMPORAL CROSS-VALIDATION"
    )

    print(
        "-" * 96
    )


    (
        cv_metrics,
        cv_predictions,
    ) = run_temporal_cross_validation(
        dataframe
    )


    cv_summary = (
        summarize_cv_metrics(
            cv_metrics
        )
    )


    print(
        cv_summary.to_string(
            index=False,

            float_format=lambda value:
                f"{value:.6f}",
        )
    )


    cv_metrics.to_csv(
        CV_METRICS_PATH,
        index=False,
    )


    cv_predictions.to_csv(
        CV_PREDICTIONS_PATH,
        index=False,
    )


    # =====================================================
    # FRIEDMAN
    # =====================================================

    print()
    print(
        "FRIEDMAN TEST · DAILY BLOCKS"
    )

    print(
        "-" * 96
    )


    friedman = (
        run_friedman_test(
            cv_predictions
        )
    )


    print(
        json.dumps(
            friedman,
            indent=2,
            ensure_ascii=False,
        )
    )


    FRIEDMAN_PATH.write_text(
        json.dumps(
            friedman,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


    # =====================================================
    # WILCOXON + HOLM + DIEBOLD-MARIANO
    # =====================================================

    print()
    print(
        "PAIRWISE TESTS · SELECTED MODEL VS COMPARATORS"
    )

    print(
        "-" * 96
    )


    pairwise = (
        run_pairwise_tests(
            predictions=
                cv_predictions,

            selected_model_name=
                selected_model_name,
        )
    )


    print(
        pairwise.to_string(
            index=False,

            float_format=lambda value:
                f"{value:.6f}",
        )
    )


    pairwise.to_csv(
        PAIRWISE_TESTS_PATH,
        index=False,
    )


    # =====================================================
    # FINAL 2025 HOLDOUT
    # =====================================================

    print()
    print(
        "FINAL UNTOUCHED HOLDOUT · 2025"
    )

    print(
        "-" * 96
    )


    (
        final_metrics,
        final_predictions,
        final_pipeline,
    ) = run_final_holdout_test(
        dataframe=
            dataframe,

        selected_model_name=
            selected_model_name,
    )


    print(
        final_metrics.to_string(
            index=False,

            float_format=lambda value:
                f"{value:.6f}",
        )
    )


    final_metrics.to_csv(
        FINAL_TEST_METRICS_PATH,
        index=False,
    )


    final_predictions.to_csv(
        FINAL_TEST_PREDICTIONS_PATH,
        index=False,
    )


    # =====================================================
    # FINAL STATISTICAL COMPARISON
    # =====================================================

    print()
    print(
        "FINAL SELECTED MODEL VS PERSISTENCE"
    )

    print(
        "-" * 96
    )


    final_comparison = (
        final_selected_vs_persistence_test(
            final_predictions
        )
    )


    print(
        json.dumps(
            final_comparison,
            indent=2,
            ensure_ascii=False,
        )
    )


    # =====================================================
    # BLOCK BOOTSTRAP
    # =====================================================

    print()
    print(
        "95% DAILY-BLOCK BOOTSTRAP CONFIDENCE INTERVALS"
    )

    print(
        "-" * 96
    )


    bootstrap = (
        run_block_bootstrap(
            final_predictions
        )
    )


    print(
        json.dumps(
            bootstrap,
            indent=2,
            ensure_ascii=False,
        )
    )


    BOOTSTRAP_PATH.write_text(
        json.dumps(
            bootstrap,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


    # =====================================================
    # RESIDUAL DIAGNOSTICS
    # =====================================================

    print()
    print(
        "RESIDUAL DIAGNOSTICS"
    )

    print(
        "-" * 96
    )


    residuals = (
        residual_diagnostics(
            final_predictions
        )
    )


    print(
        json.dumps(
            residuals,
            indent=2,
            ensure_ascii=False,
        )
    )


    RESIDUAL_DIAGNOSTICS_PATH.write_text(
        json.dumps(
            residuals,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


    # =====================================================
    # INTERPRETATION
    # =====================================================

    interpretation = (
        build_evaluation_interpretation(
            selected_model_name=
                selected_model_name,

            cv_summary=
                cv_summary,

            friedman=
                friedman,

            pairwise=
                pairwise,

            final_metrics=
                final_metrics,

            final_comparison=
                final_comparison,

            bootstrap=
                bootstrap,
        )
    )


    print()
    print(
        "INTERPRETATION"
    )

    print(
        "-" * 96
    )


    for (
        section,
        text,
    ) in interpretation.items():

        print()
        print(
            f"[{section.upper()}]"
        )

        print(
            text
        )


    # =====================================================
    # SAVE FINAL EXPERIMENTAL MODEL
    # =====================================================

    save_final_experimental_model(
        selected_model_name=
            selected_model_name,

        pipeline=
            final_pipeline,
    )


    # =====================================================
    # SUMMARY
    # =====================================================

    evaluation_summary = {
        "methodology":
            "CRISP-DM",

        "selected_model":
            selected_model_name,

        "selection_period":
            "2024",

        "cross_validation_period":
            "2022-2024",

        "final_holdout_period":
            "2025",

        "cv_gap_hours":
            CV_GAP_ROWS,

        "statistical_tests": {
            "friedman":
                friedman,

            "pairwise":
                pairwise.to_dict(
                    orient="records"
                ),

            "final_selected_vs_persistence":
                final_comparison,

            "bootstrap":
                bootstrap,

            "residual_diagnostics":
                residuals,
        },

        "interpretation":
            interpretation,

        "architecture": {
            "purpose":
                "COMPLEMENTARY_PREDICTION",

            "decision_authority":
                False,

            "modifies_trusted_state":
                False,

            "modifies_recommendation":
                False,
        },
    }


    EVALUATION_SUMMARY_PATH.write_text(
        json.dumps(
            evaluation_summary,
            indent=2,
            ensure_ascii=False,
            default=str,
        ),
        encoding="utf-8",
    )


    # =====================================================
    # ARTIFACTS
    # =====================================================

    print()
    print(
        "ARTIFACTS"
    )

    print(
        "-" * 96
    )


    for path in [
        CV_METRICS_PATH,
        CV_PREDICTIONS_PATH,
        FRIEDMAN_PATH,
        PAIRWISE_TESTS_PATH,
        FINAL_TEST_METRICS_PATH,
        FINAL_TEST_PREDICTIONS_PATH,
        BOOTSTRAP_PATH,
        RESIDUAL_DIAGNOSTICS_PATH,
        FINAL_SELECTED_MODEL_PATH,
        EVALUATION_SUMMARY_PATH,
    ]:

        print(
            path
        )


    print()
    print(
        "ARCHITECTURE NOTE"
    )

    print(
        "-" * 96
    )

    print(
        "This evaluation concerns only the complementary "
        "soil-moisture prediction module."
    )

    print(
        "It does NOT evaluate, replace, or control "
        "AgroTwin's inference and decision engine."
    )

    print(
        "The current production Random Forest artifact "
        "has not been overwritten."
    )


    print()
    print(
        "=" * 96
    )

    print(
        "CRISP-DM EVALUATION COMPLETE"
    )

    print(
        "=" * 96
    )


if __name__ == "__main__":

    main()