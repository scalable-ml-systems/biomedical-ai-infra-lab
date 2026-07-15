from app.main import create_app
from fastapi.testclient import TestClient


def test_query_placeholder_endpoint_returns_structured_contract_response() -> None:
    client = TestClient(create_app())

    request_payload = {"query": "What does the official label say about warnings for warfarin?"}

    response = client.post("/query", json=request_payload)

    assert response.status_code == 200

    payload = response.json()

    assert payload["response_status"] == "succeeded"
    assert payload["response_mode"] == "answer_with_limitations"
    assert payload["original_query"] == request_payload["query"]
    assert payload["query_type"] == "warning_question"
    assert payload["answer_text"] is not None
    assert payload["generated_answer"] is not None
    assert payload["evidence_strength"] == "insufficient"
    assert payload["validation_status"] == "not_checked"
    assert payload["audit_id"].startswith("audit-placeholder-query-")


def test_query_placeholder_endpoint_blocks_personal_medical_advice() -> None:
    client = TestClient(create_app())

    request_payload = {"query": "Should I take warfarin with ibuprofen?"}

    response = client.post("/query", json=request_payload)

    assert response.status_code == 200

    payload = response.json()

    assert payload["response_status"] == "blocked"
    assert payload["response_mode"] == "safe_refusal"
    assert payload["query_type"] == "personal_medical_advice"
    assert payload["message"].startswith("I cannot provide personal medical advice")
    assert payload["safe_redirect"] is not None
    assert payload["blocked_result"] is not None
    assert payload["audit_id"].startswith("audit-placeholder-query-")
