import os
from typing import Any

import httpx


class LangflowClientError(RuntimeError):
    pass


def extract_langflow_answer(payload: dict[str, Any]) -> str:
    try:
        result = payload["outputs"][0]["outputs"][0]["results"]
        message = result["message"]

        if isinstance(message, dict):
            text = message.get("text")

            if not text and isinstance(message.get("data"), dict):
                text = message["data"].get("text")

            if text:
                return str(text)

    except (KeyError, IndexError, TypeError):
        pass

    raise LangflowClientError(
        "No se pudo extraer la respuesta del Agent de Langflow."
    )


async def run_langflow(
    message: str,
    session_id: str,
) -> str:

    server_url = os.getenv("LANGFLOW_SERVER_URL")
    flow_id = os.getenv("LANGFLOW_FLOW_ID")
    api_key = os.getenv("LANGFLOW_API_KEY")

    if not server_url:
        raise LangflowClientError(
            "LANGFLOW_SERVER_URL no está configurado."
        )

    if not flow_id:
        raise LangflowClientError(
            "LANGFLOW_FLOW_ID no está configurado."
        )

    if not api_key:
        raise LangflowClientError(
            "LANGFLOW_API_KEY no está configurado."
        )

    url = (
        f"{server_url.rstrip('/')}"
        f"/api/v1/run/{flow_id}"
    )

    headers = {
        "x-api-key": api_key,
        "Content-Type": "application/json",
    }

    body = {
        "input_value": message,
        "input_type": "chat",
        "output_type": "chat",
        "session_id": session_id,
    }

    try:
        async with httpx.AsyncClient(
            timeout=90.0
        ) as client:

            response = await client.post(
                url,
                headers=headers,
                json=body,
            )

            response.raise_for_status()

    except httpx.HTTPStatusError as exc:
        raise LangflowClientError(
            "Langflow respondió con error "
            f"{exc.response.status_code}: "
            f"{exc.response.text[:500]}"
        ) from exc

    except httpx.RequestError as exc:
        raise LangflowClientError(
            f"No se pudo contactar con Langflow: {exc}"
        ) from exc

    return extract_langflow_answer(
        response.json()
    )
