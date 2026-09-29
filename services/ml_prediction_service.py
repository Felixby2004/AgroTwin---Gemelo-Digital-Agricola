from pathlib import Path

from ml.soil_moisture_model import (
    FEATURES,
    MODEL_PURPOSE,
    MODEL_STATUS,
    PREDICTION_HORIZON_HOURS,
    PROVENANCE,
    SoilMoistureRandomForest,
)


PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parents[1]
)

MODEL_PATH = (
    PROJECT_ROOT
    / "artifacts"
    / "ml"
    / "soil_moisture_rf.joblib"
)


class MLPredictionService:

    # ==================================================
    # AVAILABLE
    # ==================================================

    def model_available(
        self,
    ) -> bool:

        return MODEL_PATH.exists()


    # ==================================================
    # LOAD
    # ==================================================

    def load_model(
        self,
    ) -> SoilMoistureRandomForest:

        if not self.model_available():

            raise FileNotFoundError(
                "Random Forest model "
                "has not been trained."
            )

        return (
            SoilMoistureRandomForest
            .load(
                MODEL_PATH
            )
        )


    # ==================================================
    # STATUS
    # ==================================================

    def status(
        self,
    ) -> dict:

        base = {
            "available":
                self.model_available(),

            "model":
                "RandomForestRegressor",

            "model_status":
                MODEL_STATUS,

            "purpose":
                MODEL_PURPOSE,

            "target":
                "soil_moisture_change_24h",

            "output":
                "future_soil_moisture_24h",

            "prediction_horizon_hours":
                PREDICTION_HORIZON_HOURS,

            "provenance":
                PROVENANCE,

            "decision_authority":
                False,

            "modifies_trusted_state":
                False,

            "modifies_recommendation":
                False,

            "features":
                FEATURES,

            "validation_summary": {
                "method":
                    "ROLLING_ORIGIN",

                "period":
                    "2023-2025",

                "status":
                    "MIXED",

                "aggregate": {
                    "random_forest_mae":
                        0.004291,

                    "random_forest_rmse":
                        0.012492,

                    "random_forest_r2":
                        0.851056,

                    "persistence_mae":
                        0.003683,

                    "persistence_rmse":
                        0.011873,

                    "persistence_r2":
                        0.865465,

                    "mae_improvement_percent":
                        -16.50,

                    "rmse_improvement_percent":
                        -5.22,
                },

                "final_test_2025": {
                    "random_forest_mae":
                        0.003188,

                    "random_forest_rmse":
                        0.011129,

                    "random_forest_r2":
                        0.852674,

                    "mae_improvement_percent":
                        0.73,

                    "rmse_improvement_percent":
                        3.08,
                },
            },
        }


        if not self.model_available():
            return base


        model = self.load_model()

        base[
            "feature_importance"
        ] = (
            model.feature_importance()
        )

        return base


    # ==================================================
    # PREDICT
    # ==================================================

    def predict(
        self,
        features: dict,
    ) -> dict:

        model = self.load_model()

        result = model.predict(
            features
        )

        return {
            "model":
                "RandomForestRegressor",

            "model_status":
                MODEL_STATUS,

            "purpose":
                MODEL_PURPOSE,

            "prediction_horizon_hours":
                PREDICTION_HORIZON_HOURS,

            "unit":
                "m3/m3",

            "provenance":
                PROVENANCE,

            "decision_authority":
                False,

            "modifies_trusted_state":
                False,

            "modifies_recommendation":
                False,

            **result,
        }