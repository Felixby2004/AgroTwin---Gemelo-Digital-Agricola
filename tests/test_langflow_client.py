from api.services.langflow_client import extract_langflow_answer


def test_extract_langflow_answer():
    payload = {
        "outputs": [
            {
                "outputs": [
                    {
                        "results": {
                            "message": {
                                "text": "AgriTwin responde correctamente."
                            }
                        }
                    }
                ]
            }
        ]
    }

    assert extract_langflow_answer(payload) == "AgriTwin responde correctamente."
