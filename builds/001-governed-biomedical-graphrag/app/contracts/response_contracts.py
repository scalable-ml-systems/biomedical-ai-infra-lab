"""Structured API response contracts.

These contracts represent the external response shape returned by the
governed biomedical GraphRAG API and displayed by the Streamlit UI.
"""

from datetime import UTC, datetime
from enum import StrEnum
from typing import Annotated, Any

from pydantic import Field

from app.contracts.governance import (
    EvidenceStrength,
    InsufficientEvidenceResult,
    RefusalResponse,
    ResponseMode,
)
from app.contracts.ontology_base import (
    BaseOntologyModel,
    ConfidenceScore,
    OntologyObject,
    OntologyObjectId,
    OntologyObjectType,
    SourceSystem,
    ValidationStatus,
)
from app.contracts.query_contracts import BlockedQueryResult, QueryClassification, QueryType

NonEmptyString = Annotated[str, Field(min_length=1)]


class ResponseStatus(StrEnum):
    """Top-level response status for API consumers."""

    SUCCEEDED = "succeeded"
    BLOCKED = "blocked"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"
    FAILED = "failed"


class GeneratedAnswer(OntologyObject):
    """Generated answer object created from an evidence bundle.

    The generated answer is not trusted by default. It must be connected
    to evidence claims, citations, validation results, safety decisions,
    and an audit record.
    """

    object_type: OntologyObjectType = OntologyObjectType.GENERATED_ANSWER
    source_system: SourceSystem = SourceSystem.EXTERNAL_LLM

    answer_text: NonEmptyString

    query_id: NonEmptyString
    evidence_bundle_object_id: OntologyObjectId | None = None
    evidence_contract_object_id: OntologyObjectId | None = None

    claim_object_ids: list[OntologyObjectId] = Field(default_factory=list)
    citation_ids: list[str] = Field(default_factory=list)
    graph_path_ids: list[str] = Field(default_factory=list)

    validation_result_object_ids: list[OntologyObjectId] = Field(default_factory=list)
    safety_decision_object_id: OntologyObjectId | None = None

    response_mode: ResponseMode = ResponseMode.ANSWER_WITH_EVIDENCE
    evidence_strength: EvidenceStrength = EvidenceStrength.INSUFFICIENT
    validation_status: ValidationStatus = ValidationStatus.NOT_CHECKED

    llm_provider: str | None = None
    llm_model: str | None = None
    generation_prompt_id: str | None = None

    confidence: ConfidenceScore | None = None
    limitations: list[str] = Field(default_factory=list)

    generated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    generation_metadata: dict[str, Any] = Field(default_factory=dict)


class StructuredQueryResponse(BaseOntologyModel):
    """Successful or partially successful governed query response.

    This is the main response shape for POST /query when the system is
    allowed to return an evidence-grounded answer.
    """

    response_id: NonEmptyString
    response_status: ResponseStatus = ResponseStatus.SUCCEEDED
    response_mode: ResponseMode = ResponseMode.ANSWER_WITH_EVIDENCE

    query_id: NonEmptyString
    original_query: NonEmptyString
    query_type: QueryType

    classification: QueryClassification | None = None

    generated_answer: GeneratedAnswer | None = None
    answer_text: str | None = None

    evidence_bundle_object_id: OntologyObjectId | None = None
    evidence_contract_object_id: OntologyObjectId | None = None

    claim_object_ids: list[OntologyObjectId] = Field(default_factory=list)
    citation_ids: list[str] = Field(default_factory=list)
    graph_path_ids: list[str] = Field(default_factory=list)

    validation_result_object_ids: list[OntologyObjectId] = Field(default_factory=list)
    safety_decision_object_id: OntologyObjectId | None = None

    audit_record_object_id: OntologyObjectId | None = None
    audit_id: str | None = None

    evidence_strength: EvidenceStrength = EvidenceStrength.INSUFFICIENT
    validation_status: ValidationStatus = ValidationStatus.NOT_CHECKED

    warnings: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)

    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    response_metadata: dict[str, Any] = Field(default_factory=dict)


class BlockedQueryResponse(BaseOntologyModel):
    """Response returned when a query is blocked by safety policy."""

    response_id: NonEmptyString
    response_status: ResponseStatus = ResponseStatus.BLOCKED
    response_mode: ResponseMode = ResponseMode.SAFE_REFUSAL

    query_id: NonEmptyString
    original_query: NonEmptyString
    query_type: QueryType

    blocked_result: BlockedQueryResult | None = None
    refusal_response: RefusalResponse | None = None

    message: NonEmptyString
    safe_redirect: str | None = None

    safety_decision_object_id: OntologyObjectId | None = None
    refusal_response_object_id: OntologyObjectId | None = None

    audit_record_object_id: OntologyObjectId | None = None
    audit_id: str | None = None

    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    response_metadata: dict[str, Any] = Field(default_factory=dict)


class InsufficientEvidenceResponse(BaseOntologyModel):
    """Response returned when retrieval did not produce enough support."""

    response_id: NonEmptyString
    response_status: ResponseStatus = ResponseStatus.INSUFFICIENT_EVIDENCE
    response_mode: ResponseMode = ResponseMode.INSUFFICIENT_EVIDENCE

    query_id: NonEmptyString
    original_query: NonEmptyString
    query_type: QueryType

    insufficient_evidence_result: InsufficientEvidenceResult

    message: NonEmptyString
    missing_evidence_types: list[str] = Field(default_factory=list)
    retrieved_source_object_ids: list[OntologyObjectId] = Field(default_factory=list)

    evidence_bundle_object_id: OntologyObjectId | None = None
    audit_record_object_id: OntologyObjectId | None = None
    audit_id: str | None = None

    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    response_metadata: dict[str, Any] = Field(default_factory=dict)


class ErrorResponse(BaseOntologyModel):
    """Response returned when the system fails unexpectedly."""

    response_id: NonEmptyString
    response_status: ResponseStatus = ResponseStatus.FAILED
    response_mode: ResponseMode = ResponseMode.ERROR

    error_type: NonEmptyString
    message: NonEmptyString

    query_id: str | None = None
    original_query: str | None = None

    recoverable: bool = True
    details: dict[str, Any] = Field(default_factory=dict)

    audit_record_object_id: OntologyObjectId | None = None
    audit_id: str | None = None

    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
