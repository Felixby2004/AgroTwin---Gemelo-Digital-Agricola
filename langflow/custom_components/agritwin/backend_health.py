import requests

from lfx.custom.custom_component.component import Component
from lfx.io import MessageTextInput, Output
from lfx.schema import Data


class AgriTwinBackendHealth(Component):
    display_name = "AgriTwin - Backend Health"
    description = "Comprueba si el backend FastAPI de AgriTwin está disponible."
    icon = "Activity"
    name = "AgriTwinBackendHealth"

    inputs = [
        MessageTextInput(
            name="request_text",
            display_name="Solicitud",
            value="Comprobar disponibilidad del backend",
            tool_mode=True,
        ),
    ]

    outputs = [
        Output(
            name="result",
            display_name="Estado del Backend",
            method="check_backend",
        ),
    ]

    def check_backend(self) -> Data:
        url = (
            "http://host.docker.internal:8000"
            "/api/langflow/health"
        )

        response = requests.get(
            url,
            timeout=10,
        )

        response.raise_for_status()

        result = response.json()

        self.status = "Backend AgriTwin disponible"

        return Data(data=result)