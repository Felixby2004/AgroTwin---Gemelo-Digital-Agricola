from __future__ import annotations

from sqlalchemy.orm import (
    Session,
)

from services.ml_feature_builder_service import (
    MLFeatureBuilderService,
)

from services.ml_prediction_service import (
    MLPredictionService,
)


class ParcelMLForecastService:

    def __init__(
        self,
        session: Session,
    ) -> None:

        self.feature_builder = (
            MLFeatureBuilderService(
                session
            )
        )

        self.ml_service = (
            MLPredictionService()
        )


    def forecast(
        self,
        parcel_id: str,
    ) -> dict:

        feature_result = (
            self.feature_builder
            .build(
                parcel_id
            )
        )


        prediction = (
            self.ml_service
            .predict(
                feature_result[
                    "features"
                ]
            )
        )


        return {
            "parcel_id":
                parcel_id,

            "reference_timestamp":
                feature_result[
                    "reference_timestamp"
                ],

            "model":
                prediction[
                    "model"
                ],

            "model_status":
                prediction[
                    "model_status"
                ],

            "purpose":
                prediction[
                    "purpose"
                ],

            "prediction_horizon_hours":
                prediction[
                    "prediction_horizon_hours"
                ],

            "provenance":
                prediction[
                    "provenance"
                ],

            "decision_authority":
                False,

            "modifies_trusted_state":
                False,

            "modifies_recommendation":
                False,

            "feature_availability":
                feature_result[
                    "feature_availability"
                ],

            "current_soil_moisture":
                prediction[
                    "current_soil_moisture"
                ],

            "predicted_delta_24h":
                prediction[
                    "predicted_delta_24h"
                ],

            "predicted_soil_moisture_24h":
                prediction[
                    "predicted_soil_moisture_24h"
                ],

            "delta_percent":
                prediction[
                    "delta_percent"
                ],

            "trend":
                prediction[
                    "trend"
                ],

            "uncertainty":
                prediction[
                    "uncertainty"
                ],

            "explanation":
                prediction[
                    "explanation"
                ],
        }