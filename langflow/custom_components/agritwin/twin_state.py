import requests

from lfx.custom.custom_component.component import Component
from lfx.io import MessageTextInput, Output
from lfx.schema import Data


class AgriTwinTwinState(Component):
    display_name = "AgroTwin - Estado del Gemelo"

    description = (
        "Consulta el estado operacional y confiable actual "
        "de una parcela en el Gemelo Digital AgroTwin. "
        "Incluye evidencia, conocimiento del agricultor, "
        "estado confiable, recomendación y riesgo."
    )

    icon = "Sprout"
    name = "AgroTwinTwinState"

    inputs = [
        MessageTextInput(
            name="parcel_id",
            display_name="ID de parcela",
            info=(
                "Identificador real de la parcela registrada "
                "en AgroTwin."
            ),
            tool_mode=True,
        ),
    ]

    outputs = [
        Output(
            name="result",
            display_name="Estado del Gemelo",
            method="get_twin_state",
        ),
    ]

    def get_twin_state(self) -> Data:

        parcel_id = self.parcel_id.strip()

        if not parcel_id:
            return Data(
                data={
                    "status": "error",
                    "message": (
                        "Se requiere el identificador "
                        "de una parcela."
                    ),
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
                        "message": (
                            "La parcela no existe "
                            "en AgroTwin."
                        ),
                    }
                )

            response.raise_for_status()

            result = response.json()

            self.status = (
                f"Estado consultado: {parcel_id}"
            )

            return Data(
                data={
                    "status": "ok",
                    "source": "agrotwin_operational_state",
                    "parcel_id": parcel_id,
                    "state": result,
                }
            )

        except requests.RequestException as exc:

            self.status = (
                "Error consultando el Gemelo Digital"
            )

            return Data(
                data={
                    "status": "error",
                    "parcel_id": parcel_id,
                    "message": str(exc),
                }
            )