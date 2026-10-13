import requests

from lfx.custom.custom_component.component import Component
from lfx.io import MessageTextInput, Output
from lfx.schema import Data


class AgriTwinExplanation(Component):
    display_name = "AgriTwin - Explicación XAI"

    description = (
        "Explica una recomendación de AgriTwin utilizando "
        "las razones del motor multicriterio, riesgo, estado "
        "de calidad, conflictos humano-máquina y trazabilidad."
    )

    icon = "Brain"
    name = "AgriTwinExplanation"

    inputs = [
        MessageTextInput(
            name="parcel_id",
            display_name="ID de parcela",
            info="Identificador real de la parcela.",
            tool_mode=True,
        ),
    ]

    outputs = [
        Output(
            name="result",
            display_name="Explicación",
            method="get_explanation",
        ),
    ]

    def get_explanation(self) -> Data:

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

            latest_trace = (
                state.get("latest_trace") or {}
            )

            result = {
                "status": "ok",
                "source": "agritwin_explainability",

                "explanation_type": (
                    "decision_trace_and_reason_based"
                ),

                "parcel_id": parcel_id,

                "decision": {
                    "recommendation_status":
                        recommendation.get("status"),

                    "recommendation_allowed":
                        recommendation.get("allowed"),

                    "irrigation_mm":
                        recommendation.get("irrigation_mm"),

                    "score":
                        recommendation.get("score"),

                    "reasons":
                        recommendation.get(
                            "reasons",
                            [],
                        ),
                },

                "risk": {
                    "level":
                        risk.get("level"),

                    "confidence":
                        risk.get("confidence"),

                    "requires_human_confirmation":
                        risk.get(
                            "requires_human_confirmation"
                        ),

                    "reasons":
                        risk.get(
                            "reasons",
                            [],
                        ),
                },

                "quality": {
                    "quality_gate_status":
                        state.get(
                            "quality_gate_status"
                        ),

                    "recommendation_allowed":
                        state.get(
                            "recommendation_allowed"
                        ),

                    "evidence":
                        state.get(
                            "evidence"
                        ),
                },

                "participatory_context": {
                    "farmer_knowledge":
                        state.get(
                            "farmer_knowledge"
                        ),

                    "conflicts_count":
                        state.get(
                            "conflicts_count"
                        ),

                    "conflicts":
                        state.get(
                            "conflicts",
                            [],
                        ),
                },

                "trace": latest_trace,

                "xai_scope": (
                    "Explicación basada en razones del motor, "
                    "riesgo, evidencia, conocimiento del "
                    "agricultor y trazabilidad de decisión. "
                    "No corresponde a atribuciones SHAP/LIME."
                ),
            }

            self.status = (
                f"Explicación generada: {parcel_id}"
            )

            return Data(data=result)

        except requests.RequestException as exc:

            self.status = "Error obteniendo explicación"

            return Data(
                data={
                    "status": "error",
                    "parcel_id": parcel_id,
                    "message": str(exc),
                }
            )