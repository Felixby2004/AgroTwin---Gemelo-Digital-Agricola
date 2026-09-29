from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import shap

from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)
from sklearn.pipeline import Pipeline


# ======================================================
# MODEL DEFINITION
# ======================================================

FEATURES = [
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


TARGET = "soil_moisture_change_24h"

MODEL_STATUS = "MIXED_COMPLEMENTARY_MODEL"

MODEL_PURPOSE = "COMPLEMENTARY_PREDICTION"

PROVENANCE = "MODEL_DERIVED"

PREDICTION_HORIZON_HOURS = 24


# ======================================================
# METRICS
# ======================================================

@dataclass
class RegressionMetrics:
    mae: float
    rmse: float
    r2: float


@dataclass
class ModelEvaluation:
    model: RegressionMetrics
    baseline: RegressionMetrics

    mae_improvement_percent: float
    rmse_improvement_percent: float

    train_samples: int
    test_samples: int

    train_start: str
    train_end: str

    test_start: str
    test_end: str


# ======================================================
# RANDOM FOREST
# ======================================================

class SoilMoistureRandomForest:

    def __init__(
        self,
        random_state: int = 42,
    ) -> None:

        self.random_state = random_state

        self.pipeline = Pipeline(
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
                        random_state=random_state,
                        n_jobs=-1,
                    ),
                ),
            ]
        )

        self.evaluation: ModelEvaluation | None = None


    # ==================================================
    # METRICS
    # ==================================================

    @staticmethod
    def _metrics(
        observed,
        predicted,
    ) -> RegressionMetrics:

        return RegressionMetrics(
            mae=float(
                mean_absolute_error(
                    observed,
                    predicted,
                )
            ),
            rmse=float(
                mean_squared_error(
                    observed,
                    predicted,
                )
                ** 0.5
            ),
            r2=float(
                r2_score(
                    observed,
                    predicted,
                )
            ),
        )


    # ==================================================
    # TEMPORAL TRAINING
    # ==================================================

    def train_temporal(
        self,
        dataframe: pd.DataFrame,
        test_year: int = 2025,
    ) -> ModelEvaluation:

        required = (
            FEATURES
            + [
                TARGET,
                "future_soil_moisture_24h",
                "timestamp",
            ]
        )

        missing = [
            column
            for column in required
            if column not in dataframe.columns
        ]

        if missing:
            raise ValueError(
                "Missing columns: "
                + ", ".join(missing)
            )

        data = dataframe.copy()

        data["timestamp"] = pd.to_datetime(
            data["timestamp"],
            errors="coerce",
            utc=True,
        )

        data = data.dropna(
            subset=[
                "timestamp",
                "soil_moisture",
                TARGET,
                "future_soil_moisture_24h",
            ]
        )

        train = data[
            data["timestamp"].dt.year
            < test_year
        ].copy()

        test = data[
            data["timestamp"].dt.year
            == test_year
        ].copy()

        if len(train) < 100:
            raise ValueError(
                "Not enough training observations."
            )

        if len(test) < 50:
            raise ValueError(
                "Not enough temporal test observations."
            )

        X_train = train[FEATURES]
        y_train = train[TARGET]

        X_test = test[FEATURES]

        self.pipeline.fit(
            X_train,
            y_train,
        )

        # RF predicts DELTA, not absolute moisture.
        predicted_delta = (
            self.pipeline.predict(
                X_test
            )
        )

        current_moisture = (
            test["soil_moisture"]
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
        )

        model_metrics = self._metrics(
            observed_future,
            predicted_future,
        )

        # Persistence baseline:
        # theta(t+24) = theta(t)
        baseline_predictions = (
            current_moisture
        )

        baseline_metrics = self._metrics(
            observed_future,
            baseline_predictions,
        )

        mae_improvement = (
            (
                baseline_metrics.mae
                - model_metrics.mae
            )
            / baseline_metrics.mae
            * 100
            if baseline_metrics.mae > 0
            else 0.0
        )

        rmse_improvement = (
            (
                baseline_metrics.rmse
                - model_metrics.rmse
            )
            / baseline_metrics.rmse
            * 100
            if baseline_metrics.rmse > 0
            else 0.0
        )

        self.evaluation = ModelEvaluation(
            model=model_metrics,
            baseline=baseline_metrics,

            mae_improvement_percent=float(
                mae_improvement
            ),

            rmse_improvement_percent=float(
                rmse_improvement
            ),

            train_samples=len(train),
            test_samples=len(test),

            train_start=(
                train["timestamp"]
                .min()
                .isoformat()
            ),

            train_end=(
                train["timestamp"]
                .max()
                .isoformat()
            ),

            test_start=(
                test["timestamp"]
                .min()
                .isoformat()
            ),

            test_end=(
                test["timestamp"]
                .max()
                .isoformat()
            ),
        )

        return self.evaluation


    # ==================================================
    # INFERENCE
    # ==================================================

    def predict(
        self,
        features: dict[
            str,
            float | None,
        ],
    ) -> dict:

        dataframe = pd.DataFrame(
            [
                {
                    feature:
                        features.get(feature)

                    for feature
                    in FEATURES
                }
            ]
        )

        current_soil_moisture = (
            features.get(
                "soil_moisture"
            )
        )

        if current_soil_moisture is None:
            raise ValueError(
                "soil_moisture is required."
            )

        current_soil_moisture = float(
            current_soil_moisture
        )

        # ----------------------------------------------
        # RF predicts Δ soil moisture
        # ----------------------------------------------

        predicted_delta = float(
            self.pipeline.predict(
                dataframe
            )[0]
        )

        # ----------------------------------------------
        # Reconstruct absolute future value
        # ----------------------------------------------

        predicted_future = (
            current_soil_moisture
            + predicted_delta
        )

        # Physical guard
        predicted_future = float(
            np.clip(
                predicted_future,
                0.0,
                0.8,
            )
        )

        effective_delta = (
            predicted_future
            - current_soil_moisture
        )

        if effective_delta < -0.005:
            trend = "DECREASING"

        elif effective_delta > 0.005:
            trend = "INCREASING"

        else:
            trend = "STABLE"


        # ----------------------------------------------
        # Prepare transformed sample
        # ----------------------------------------------

        imputer: SimpleImputer = (
            self.pipeline
            .named_steps[
                "imputer"
            ]
        )

        model: RandomForestRegressor = (
            self.pipeline
            .named_steps[
                "model"
            ]
        )

        transformed = (
            imputer.transform(
                dataframe
            )
        )


        # ----------------------------------------------
        # TREE DISTRIBUTION
        #
        # Trees predict Δ.
        # Convert every tree prediction to absolute
        # future moisture.
        # ----------------------------------------------

        tree_delta_predictions = np.array(
            [
                tree.predict(
                    transformed
                )[0]

                for tree
                in model.estimators_
            ],
            dtype=float,
        )

        tree_future_predictions = (
            current_soil_moisture
            + tree_delta_predictions
        )

        tree_future_predictions = (
            np.clip(
                tree_future_predictions,
                0.0,
                0.8,
            )
        )

        ensemble_std = float(
            np.std(
                tree_future_predictions
            )
        )

        p10 = float(
            np.percentile(
                tree_future_predictions,
                10,
            )
        )

        p90 = float(
            np.percentile(
                tree_future_predictions,
                90,
            )
        )


        # ----------------------------------------------
        # SHAP
        #
        # IMPORTANT:
        # SHAP explains predicted DELTA.
        # ----------------------------------------------

        explainer = shap.TreeExplainer(
            model
        )

        shap_values = (
            explainer.shap_values(
                transformed
            )
        )

        shap_array = np.asarray(
            shap_values
        )

        if shap_array.ndim == 2:
            sample_shap = shap_array[0]

        else:
            sample_shap = (
                shap_array.reshape(-1)
            )

        explanations = []

        for index, feature in enumerate(
            FEATURES
        ):

            contribution = float(
                sample_shap[index]
            )

            explanations.append(
                {
                    "feature":
                        feature,

                    "contribution_to_delta":
                        contribution,

                    "direction":
                        (
                            "INCREASE_MOISTURE"
                            if contribution > 0
                            else
                            "DECREASE_MOISTURE"
                            if contribution < 0
                            else
                            "NEUTRAL"
                        ),
                }
            )

        explanations.sort(
            key=lambda item:
                abs(
                    item[
                        "contribution_to_delta"
                    ]
                ),
            reverse=True,
        )


        # ----------------------------------------------
        # Percentage change
        # ----------------------------------------------

        delta_percent = None

        if current_soil_moisture != 0:
            delta_percent = float(
                effective_delta
                / current_soil_moisture
                * 100
            )


        return {
            "current_soil_moisture":
                current_soil_moisture,

            "predicted_delta_24h":
                effective_delta,

            "predicted_soil_moisture_24h":
                predicted_future,

            "delta_percent":
                delta_percent,

            "trend":
                trend,

            "uncertainty": {
                "method":
                    "TREE_ENSEMBLE_DISPERSION",

                "ensemble_std":
                    ensemble_std,

                "p10":
                    p10,

                "p90":
                    p90,
            },

            "explanation": {
                "method":
                    "SHAP_TREE_EXPLAINER",

                "explained_output":
                    "SOIL_MOISTURE_CHANGE_24H",

                "features":
                    explanations,
            },
        }


    # ==================================================
    # GLOBAL FEATURE IMPORTANCE
    # ==================================================

    def feature_importance(
        self,
    ) -> list[dict]:

        model: RandomForestRegressor = (
            self.pipeline
            .named_steps[
                "model"
            ]
        )

        result = [
            {
                "feature":
                    feature,

                "importance":
                    float(
                        importance
                    ),
            }

            for (
                feature,
                importance,
            )
            in zip(
                FEATURES,
                model.feature_importances_,
                strict=True,
            )
        ]

        result.sort(
            key=lambda item:
                item["importance"],
            reverse=True,
        )

        return result


    # ==================================================
    # SAVE
    # ==================================================

    def save(
        self,
        path: str | Path,
    ) -> None:

        target = Path(path)

        target.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        payload = {
            "pipeline":
                self.pipeline,

            "evaluation":
                self.evaluation,

            "features":
                FEATURES,

            "target":
                TARGET,

            "model_name":
                "RandomForestRegressor",

            "model_status":
                MODEL_STATUS,

            "purpose":
                MODEL_PURPOSE,

            "provenance":
                PROVENANCE,

            "prediction_horizon_hours":
                PREDICTION_HORIZON_HOURS,

            "decision_authority":
                False,

            "modifies_trusted_state":
                False,

            "modifies_recommendation":
                False,
        }

        joblib.dump(
            payload,
            target,
        )


    # ==================================================
    # LOAD
    # ==================================================

    @classmethod
    def load(
        cls,
        path: str | Path,
    ) -> "SoilMoistureRandomForest":

        payload = joblib.load(
            path
        )

        instance = cls()

        instance.pipeline = (
            payload[
                "pipeline"
            ]
        )

        instance.evaluation = (
            payload.get(
                "evaluation"
            )
        )

        return instance


    # ==================================================
    # EVALUATION
    # ==================================================

    def evaluation_dict(
        self,
    ) -> dict | None:

        if self.evaluation is None:
            return None

        return asdict(
            self.evaluation
        )