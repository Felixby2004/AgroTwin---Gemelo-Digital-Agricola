from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import json
import time

import joblib
import numpy as np
import pandas as pd

from sklearn.ensemble import (
    ExtraTreesRegressor,
    HistGradientBoostingRegressor,
    RandomForestRegressor,
)
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from ml.datasets import (
    FUTURE_SOIL_MOISTURE,
    TIMESTAMP_COLUMN,
    load_training_dataset,
)

from ml.features import (
    FEATURES,
    TARGET,
    temporal_train_validation_test_split,
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


RESULTS_PATH = (
    EXPERIMENT_DIR
    / "model_selection_results.csv"
)


METADATA_PATH = (
    EXPERIMENT_DIR
    / "model_selection_metadata.json"
)


SELECTED_MODEL_PATH = (
    EXPERIMENT_DIR
    / "selected_model_candidate.joblib"
)


VALIDATION_PREDICTIONS_PATH = (
    EXPERIMENT_DIR
    / "validation_predictions.csv"
)


# =========================================================
# CONFIGURATION
# =========================================================

RANDOM_STATE = 42

PHYSICAL_MIN = 0.0

PHYSICAL_MAX = 0.8


# =========================================================
# METRICS
# =========================================================

@dataclass
class RegressionMetrics:
    mae: float
    rmse: float
    r2: float
    bias: float


@dataclass
class CandidateEvaluation:
    model_name: str

    mae: float
    rmse: float
    r2: float
    bias: float

    mae_improvement_vs_persistence_percent: float
    rmse_improvement_vs_persistence_percent: float

    train_seconds: float
    predict_seconds: float

    train_samples: int
    validation_samples: int


# =========================================================
# MODELS
# =========================================================

def build_candidates() -> dict[str, Pipeline]:
    """
    Candidate regressors evaluated under the same
    temporal partition and the same predictor set.

    The currently deployed Random Forest remains only
    one candidate in this CRISP-DM experiment.
    """

    return {
        # -------------------------------------------------
        # Linear regularized reference model
        # -------------------------------------------------
        "Ridge": Pipeline(
            steps=[
                (
                    "imputer",
                    SimpleImputer(
                        strategy="median",
                    ),
                ),
                (
                    "scaler",
                    StandardScaler(),
                ),
                (
                    "model",
                    Ridge(
                        alpha=1.0,
                    ),
                ),
            ]
        ),

        # -------------------------------------------------
        # Existing Random Forest family
        # -------------------------------------------------
        "Random Forest": Pipeline(
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
                        n_estimators=300,
                        max_depth=12,
                        min_samples_leaf=2,
                        min_samples_split=4,
                        max_features=0.8,
                        bootstrap=True,
                        random_state=RANDOM_STATE,
                        n_jobs=-1,
                    ),
                ),
            ]
        ),

        # -------------------------------------------------
        # Extremely randomized trees
        # -------------------------------------------------
        "Extra Trees": Pipeline(
            steps=[
                (
                    "imputer",
                    SimpleImputer(
                        strategy="median",
                    ),
                ),
                (
                    "model",
                    ExtraTreesRegressor(
                        n_estimators=300,
                        max_depth=16,
                        min_samples_leaf=2,
                        min_samples_split=4,
                        max_features=0.8,
                        bootstrap=False,
                        random_state=RANDOM_STATE,
                        n_jobs=-1,
                    ),
                ),
            ]
        ),

        # -------------------------------------------------
        # Gradient boosting
        # -------------------------------------------------
        "Hist Gradient Boosting": Pipeline(
            steps=[
                (
                    "imputer",
                    SimpleImputer(
                        strategy="median",
                    ),
                ),
                (
                    "model",
                    HistGradientBoostingRegressor(
                        learning_rate=0.05,
                        max_iter=300,
                        max_leaf_nodes=31,
                        min_samples_leaf=20,
                        l2_regularization=0.1,
                        random_state=RANDOM_STATE,
                    ),
                ),
            ]
        ),
    }


# =========================================================
# METRIC CALCULATION
# =========================================================

def calculate_metrics(
    observed: np.ndarray,
    predicted: np.ndarray,
) -> RegressionMetrics:

    observed_array = np.asarray(
        observed,
        dtype=float,
    )

    predicted_array = np.asarray(
        predicted,
        dtype=float,
    )


    return RegressionMetrics(
        mae=float(
            mean_absolute_error(
                observed_array,
                predicted_array,
            )
        ),

        rmse=float(
            mean_squared_error(
                observed_array,
                predicted_array,
            )
            ** 0.5
        ),

        r2=float(
            r2_score(
                observed_array,
                predicted_array,
            )
        ),

        bias=float(
            np.mean(
                predicted_array
                -
                observed_array
            )
        ),
    )


# =========================================================
# IMPROVEMENT AGAINST PERSISTENCE
# =========================================================

def improvement_percent(
    baseline: float,
    candidate: float,
) -> float:

    if baseline == 0:
        return 0.0


    return float(
        (
            baseline
            -
            candidate
        )
        /
        baseline
        *
        100
    )


# =========================================================
# RECONSTRUCT ABSOLUTE FUTURE MOISTURE
# =========================================================

def reconstruct_future_moisture(
    current_moisture: np.ndarray,
    predicted_delta: np.ndarray,
) -> np.ndarray:
    """
    All ML candidates predict Δ soil moisture at +24 h.

    The absolute future moisture is reconstructed as:

        theta(t+24) = theta(t) + predicted_delta

    The same physical guard is applied to every candidate
    to guarantee a fair comparison.
    """

    predicted_future = (
        np.asarray(
            current_moisture,
            dtype=float,
        )
        +
        np.asarray(
            predicted_delta,
            dtype=float,
        )
    )


    return np.clip(
        predicted_future,
        PHYSICAL_MIN,
        PHYSICAL_MAX,
    )


# =========================================================
# EVALUATE ONE CANDIDATE
# =========================================================

def evaluate_candidate(
    model_name: str,
    pipeline: Pipeline,
    train: pd.DataFrame,
    validation: pd.DataFrame,
    baseline_metrics: RegressionMetrics,
) -> tuple[
    CandidateEvaluation,
    Pipeline,
    np.ndarray,
]:

    X_train = train[
        FEATURES
    ]


    y_train = train[
        TARGET
    ]


    X_validation = validation[
        FEATURES
    ]


    current_moisture = (
        validation[
            "soil_moisture"
        ]
        .to_numpy(
            dtype=float,
        )
    )


    observed_future = (
        validation[
            FUTURE_SOIL_MOISTURE
        ]
        .to_numpy(
            dtype=float,
        )
    )


    # -----------------------------------------------------
    # Train
    # -----------------------------------------------------

    train_started = (
        time.perf_counter()
    )


    pipeline.fit(
        X_train,
        y_train,
    )


    train_seconds = (
        time.perf_counter()
        -
        train_started
    )


    # -----------------------------------------------------
    # Predict delta
    # -----------------------------------------------------

    predict_started = (
        time.perf_counter()
    )


    predicted_delta = (
        pipeline.predict(
            X_validation
        )
    )


    predict_seconds = (
        time.perf_counter()
        -
        predict_started
    )


    # -----------------------------------------------------
    # Reconstruct absolute moisture
    # -----------------------------------------------------

    predicted_future = (
        reconstruct_future_moisture(
            current_moisture=
                current_moisture,

            predicted_delta=
                predicted_delta,
        )
    )


    # -----------------------------------------------------
    # Metrics
    # -----------------------------------------------------

    metrics = (
        calculate_metrics(
            observed_future,
            predicted_future,
        )
    )


    result = CandidateEvaluation(
        model_name=
            model_name,

        mae=
            metrics.mae,

        rmse=
            metrics.rmse,

        r2=
            metrics.r2,

        bias=
            metrics.bias,

        mae_improvement_vs_persistence_percent=
            improvement_percent(
                baseline_metrics.mae,
                metrics.mae,
            ),

        rmse_improvement_vs_persistence_percent=
            improvement_percent(
                baseline_metrics.rmse,
                metrics.rmse,
            ),

        train_seconds=
            float(
                train_seconds
            ),

        predict_seconds=
            float(
                predict_seconds
            ),

        train_samples=
            int(
                len(
                    train
                )
            ),

        validation_samples=
            int(
                len(
                    validation
                )
            ),
    )


    return (
        result,
        pipeline,
        predicted_future,
    )


# =========================================================
# SELECT BEST CANDIDATE
# =========================================================

def select_best_candidate(
    results: pd.DataFrame,
) -> str:
    """
    Selection criteria:

    1. MAE  -> primary
    2. RMSE -> secondary
    3. R²   -> tertiary tie-breaker

    2025 is NOT used here.
    """

    if results.empty:

        raise ValueError(
            "No candidate results are available."
        )


    ordered = (
        results
        .sort_values(
            by=[
                "mae",
                "rmse",
                "r2",
            ],
            ascending=[
                True,
                True,
                False,
            ],
        )
        .reset_index(
            drop=True
        )
    )


    return str(
        ordered
        .iloc[0][
            "model_name"
        ]
    )


# =========================================================
# SELECTION INTERPRETATION
# =========================================================

def build_selection_interpretation(
    results: pd.DataFrame,
    baseline_metrics: RegressionMetrics,
    selected_model_name: str,
) -> str:

    selected = (
        results[
            results[
                "model_name"
            ]
            ==
            selected_model_name
        ]
        .iloc[0]
    )


    beats_baseline_mae = bool(
        selected[
            "mae"
        ]
        <
        baseline_metrics.mae
    )


    beats_baseline_rmse = bool(
        selected[
            "rmse"
        ]
        <
        baseline_metrics.rmse
    )


    if (
        beats_baseline_mae
        and
        beats_baseline_rmse
    ):

        baseline_text = (
            "El candidato seleccionado supera al benchmark "
            "de persistencia tanto en MAE como en RMSE "
            "sobre la validación temporal de 2024."
        )


    elif (
        beats_baseline_mae
        or
        beats_baseline_rmse
    ):

        baseline_text = (
            "El candidato seleccionado supera al benchmark "
            "de persistencia únicamente en una de las dos "
            "métricas principales. Su ventaja predictiva "
            "debe verificarse mediante validación cruzada "
            "y pruebas estadísticas."
        )


    else:

        baseline_text = (
            "El candidato seleccionado es el mejor entre "
            "los modelos entrenados, pero no supera al "
            "benchmark de persistencia en MAE y RMSE. "
            "Por tanto, todavía no puede afirmarse una "
            "ventaja predictiva respecto al benchmark."
        )


    return (
        f"El modelo seleccionado durante la validación "
        f"temporal es {selected_model_name}. "
        f"La selección utiliza MAE como criterio principal, "
        f"RMSE como criterio secundario y R² únicamente "
        f"como criterio terciario de desempate. "
        f"El conjunto correspondiente a 2025 permanece "
        f"completamente aislado y no interviene en esta "
        f"selección. "
        f"{baseline_text}"
    )


# =========================================================
# MODEL SELECTION
# =========================================================

def run_model_selection(
    dataframe: pd.DataFrame,
) -> dict:

    split = (
        temporal_train_validation_test_split(
            dataframe
        )
    )


    train = (
        split.train
    )


    validation = (
        split.validation
    )


    final_test = (
        split.final_test
    )


    # -----------------------------------------------------
    # Persistence benchmark
    #
    # theta(t+24) = theta(t)
    # -----------------------------------------------------

    current_validation = (
        validation[
            "soil_moisture"
        ]
        .to_numpy(
            dtype=float,
        )
    )


    observed_validation = (
        validation[
            FUTURE_SOIL_MOISTURE
        ]
        .to_numpy(
            dtype=float,
        )
    )


    persistence_predictions = (
        current_validation.copy()
    )


    baseline_metrics = (
        calculate_metrics(
            observed_validation,
            persistence_predictions,
        )
    )


    # -----------------------------------------------------
    # Candidate models
    # -----------------------------------------------------

    candidates = (
        build_candidates()
    )


    result_rows = []


    fitted_models: dict[
        str,
        Pipeline,
    ] = {}


    # -----------------------------------------------------
    # Prediction table for later statistical evaluation
    # -----------------------------------------------------

    prediction_table = pd.DataFrame(
        {
            "timestamp":
                validation[
                    TIMESTAMP_COLUMN
                ]
                .reset_index(
                    drop=True
                ),

            "observed_future_soil_moisture":
                observed_validation,

            "persistence_prediction":
                persistence_predictions,

            "persistence_absolute_error":
                np.abs(
                    observed_validation
                    -
                    persistence_predictions
                ),
        }
    )


    # -----------------------------------------------------
    # Train and evaluate
    # -----------------------------------------------------

    for (
        model_name,
        pipeline,
    ) in candidates.items():

        (
            result,
            fitted_pipeline,
            predictions,
        ) = evaluate_candidate(
            model_name=
                model_name,

            pipeline=
                pipeline,

            train=
                train,

            validation=
                validation,

            baseline_metrics=
                baseline_metrics,
        )


        result_rows.append(
            asdict(
                result
            )
        )


        fitted_models[
            model_name
        ] = fitted_pipeline


        safe_name = (
            model_name
            .lower()
            .replace(
                " ",
                "_",
            )
        )


        prediction_table[
            f"{safe_name}_prediction"
        ] = predictions


        prediction_table[
            f"{safe_name}_absolute_error"
        ] = np.abs(
            observed_validation
            -
            predictions
        )


    # -----------------------------------------------------
    # Comparative table
    # -----------------------------------------------------

    results = (
        pd.DataFrame(
            result_rows
        )
        .sort_values(
            by=[
                "mae",
                "rmse",
                "r2",
            ],
            ascending=[
                True,
                True,
                False,
            ],
        )
        .reset_index(
            drop=True
        )
    )


    selected_model_name = (
        select_best_candidate(
            results
        )
    )


    selected_pipeline = (
        fitted_models[
            selected_model_name
        ]
    )


    interpretation = (
        build_selection_interpretation(
            results=
                results,

            baseline_metrics=
                baseline_metrics,

            selected_model_name=
                selected_model_name,
        )
    )


    return {
        "train":
            train,

        "validation":
            validation,

        "final_test":
            final_test,

        "baseline_metrics":
            baseline_metrics,

        "results":
            results,

        "selected_model_name":
            selected_model_name,

        "selected_pipeline":
            selected_pipeline,

        "validation_predictions":
            prediction_table,

        "interpretation":
            interpretation,
    }


# =========================================================
# SAVE EXPERIMENTAL ARTIFACTS
# =========================================================

def save_model_selection_artifacts(
    selection: dict,
) -> None:
    """
    Save only the CRISP-DM experimental artifacts.

    IMPORTANT:
    This does NOT overwrite:

        artifacts/ml/soil_moisture_rf.joblib

    Therefore the production complementary RF remains
    untouched.
    """

    EXPERIMENT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )


    results: pd.DataFrame = (
        selection[
            "results"
        ]
    )


    predictions: pd.DataFrame = (
        selection[
            "validation_predictions"
        ]
    )


    baseline_metrics: RegressionMetrics = (
        selection[
            "baseline_metrics"
        ]
    )


    selected_model_name = str(
        selection[
            "selected_model_name"
        ]
    )


    selected_pipeline: Pipeline = (
        selection[
            "selected_pipeline"
        ]
    )


    train: pd.DataFrame = (
        selection[
            "train"
        ]
    )


    validation: pd.DataFrame = (
        selection[
            "validation"
        ]
    )


    # -----------------------------------------------------
    # Comparative metrics
    # -----------------------------------------------------

    results.to_csv(
        RESULTS_PATH,
        index=False,
    )


    # -----------------------------------------------------
    # Per-observation predictions
    # -----------------------------------------------------

    predictions.to_csv(
        VALIDATION_PREDICTIONS_PATH,
        index=False,
    )


    # -----------------------------------------------------
    # Metadata
    # -----------------------------------------------------

    metadata = {
        "methodology":
            "CRISP-DM",

        "stage":
            "MODEL_SELECTION",

        "selection_dataset":
            "2024 temporal validation",

        "final_test_dataset":
            "2025 isolated holdout",

        "selection_primary_metric":
            "MAE",

        "selection_secondary_metric":
            "RMSE",

        "selected_model":
            selected_model_name,

        "baseline": {
            "name":
                "Persistence",

            **asdict(
                baseline_metrics
            ),
        },

        "train_samples":
            int(
                len(
                    train
                )
            ),

        "validation_samples":
            int(
                len(
                    validation
                )
            ),

        "train_start":
            train[
                TIMESTAMP_COLUMN
            ]
            .min()
            .isoformat(),

        "train_end":
            train[
                TIMESTAMP_COLUMN
            ]
            .max()
            .isoformat(),

        "validation_start":
            validation[
                TIMESTAMP_COLUMN
            ]
            .min()
            .isoformat(),

        "validation_end":
            validation[
                TIMESTAMP_COLUMN
            ]
            .max()
            .isoformat(),

        "features":
            FEATURES,

        "target":
            TARGET,

        "prediction_horizon_hours":
            24,

        "physical_prediction_bounds": [
            PHYSICAL_MIN,
            PHYSICAL_MAX,
        ],

        # -------------------------------------------------
        # Architecture invariants
        # -------------------------------------------------

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

        "interpretation":
            selection[
                "interpretation"
            ],
    }


    METADATA_PATH.write_text(
        json.dumps(
            metadata,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


    # -----------------------------------------------------
    # Experimental selected candidate
    #
    # This artifact is deliberately separate from the
    # currently deployed Random Forest.
    # -----------------------------------------------------

    bundle = {
        "pipeline":
            selected_pipeline,

        "model_name":
            selected_model_name,

        "features":
            FEATURES,

        "target":
            TARGET,

        "prediction_horizon_hours":
            24,

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

        "selection_metadata":
            metadata,
    }


    joblib.dump(
        bundle,
        SELECTED_MODEL_PATH,
    )


# =========================================================
# MAIN
# =========================================================

def main() -> None:

    print()
    print(
        "=" * 90
    )

    print(
        "AGROTWIN · CRISP-DM MODEL TRAINING AND SELECTION"
    )

    print(
        "=" * 90
    )


    dataframe = (
        load_training_dataset()
    )


    selection = (
        run_model_selection(
            dataframe
        )
    )


    baseline_metrics: RegressionMetrics = (
        selection[
            "baseline_metrics"
        ]
    )


    results: pd.DataFrame = (
        selection[
            "results"
        ]
    )


    # -----------------------------------------------------
    # Partitions
    # -----------------------------------------------------

    print()
    print(
        "DATA PARTITIONS"
    )

    print(
        "-" * 90
    )


    print(
        "Train:      "
        f"{len(selection['train']):,} rows"
    )


    print(
        "Validation: "
        f"{len(selection['validation']):,} rows"
    )


    print(
        "Final test: "
        f"{len(selection['final_test']):,} rows "
        "(NOT USED FOR SELECTION)"
    )


    # -----------------------------------------------------
    # Persistence
    # -----------------------------------------------------

    print()
    print(
        "PERSISTENCE BENCHMARK"
    )

    print(
        "-" * 90
    )


    print(
        f"MAE:  "
        f"{baseline_metrics.mae:.6f}"
    )


    print(
        f"RMSE: "
        f"{baseline_metrics.rmse:.6f}"
    )


    print(
        f"R²:   "
        f"{baseline_metrics.r2:.6f}"
    )


    print(
        f"Bias: "
        f"{baseline_metrics.bias:+.6f}"
    )


    # -----------------------------------------------------
    # Candidate comparison
    # -----------------------------------------------------

    print()
    print(
        "MODEL SELECTION TABLE · VALIDATION 2024"
    )

    print(
        "-" * 90
    )


    display_columns = [
        "model_name",
        "mae",
        "rmse",
        "r2",
        "bias",
        "mae_improvement_vs_persistence_percent",
        "rmse_improvement_vs_persistence_percent",
        "train_seconds",
        "predict_seconds",
    ]


    print(
        results[
            display_columns
        ].to_string(
            index=False,

            float_format=lambda value:
                f"{value:.6f}",
        )
    )


    # -----------------------------------------------------
    # Selected model
    # -----------------------------------------------------

    print()
    print(
        "SELECTED MODEL"
    )

    print(
        "-" * 90
    )


    print(
        selection[
            "selected_model_name"
        ]
    )


    # -----------------------------------------------------
    # Interpretation
    # -----------------------------------------------------

    print()
    print(
        "INTERPRETATION"
    )

    print(
        "-" * 90
    )


    print(
        selection[
            "interpretation"
        ]
    )


    # -----------------------------------------------------
    # Save
    # -----------------------------------------------------

    save_model_selection_artifacts(
        selection
    )


    print()
    print(
        "ARTIFACTS"
    )

    print(
        "-" * 90
    )


    print(
        RESULTS_PATH
    )


    print(
        METADATA_PATH
    )


    print(
        SELECTED_MODEL_PATH
    )


    print(
        VALIDATION_PREDICTIONS_PATH
    )


    # -----------------------------------------------------
    # Architecture protection
    # -----------------------------------------------------

    print()
    print(
        "ARCHITECTURE NOTE"
    )

    print(
        "-" * 90
    )


    print(
        "The selected CRISP-DM candidate is an "
        "experimental complementary predictive model."
    )


    print(
        "It has NOT replaced the currently deployed "
        "Random Forest artifact."
    )


    print(
        "It has no decision authority, does not modify "
        "TrustedState and does not modify recommendations."
    )


    print()
    print(
        "=" * 90
    )

    print(
        "MODEL TRAINING COMPLETE"
    )

    print(
        "=" * 90
    )


if __name__ == "__main__":

    main()