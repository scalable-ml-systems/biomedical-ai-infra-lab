"""Query API routes for the governed biomedical GraphRAG pipeline."""

from hashlib import sha256
from typing import TypeAlias

from fastapi import APIRouter

from app.contracts.governance import (
    EvidenceStrength,
    RefusalResponse,
    ResponseMode,
    SafetyDecisionReason,
)
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

QueryApiResponse: TypeAlias = StructuredQueryResponse | BlockedQueryResponse


router = APIRouter(tags=["query"])


def _build_stable_id(prefix: str, text: str) -> str:
    """Build a short stable ID for placeholder API responses."""

    digest = sha256(text.encode("utf-8")).hexdigest()[:12]
    return f"{prefix}-{digest}"


def _looks_like_personal_medical_advice(query_text: str) -> bool:
    """Very small deterministic safety placeholder.

    This is not the final classifier. It only proves that the API can return
    a typed blocked response before Phase 2 classification logic exists.
    """

    lowered_query = query_text.lower()

    blocked_phrases = [
        "should i take",
        "should i stop",
        "what dose",
        "what dosage",
        "can i take",
        "is it safe for me",
        "safe for me",
        "am i allowed to",
        "which medication is better for me",
    ]

    return any(phrase in lowered_query for phrase in blocked_phrases)


def _classify_placeholder_query(query_text: str) -> QueryType:
    """Classify a query using simple placeholder rules."""

    lowered_query = query_text.lower()

    if _looks_like_personal_medical_advice(query_text):
        return QueryType.PERSONAL_MEDICAL_ADVICE

    if "contraindication" in lowered_query:
        return QueryType.CONTRAINDICATION_QUESTION

    if "adverse" in lowered_query or "side effect" in lowered_query:
        return QueryType.ADVERSE_REACTION_QUESTION

    if "pubmed" in lowered_query or "literature" in lowered_query:
        return QueryType.PUBMED_LITERATURE_QUESTION

    if "interaction" in lowered_query or "with ibuprofen" in lowered_query:
        return QueryType.DRUG_INTERACTION_EVIDENCE_QUESTION

    if "warning" in lowered_query or "precaution" in lowered_query:
        return QueryType.WARNING_QUESTION

    if "label" in lowered_query:
        return QueryType.LABEL_SUMMARY

    return QueryType.UNKNOWN


def _build_blocked_response(request: QueryRequest) -> BlockedQueryResponse:
    """Build a typed blocked response for unsafe medical-advice queries."""

    query_id = _build_stable_id("query", request.query)
    response_id = _build_stable_id("response-blocked", request.query)
    safety_decision_id = build_ontology_object_id(
        OntologyObjectType.SAFETY_DECISION,
        SourceSystem.SYSTEM,
        f"{query_id}-safety-decision",
    )
    refusal_object_id = build_ontology_object_id(
        OntologyObjectType.REFUSAL_RESPONSE,
        SourceSystem.SYSTEM,
        f"{query_id}-refusal",
    )

    message = (
        "I cannot provide personal medical advice or determine whether a "
        "medication is appropriate for you."
    )
    safe_redirect = (
        "I can summarize what public drug labels and biomedical literature say, "
        "but you should consult a qualified healthcare professional for personal "
        "medical decisions."
    )

    blocked_result = BlockedQueryResult(
        query_id=query_id,
        original_query=request.query,
        query_type=QueryType.PERSONAL_MEDICAL_ADVICE,
        safety_reason=SafetyDecisionReason.PERSONAL_MEDICAL_ADVICE,
        response_mode=ResponseMode.SAFE_REFUSAL,
        user_visible_message=message,
        safe_redirect=safe_redirect,
        matched_terms=["personal-medical-advice-placeholder"],
        safety_decision_object_id=safety_decision_id,
        refusal_response_object_id=refusal_object_id,
    )

    refusal_response = RefusalResponse(
        object_id=refusal_object_id,
        source_object_id=f"{query_id}-refusal",
        refusal_reason=SafetyDecisionReason.PERSONAL_MEDICAL_ADVICE,
        message=message,
        safe_redirect=safe_redirect,
        safety_decision_object_id=safety_decision_id,
    )

    return BlockedQueryResponse(
        response_id=response_id,
        response_status=ResponseStatus.BLOCKED,
        response_mode=ResponseMode.SAFE_REFUSAL,
        query_id=query_id,
        original_query=request.query,
        query_type=QueryType.PERSONAL_MEDICAL_ADVICE,
        blocked_result=blocked_result,
        refusal_response=refusal_response,
        message=message,
        safe_redirect=safe_redirect,
        safety_decision_object_id=safety_decision_id,
        refusal_response_object_id=refusal_object_id,
        audit_id=f"audit-placeholder-{query_id}",
    )


def _build_structured_placeholder_response(request: QueryRequest) -> StructuredQueryResponse:
    """Build a typed placeholder response for safe evidence queries."""

    query_id = _build_stable_id("query", request.query)
    response_id = _build_stable_id("response", request.query)
    query_type = _classify_placeholder_query(request.query)

    generated_answer_id = build_ontology_object_id(
        OntologyObjectType.GENERATED_ANSWER,
        SourceSystem.EXTERNAL_LLM,
        f"{query_id}-placeholder-answer",
    )

    classification = QueryClassification(
        query_id=query_id,
        query_text=request.query,
        query_type=query_type,
        confidence=0.50,
        is_safe_evidence_query=True,
        requires_safety_refusal=False,
        safety_reason=SafetyDecisionReason.SAFE_PUBLIC_EVIDENCE_QUERY,
        response_mode=ResponseMode.ANSWER_WITH_LIMITATIONS,
        classification_reason=(
            "Placeholder deterministic classification. Full classifier will be "
            "implemented in Phase 2."
        ),
    )

    answer_text = (
        "This is a typed placeholder response. The request was accepted as a "
        "safe public-evidence query, but retrieval, GraphRAG, generation, "
        "validation, and audit logging are not implemented yet."
    )

    generated_answer = GeneratedAnswer(
        object_id=generated_answer_id,
        source_object_id=f"{query_id}-placeholder-answer",
        answer_text=answer_text,
        query_id=query_id,
        response_mode=ResponseMode.ANSWER_WITH_LIMITATIONS,
        evidence_strength=EvidenceStrength.INSUFFICIENT,
        validation_status=ValidationStatus.NOT_CHECKED,
        llm_provider="placeholder",
        llm_model="none",
        limitations=[
            "No DailyMed evidence has been retrieved yet.",
            "No PubMed evidence has been retrieved yet.",
            "No graph paths have been retrieved yet.",
            "No claim validation has been run yet.",
        ],
    )

    return StructuredQueryResponse(
        response_id=response_id,
        response_status=ResponseStatus.SUCCEEDED,
        response_mode=ResponseMode.ANSWER_WITH_LIMITATIONS,
        query_id=query_id,
        original_query=request.query,
        query_type=query_type,
        classification=classification,
        generated_answer=generated_answer,
        answer_text=answer_text,
        evidence_strength=EvidenceStrength.INSUFFICIENT,
        validation_status=ValidationStatus.NOT_CHECKED,
        audit_id=f"audit-placeholder-{query_id}",
        warnings=[
            "Contract-shaped placeholder only.",
            "Retrieval and validation are not implemented yet.",
        ],
        limitations=generated_answer.limitations,
    )


@router.post("/query", response_model=QueryApiResponse)
def query_placeholder(request: QueryRequest) -> QueryApiResponse:
    """Return a contract-shaped placeholder response.

    Phase 1 proves the API can speak the ontology contract language.
    Real query classification, retrieval, generation, validation, and audit
    logging will be implemented in later phases.
    """

    if _looks_like_personal_medical_advice(request.query):
        return _build_blocked_response(request)

    return _build_structured_placeholder_response(request)
