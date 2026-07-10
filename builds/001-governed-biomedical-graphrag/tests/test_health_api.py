from app.main import create_app
from fastapi.testclient import TestClient


def test_health_endpoint_returns_ok() -> None:
    client = TestClient(create_app())

    response = client.get("/health")

    assert response.status_code == 200

    payload = response.json()

    assert payload["status"] == "ok"
    assert payload["service"] == "governed-biomedical-graphrag"
    assert payload["build"] == "001-governed-biomedical-graphrag"
    assert payload["app_env"] == "local"
    assert payload["pubmed_enabled"] is True
    assert payload["graph_validation_enabled"] is True
    assert payload["strict_safety_enabled"] is True
    assert "timestamp_utc" in payload
