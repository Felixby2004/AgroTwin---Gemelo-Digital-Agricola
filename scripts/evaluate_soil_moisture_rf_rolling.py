from __future__ import annotations

from pathlib import Path
import sys

import numpy as np
import pandas as pd

from sklearn.ensemble import (
    RandomForestRegressor,
)

from sklearn.impute import (
    SimpleImputer,
)

from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)

from sklearn.pipeline import (
    Pipeline,
)


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


from ml.soil_moisture_model import (
    FEATURES,
    TARGET,
)


# ======================================================
# PATHS
# ======================================================

DATASET_PATH = (
    PROJECT_ROOT
    / "data"
    / "ml"
    / "soil_moisture_training.csv"
)


# ======================================================
# FIXED CONFIGURATION
#
# Selected previously using 2024 validation.
# ======================================================

RF_PARAMS = {

    "n_estimators":
        300,

    "max_depth":
        12,

    "min_samples_leaf":
        2,

    "min_samples_split":
        4,

    "max_features":
        0.8,

    "criterion":
        "squared_error",

    "bootstrap":
        True,

    "random_state":
        42,

    "n_jobs":
        -1,
}


# ======================================================
# ROLLING FOLDS
# ======================================================

FOLDS = [
    {
        "name":
            "Fold 1",

        "train_years":
            [2022],

        "test_year":
            2023,

        "role":
            "BACKTEST",
    },
    {
        "name":
            "Fold 2",

        "train_years":
            [
                2022,
                2023,
            ],

        "test_year":
            2024,

        "role":
            "VALIDATION",
    },
    {
        "name":
            "Fold 3",

        "train_years":
            [
                2022,
                2023,
                2024,
            ],

        "test_year":
            2025,

        "role":
            "FINAL_TEST",
    },
]


# ======================================================
# BUILD MODEL
# ======================================================

def build_pipeline() -> Pipeline:

    return Pipeline(
        steps=[
            (
                "imputer",
                SimpleImputer(
                    strategy="median",
                ),
            ),
            (
                "model",
                RandomForestRegressor(
                    **RF_PARAMS
                ),
            ),
        ]
    )


# ======================================================
# METRICS
# ======================================================

def calculate_metrics(
    observed: np.ndarray,
    predicted: np.ndarray,
) -> dict:

    return {

        "mae":
            float(
                mean_absolute_error(
                    observed,
                    predicted,
                )
            ),

        "rmse":
            float(
                mean_squared_error(
                    observed,
                    predicted,
                )
                ** 0.5
            ),

        "r2":
            float(
                r2_score(
                    observed,
                    predicted,
                )
            ),
    }


# ======================================================
# IMPROVEMENT
# ======================================================

def improvement_percent(
    baseline: float,
    model: float,
) -> float:

    if baseline == 0:

        return 0.0


    return float(
        (
            baseline
            - model
        )
        / baseline
        * 100
    )


# ======================================================
# SINGLE FOLD
# ======================================================

def evaluate_fold(
    dataframe: pd.DataFrame,
    train_years: list[int],
    test_year: int,
) -> dict:

    train = dataframe[
        dataframe[
            "timestamp"
        ]
        .dt.year
        .isin(
            train_years
        )
    ].copy()


    test = dataframe[
        dataframe[
            "timestamp"
        ]
        .dt.year
        == test_year
    ].copy()


    if len(train) == 0:

        raise ValueError(
            f"No training data "
            f"for years "
            f"{train_years}"
        )


    if len(test) == 0:

        raise ValueError(
            f"No test data "
            f"for year "
            f"{test_year}"
        )


    # ==================================================
    # TRAIN
    # ==================================================

    pipeline = (
        build_pipeline()
    )


    X_train = train[
        FEATURES
    ]

    y_train = train[
        TARGET
    ]


    pipeline.fit(
        X_train,
        y_train,
    )


    # ==================================================
    # PREDICT DELTA
    # ==================================================

    predicted_delta = (
        pipeline.predict(
            test[
                FEATURES
            ]
        )
    )


    # ==================================================
    # RECONSTRUCT FUTURE SOIL MOISTURE
    # ==================================================

    current_moisture = (
        test[
            "soil_moisture"
        ]
        .to_numpy(
            dtype=float
        )
    )


    predicted_future = (
        current_moisture
        + predicted_delta
    )


    observed_future = (
        test[
            "future_soil_moisture_24h"
        ]
        .to_numpy(
            dtype=float
        )
    )


    # ==================================================
    # RANDOM FOREST METRICS
    # ==================================================

    model_metrics = (
        calculate_metrics(
            observed_future,
            predicted_future,
        )
    )


    # ==================================================
    # PERSISTENCE BASELINE
    #
    # Future soil moisture =
    # current soil moisture
    # ==================================================

    baseline_predictions = (
        current_moisture
    )


    baseline_metrics = (
        calculate_metrics(
            observed_future,
            baseline_predictions,
        )
    )


    # ==================================================
    # IMPROVEMENTS
    # ==================================================

    mae_improvement = (
        improvement_percent(
            baseline_metrics[
                "mae"
            ],
            model_metrics[
                "mae"
            ],
        )
    )


    rmse_improvement = (
        improvement_percent(
            baseline_metrics[
                "rmse"
            ],
            model_metrics[
                "rmse"
            ],
        )
    )


    # ==================================================
    # ERROR DISTRIBUTION
    # ==================================================

    model_absolute_error = (
        np.abs(
            observed_future
            - predicted_future
        )
    )


    baseline_absolute_error = (
        np.abs(
            observed_future
            - baseline_predictions
        )
    )


    model_better_count = int(
        np.sum(
            model_absolute_error
            <
            baseline_absolute_error
        )
    )


    baseline_better_count = int(
        np.sum(
            baseline_absolute_error
            <
            model_absolute_error
        )
    )


    ties = int(
        len(test)
        - model_better_count
        - baseline_better_count
    )


    model_better_percent = (
        model_better_count
        / len(test)
        * 100
    )


    # ==================================================
    # RETURN
    # ==================================================

    return {

        "train_samples":
            len(train),

        "test_samples":
            len(test),

        "model":
            model_metrics,

        "baseline":
            baseline_metrics,

        "mae_improvement_percent":
            mae_improvement,

        "rmse_improvement_percent":
            rmse_improvement,

        "model_better_count":
            model_better_count,

        "baseline_better_count":
            baseline_better_count,

        "ties":
            ties,

        "model_better_percent":
            model_better_percent,

        "observed":
            observed_future,

        "model_predictions":
            predicted_future,

        "baseline_predictions":
            baseline_predictions,
    }


# ======================================================
# MAIN
# ======================================================

def main() -> None:

    if not DATASET_PATH.exists():

        raise FileNotFoundError(
            f"Dataset not found: "
            f"{DATASET_PATH}"
        )


    dataframe = pd.read_csv(
        DATASET_PATH
    )


    dataframe[
        "timestamp"
    ] = pd.to_datetime(
        dataframe[
            "timestamp"
        ],
        utc=True,
        errors="coerce",
    )


    dataframe = dataframe.dropna(
        subset=[
            "timestamp",
            "soil_moisture",
            "future_soil_moisture_24h",
            TARGET,
        ]
    )


    print()
    print(
        "=========================================="
    )
    print(
        "RANDOM FOREST ROLLING-ORIGIN VALIDATION"
    )
    print(
        "=========================================="
    )


    print()

    print(
        "Fixed configuration:"
    )

    for key, value in (
        RF_PARAMS.items()
    ):

        print(
            f"  {key}: "
            f"{value}"
        )


    results = []


    all_observed = []

    all_model_predictions = []

    all_baseline_predictions = []


    # ==================================================
    # FOLDS
    # ==================================================

    for fold in FOLDS:

        print()
        print(
            "=========================================="
        )

        print(
            f"{fold['name']} "
            f"— {fold['role']}"
        )

        print(
            "=========================================="
        )


        print(
            "Train years: "
            + ", ".join(
                str(year)
                for year in
                fold[
                    "train_years"
                ]
            )
        )


        print(
            f"Test year: "
            f"{fold['test_year']}"
        )


        result = (
            evaluate_fold(
                dataframe,
                fold[
                    "train_years"
                ],
                fold[
                    "test_year"
                ],
            )
        )


        results.append(
            {
                **fold,
                **result,
            }
        )


        all_observed.append(
            result[
                "observed"
            ]
        )


        all_model_predictions.append(
            result[
                "model_predictions"
            ]
        )


        all_baseline_predictions.append(
            result[
                "baseline_predictions"
            ]
        )


        print()
        print(
            f"Train samples: "
            f"{result['train_samples']}"
        )

        print(
            f"Test samples:  "
            f"{result['test_samples']}"
        )


        print()
        print(
            "Random Forest:"
        )

        print(
            f"  MAE:  "
            f"{result['model']['mae']:.6f}"
        )

        print(
            f"  RMSE: "
            f"{result['model']['rmse']:.6f}"
        )

        print(
            f"  R²:   "
            f"{result['model']['r2']:.6f}"
        )


        print()
        print(
            "Persistence baseline:"
        )

        print(
            f"  MAE:  "
            f"{result['baseline']['mae']:.6f}"
        )

        print(
            f"  RMSE: "
            f"{result['baseline']['rmse']:.6f}"
        )

        print(
            f"  R²:   "
            f"{result['baseline']['r2']:.6f}"
        )


        print()
        print(
            "Improvement vs baseline:"
        )

        print(
            f"  MAE:  "
            f"{result['mae_improvement_percent']:.2f}%"
        )

        print(
            f"  RMSE: "
            f"{result['rmse_improvement_percent']:.2f}%"
        )


        print()
        print(
            "Per-observation comparison:"
        )

        print(
            f"  RF better: "
            f"{result['model_better_count']}"
        )

        print(
            f"  Baseline better: "
            f"{result['baseline_better_count']}"
        )

        print(
            f"  Ties: "
            f"{result['ties']}"
        )

        print(
            f"  RF better in: "
            f"{result['model_better_percent']:.2f}%"
        )


    # ==================================================
    # AGGREGATE ALL TEST YEARS
    # ==================================================

    observed_combined = (
        np.concatenate(
            all_observed
        )
    )


    model_combined = (
        np.concatenate(
            all_model_predictions
        )
    )


    baseline_combined = (
        np.concatenate(
            all_baseline_predictions
        )
    )


    aggregate_model = (
        calculate_metrics(
            observed_combined,
            model_combined,
        )
    )


    aggregate_baseline = (
        calculate_metrics(
            observed_combined,
            baseline_combined,
        )
    )


    aggregate_mae_improvement = (
        improvement_percent(
            aggregate_baseline[
                "mae"
            ],
            aggregate_model[
                "mae"
            ],
        )
    )


    aggregate_rmse_improvement = (
        improvement_percent(
            aggregate_baseline[
                "rmse"
            ],
            aggregate_model[
                "rmse"
            ],
        )
    )


    # ==================================================
    # SUMMARY TABLE
    # ==================================================

    print()
    print(
        "=========================================="
    )
    print(
        "ROLLING SUMMARY"
    )
    print(
        "=========================================="
    )


    for result in results:

        print(
            f"{result['test_year']} | "
            f"MAE Δ "
            f"{result['mae_improvement_percent']:+.2f}% | "
            f"RMSE Δ "
            f"{result['rmse_improvement_percent']:+.2f}% | "
            f"RF better observations "
            f"{result['model_better_percent']:.2f}%"
        )


    # ==================================================
    # AGGREGATE
    # ==================================================

    print()
    print(
        "=========================================="
    )
    print(
        "AGGREGATE 2023–2025"
    )
    print(
        "=========================================="
    )


    print(
        "Random Forest:"
    )

    print(
        f"  MAE:  "
        f"{aggregate_model['mae']:.6f}"
    )

    print(
        f"  RMSE: "
        f"{aggregate_model['rmse']:.6f}"
    )

    print(
        f"  R²:   "
        f"{aggregate_model['r2']:.6f}"
    )


    print()
    print(
        "Persistence baseline:"
    )

    print(
        f"  MAE:  "
        f"{aggregate_baseline['mae']:.6f}"
    )

    print(
        f"  RMSE: "
        f"{aggregate_baseline['rmse']:.6f}"
    )

    print(
        f"  R²:   "
        f"{aggregate_baseline['r2']:.6f}"
    )


    print()
    print(
        "Aggregate improvement:"
    )

    print(
        f"  MAE:  "
        f"{aggregate_mae_improvement:.2f}%"
    )

    print(
        f"  RMSE: "
        f"{aggregate_rmse_improvement:.2f}%"
    )


    # ==================================================
    # CONSISTENCY
    # ==================================================

    both_metrics_better = sum(
        1
        for result
        in results
        if (
            result[
                "mae_improvement_percent"
            ]
            > 0
            and
            result[
                "rmse_improvement_percent"
            ]
            > 0
        )
    )


    rmse_better_years = sum(
        1
        for result
        in results
        if result[
            "rmse_improvement_percent"
        ]
        > 0
    )


    print()
    print(
        "=========================================="
    )
    print(
        "CONSISTENCY"
    )
    print(
        "=========================================="
    )


    print(
        "Years better in MAE + RMSE: "
        f"{both_metrics_better}"
        f"/{len(results)}"
    )


    print(
        "Years better in RMSE: "
        f"{rmse_better_years}"
        f"/{len(results)}"
    )


    # ==================================================
    # INTERPRETATION STATUS
    # ==================================================

    if (
        aggregate_mae_improvement > 0
        and
        aggregate_rmse_improvement > 0
        and
        both_metrics_better >= 2
    ):

        status = (
            "SUPPORTED_COMPLEMENTARY_MODEL"
        )

    elif (
        aggregate_rmse_improvement > 0
        or
        both_metrics_better >= 1
    ):

        status = (
            "MIXED_COMPLEMENTARY_MODEL"
        )

    else:

        status = (
            "NO_CLEAR_ADVANTAGE"
        )


    print()
    print(
        "=========================================="
    )
    print(
        "MODEL STATUS"
    )
    print(
        "=========================================="
    )


    print(
        status
    )


    print()
    print(
        "Interpretation:"
    )


    if status == (
        "SUPPORTED_COMPLEMENTARY_MODEL"
    ):

        print(
            "The Random Forest shows "
            "complementary predictive value "
            "across the rolling evaluation."
        )


    elif status == (
        "MIXED_COMPLEMENTARY_MODEL"
    ):

        print(
            "The Random Forest shows "
            "predictive value in some periods, "
            "but its advantage over persistence "
            "is not temporally consistent."
        )


    else:

        print(
            "The Random Forest does not show "
            "a sufficiently consistent advantage "
            "over persistence."
        )


    print()
    print(
        "The model remains complementary "
        "and has no decision authority."
    )


if __name__ == "__main__":

    main()