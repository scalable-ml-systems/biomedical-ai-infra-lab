from app.main import create_app
from fastapi.testclient import TestClient


def test_query_placeholder_endpoint_returns_query() -> None:
    client = TestClient(create_app())

    request_payload = {"query": "What does the official label say about warnings for warfarin?"}

    response = client.post("/query", json=request_payload)

    assert response.status_code == 200

    payload = response.json()

    assert payload["query"] == request_payload["query"]
    assert "placeholder" in payload["message"].lower()
