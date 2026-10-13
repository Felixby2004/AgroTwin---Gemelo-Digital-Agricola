import requests

from lfx.custom.custom_component.component import Component
from lfx.io import MessageTextInput, Output
from lfx.schema import Data


class AgriTwinIrrigation(Component):
    display_name = "AgriTwin - Recomendación de Riego"

    description = (
        "Consulta la recomendación de riego real generada por "
        "el motor multicriterio de AgriTwin para una parcela. "
        "Devuelve cantidad de riego, score, razones y riesgo."
    )

    icon = "Droplets"
    name = "AgriTwinIrrigation"

    inputs = [
        MessageTextInput(
            name="parcel_id",
            display_name="ID de parcela",
            info="Identificador real de la parcela en AgriTwin.",
            tool_mode=True,
        ),
    ]

    outputs = [
        Output(
            name="result",
            display_name="Recomendación de Riego",
            method="get_irrigation_recommendation",
        ),
    ]

    def get_irrigation_recommendation(self) -> Data:

        parcel_id = self.parcel_id.strip()

        if not parcel_id:
            return Data(
                data={
                    "status": "error",
                    "message": "Se requiere un ID de parcela.",
                }
            )

        url = (
            "http://host.docker.internal:8000"
            f"/parcels/{parcel_id}/state"
        )

        try:
            response = requests.get(
                url,
                timeout=30,
            )

            if response.status_code == 404:
                return Data(
                    data={
                        "status": "not_found",
                        "parcel_id": parcel_id,
                        "message": "La parcela no existe.",
                    }
                )

            response.raise_for_status()

            state = response.json()

            recommendation = (
                state.get("recommendation") or {}
            )

            risk = (
                state.get("risk") or {}
            )

            irrigation_mm = (
                recommendation.get("irrigation_mm")
            )

            irrigation_required = (
                irrigation_mm is not None
                and irrigation_mm > 0
            )

            result = {
                "status": "ok",
                "source": "agritwin_multicriteria_engine",

                "parcel_id": parcel_id,

                "recommendation": {
                    "status": recommendation.get(
                        "status"
                    ),

                    "allowed": recommendation.get(
                        "allowed"
                    ),

                    "irrigation_required": (
                        irrigation_required
                    ),

                    "irrigation_mm": irrigation_mm,

                    "score": recommendation.get(
                        "score"
                    ),

                    "reasons": recommendation.get(
                        "reasons",
                        [],
                    ),
                },

                "risk": {
                    "level": risk.get(
                        "level"
                    ),

                    "confidence": risk.get(
                        "confidence"
                    ),

                    "requires_human_confirmation": (
                        risk.get(
                            "requires_human_confirmation"
                        )
                    ),

                    "reasons": risk.get(
                        "reasons",
                        [],
                    ),
                },

                "quality_gate_status": (
                    state.get(
                        "quality_gate_status"
                    )
                ),

                "recommendation_allowed": (
                    state.get(
                        "recommendation_allowed"
                    )
                ),
            }

            self.status = (
                f"Recomendación consultada: {parcel_id}"
            )

            return Data(data=result)

        except requests.RequestException as exc:

            self.status = (
                "Error consultando recomendación"
            )

            return Data(
                data={
                    "status": "error",
                    "parcel_id": parcel_id,
                    "message": str(exc),
                }
            )