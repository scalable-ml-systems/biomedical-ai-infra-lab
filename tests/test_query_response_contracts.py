from app.contracts.governance import EvidenceStrength, ResponseMode, SafetyDecisionReason
from app.contracts.ontology_base import (
    OntologyObjectType,
    SourceSystem,
    ValidationStatus,
    build_ontology_object_id,
)
from app.contracts.query_contracts import (
    BlockedQueryResult,
    QueryClassification,
    QueryRequest,
    QueryType,
)
from app.contracts.response_contracts import (
    BlockedQueryResponse,
    GeneratedAnswer,
    ResponseStatus,
    StructuredQueryResponse,
)


def test_query_request_contract_instantiates() -> None:
    request = QueryRequest(
        query="What does the official label say about warnings for warfarin?",
        requested_drug_names=["warfarin"],
    )

    assert request.query.startswith("What does the official label")
    assert request.include_pubmed is True
    assert request.include_graph_paths is True


def test_query_classification_contract_instantiates() -> None:
    classification = QueryClassification(
        query_id="query-001",
        query_text="What does the official label say about warnings for warfarin?",
        query_type=QueryType.WARNING_QUESTION,
        confidence=0.97,
        is_safe_evidence_query=True,
        requires_safety_refusal=False,
        safety_reason=SafetyDecisionReason.SAFE_PUBLIC_EVIDENCE_QUERY,
        response_mode=ResponseMode.ANSWER_WITH_EVIDENCE,
    )

    assert classification.query_type == QueryType.WARNING_QUESTION
    assert classification.is_safe_evidence_query is True


def test_structured_query_response_contract_instantiates() -> None:
    generated_answer = GeneratedAnswer(
        object_id=build_ontology_object_id(
            OntologyObjectType.GENERATED_ANSWER,
            SourceSystem.EXTERNAL_LLM,
            "generated-answer-001",
        ),
        source_object_id="generated-answer-001",
        answer_text=(
            "Public label evidence for warfarin includes warnings related to "
            "bleeding risk. This is an educational evidence summary only."
        ),
        query_id="query-001",
        response_mode=ResponseMode.ANSWER_WITH_EVIDENCE,
        evidence_strength=EvidenceStrength.DIRECTLY_SUPPORTED,
        validation_status=ValidationStatus.SUPPORTED,
    )

    response = StructuredQueryResponse(
        response_id="response-001",
        response_status=ResponseStatus.SUCCEEDED,
        response_mode=ResponseMode.ANSWER_WITH_EVIDENCE,
        query_id="query-001",
        original_query="What does the official label say about warnings for warfarin?",
        query_type=QueryType.WARNING_QUESTION,
        generated_answer=generated_answer,
        answer_text=generated_answer.answer_text,
        evidence_strength=EvidenceStrength.DIRECTLY_SUPPORTED,
        validation_status=ValidationStatus.SUPPORTED,
        audit_id="audit-001",
    )

    assert response.response_status == ResponseStatus.SUCCEEDED
    assert response.query_type == QueryType.WARNING_QUESTION
    assert response.audit_id == "audit-001"


def test_blocked_query_response_contract_instantiates() -> None:
    blocked_result = BlockedQueryResult(
        query_id="query-002",
        original_query="Should I take warfarin with ibuprofen?",
        query_type=QueryType.PERSONAL_MEDICAL_ADVICE,
        safety_reason=SafetyDecisionReason.PERSONAL_MEDICAL_ADVICE,
        response_mode=ResponseMode.SAFE_REFUSAL,
        user_visible_message=(
            "I cannot provide personal medical advice or determine whether "
            "medications are appropriate for you."
        ),
        safe_redirect=(
            "I can summarize what public drug labels and biomedical literature "
            "say about warfarin, ibuprofen, and bleeding-related warnings."
        ),
    )

    response = BlockedQueryResponse(
        response_id="response-blocked-001",
        query_id="query-002",
        original_query="Should I take warfarin with ibuprofen?",
        query_type=QueryType.PERSONAL_MEDICAL_ADVICE,
        blocked_result=blocked_result,
        message=blocked_result.user_visible_message,
        safe_redirect=blocked_result.safe_redirect,
        audit_id="audit-002",
    )

    assert response.response_status == ResponseStatus.BLOCKED
    assert response.response_mode == ResponseMode.SAFE_REFUSAL
    assert response.audit_id == "audit-002"
