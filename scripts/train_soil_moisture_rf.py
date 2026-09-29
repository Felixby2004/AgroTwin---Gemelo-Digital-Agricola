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
    SoilMoistureRandomForest,
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

MODEL_PATH = (
    PROJECT_ROOT
    / "artifacts"
    / "ml"
    / "soil_moisture_rf.joblib"
)


# ======================================================
# CANDIDATE CONFIGURATIONS
# ======================================================

CANDIDATES = [
    {
        "n_estimators": 300,
        "max_depth": 12,
        "min_samples_leaf": 2,
        "min_samples_split": 4,
        "max_features": 0.8,
    },
    {
        "n_estimators": 300,
        "max_depth": 16,
        "min_samples_leaf": 2,
        "min_samples_split": 4,
        "max_features": 0.8,
    },
    {
        "n_estimators": 300,
        "max_depth": 20,
        "min_samples_leaf": 2,
        "min_samples_split": 4,
        "max_features": 0.8,
    },
    {
        "n_estimators": 300,
        "max_depth": None,
        "min_samples_leaf": 2,
        "min_samples_split": 4,
        "max_features": 0.8,
    },
    {
        "n_estimators": 300,
        "max_depth": 16,
        "min_samples_leaf": 3,
        "min_samples_split": 6,
        "max_features": 0.8,
    },
    {
        "n_estimators": 300,
        "max_depth": 18,
        "min_samples_leaf": 4,
        "min_samples_split": 8,
        "max_features": 0.8,
    },
    {
        "n_estimators": 300,
        "max_depth": 16,
        "min_samples_leaf": 2,
        "min_samples_split": 4,
        "max_features": 0.6,
    },
    {
        "n_estimators": 300,
        "max_depth": 16,
        "min_samples_leaf": 2,
        "min_samples_split": 4,
        "max_features": 1.0,
    },
]


# ======================================================
# METRICS
# ======================================================

def calculate_metrics(
    observed,
    predicted,
) -> dict:

    return {
        "mae": float(
            mean_absolute_error(
                observed,
                predicted,
            )
        ),

        "rmse": float(
            mean_squared_error(
                observed,
                predicted,
            )
            ** 0.5
        ),

        "r2": float(
            r2_score(
                observed,
                predicted,
            )
        ),
    }


# ======================================================
# BUILD MODEL
# ======================================================

def build_pipeline(
    params: dict,
) -> Pipeline:

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
                    **params,
                    criterion="squared_error",
                    bootstrap=True,
                    random_state=42,
                    n_jobs=-1,
                ),
            ),
        ]
    )


# ======================================================
# EVALUATE CONFIGURATION
# ======================================================

def evaluate_candidate(
    train: pd.DataFrame,
    validation: pd.DataFrame,
    params: dict,
) -> dict:

    pipeline = build_pipeline(
        params
    )


    X_train = train[
        FEATURES
    ]

    y_train = train[
        TARGET
    ]


    X_validation = validation[
        FEATURES
    ]


    pipeline.fit(
        X_train,
        y_train,
    )


    predicted_delta = (
        pipeline.predict(
            X_validation
        )
    )


    predicted_moisture = (
        validation[
            "soil_moisture"
        ]
        .to_numpy(
            dtype=float
        )
        + predicted_delta
    )


    observed = validation[
        "future_soil_moisture_24h"
    ]


    model_metrics = (
        calculate_metrics(
            observed,
            predicted_moisture,
        )
    )


    persistence = (
        validation[
            "soil_moisture"
        ]
        .to_numpy(
            dtype=float
        )
    )


    baseline_metrics = (
        calculate_metrics(
            observed,
            persistence,
        )
    )


    return {
        "params": params,
        "model": model_metrics,
        "baseline": baseline_metrics,
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


    # ==================================================
    # TEMPORAL SPLIT
    # ==================================================

    tuning_train = dataframe[
        dataframe[
            "timestamp"
        ].dt.year
        <= 2023
    ].copy()


    validation = dataframe[
        dataframe[
            "timestamp"
        ].dt.year
        == 2024
    ].copy()


    final_test = dataframe[
        dataframe[
            "timestamp"
        ].dt.year
        == 2025
    ].copy()


    print()
    print(
        "=========================================="
    )
    print(
        "RANDOM FOREST TEMPORAL TUNING"
    )
    print(
        "=========================================="
    )

    print(
        f"Training 2022–2023: "
        f"{len(tuning_train)}"
    )

    print(
        f"Validation 2024:     "
        f"{len(validation)}"
    )

    print(
        f"Final test 2025:     "
        f"{len(final_test)}"
    )


    # ==================================================
    # HYPERPARAMETER SEARCH
    # ==================================================

    results = []


    for index, params in enumerate(
        CANDIDATES,
        start=1,
    ):

        print()
        print(
            f"[{index}/{len(CANDIDATES)}] "
            f"{params}"
        )


        result = evaluate_candidate(
            tuning_train,
            validation,
            params,
        )


        results.append(
            result
        )


        print(
            "Validation RF "
            f"MAE={result['model']['mae']:.6f} "
            f"RMSE={result['model']['rmse']:.6f} "
            f"R²={result['model']['r2']:.6f}"
        )


        print(
            "Validation baseline "
            f"MAE={result['baseline']['mae']:.6f} "
            f"RMSE={result['baseline']['rmse']:.6f}"
        )


    # ==================================================
    # SELECT BEST
    #
    # MAE primary criterion.
    # RMSE secondary criterion.
    # ==================================================

    results.sort(
        key=lambda item: (
            item[
                "model"
            ][
                "mae"
            ],
            item[
                "model"
            ][
                "rmse"
            ],
        )
    )


    best = results[0]


    print()
    print(
        "=========================================="
    )
    print(
        "BEST VALIDATION CONFIGURATION"
    )
    print(
        "=========================================="
    )

    print(
        best[
            "params"
        ]
    )

    print(
        "Validation MAE:  "
        f"{best['model']['mae']:.6f}"
    )

    print(
        "Validation RMSE: "
        f"{best['model']['rmse']:.6f}"
    )

    print(
        "Validation R²:   "
        f"{best['model']['r2']:.6f}"
    )


    # ==================================================
    # FINAL TRAIN 2022–2024
    # ==================================================

    final_train = dataframe[
        dataframe[
            "timestamp"
        ].dt.year
        <= 2024
    ].copy()


    pipeline = build_pipeline(
        best[
            "params"
        ]
    )


    pipeline.fit(
        final_train[
            FEATURES
        ],
        final_train[
            TARGET
        ],
    )


    # ==================================================
    # FINAL 2025 TEST
    # ==================================================

    predicted_delta = (
        pipeline.predict(
            final_test[
                FEATURES
            ]
        )
    )


    final_predictions = (
        final_test[
            "soil_moisture"
        ]
        .to_numpy(
            dtype=float
        )
        + predicted_delta
    )


    observed = final_test[
        "future_soil_moisture_24h"
    ]


    final_metrics = (
        calculate_metrics(
            observed,
            final_predictions,
        )
    )


    persistence_predictions = (
        final_test[
            "soil_moisture"
        ]
        .to_numpy(
            dtype=float
        )
    )


    baseline_metrics = (
        calculate_metrics(
            observed,
            persistence_predictions,
        )
    )


    mae_improvement = (
        (
            baseline_metrics[
                "mae"
            ]
            - final_metrics[
                "mae"
            ]
        )
        /
        baseline_metrics[
            "mae"
        ]
        * 100
    )


    rmse_improvement = (
        (
            baseline_metrics[
                "rmse"
            ]
            - final_metrics[
                "rmse"
            ]
        )
        /
        baseline_metrics[
            "rmse"
        ]
        * 100
    )


    print()
    print(
        "=========================================="
    )
    print(
        "FINAL 2025 TEST"
    )
    print(
        "=========================================="
    )


    print(
        "Random Forest:"
    )

    print(
        f"MAE:  "
        f"{final_metrics['mae']:.6f}"
    )

    print(
        f"RMSE: "
        f"{final_metrics['rmse']:.6f}"
    )

    print(
        f"R²:   "
        f"{final_metrics['r2']:.6f}"
    )


    print()
    print(
        "Persistence baseline:"
    )

    print(
        f"MAE:  "
        f"{baseline_metrics['mae']:.6f}"
    )

    print(
        f"RMSE: "
        f"{baseline_metrics['rmse']:.6f}"
    )

    print(
        f"R²:   "
        f"{baseline_metrics['r2']:.6f}"
    )


    print()
    print(
        "Improvement:"
    )

    print(
        f"MAE:  "
        f"{mae_improvement:.2f}%"
    )

    print(
        f"RMSE: "
        f"{rmse_improvement:.2f}%"
    )


    # ==================================================
    # SAVE USING PROJECT MODEL CLASS
    # ==================================================

    final_model = (
        SoilMoistureRandomForest(
            random_state=42
        )
    )


    final_model.pipeline = (
        pipeline
    )


    # Preserve evaluation by running the
    # standard temporal evaluator once
    # with the selected pipeline parameters
    # already fitted afterwards.

    final_model.save(
        MODEL_PATH
    )


    # ==================================================
    # FEATURE IMPORTANCE
    # ==================================================

    rf = pipeline.named_steps[
        "model"
    ]


    importance = list(
        zip(
            FEATURES,
            rf.feature_importances_,
            strict=True,
        )
    )


    importance.sort(
        key=lambda item:
            item[1],
        reverse=True,
    )


    print()
    print(
        "=========================================="
    )
    print(
        "FINAL FEATURE IMPORTANCE"
    )
    print(
        "=========================================="
    )


    for index, (
        feature,
        value,
    ) in enumerate(
        importance,
        start=1,
    ):

        print(
            f"{index:02d}. "
            f"{feature:<36} "
            f"{value:.6f}"
        )


    print()
    print(
        "=========================================="
    )
    print(
        "MODEL SAVED"
    )
    print(
        "=========================================="
    )

    print(
        MODEL_PATH
    )


if __name__ == "__main__":

    main()