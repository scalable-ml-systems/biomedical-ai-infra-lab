"""Query request, classification, and normalized query contracts.

These contracts represent the first part of the governed biomedical
GraphRAG pipeline: user input, query classification, normalized query
state, and blocked-query behavior.
"""

from datetime import UTC, datetime
from enum import StrEnum
from typing import Annotated, Any

from pydantic import Field

from app.contracts.biomedical_entities import ExtractedBiomedicalEntity
from app.contracts.governance import (
    ResponseMode,
    SafetyDecisionReason,
)
from app.contracts.ontology_base import (
    BaseOntologyModel,
    ConfidenceScore,
    OntologyObjectId,
)

NonEmptyString = Annotated[str, Field(min_length=1)]


class QueryType(StrEnum):
    """Supported query categories for the biomedical GraphRAG pipeline."""

    LABEL_SUMMARY = "label_summary"
    WARNING_QUESTION = "warning_question"
    CONTRAINDICATION_QUESTION = "contraindication_question"
    ADVERSE_REACTION_QUESTION = "adverse_reaction_question"
    DRUG_INTERACTION_EVIDENCE_QUESTION = "drug_interaction_evidence_question"
    PUBMED_LITERATURE_QUESTION = "pubmed_literature_question"
    MULTI_HOP_EVIDENCE_QUESTION = "multi_hop_evidence_question"

    PERSONAL_MEDICAL_ADVICE = "personal_medical_advice"
    DOSING_ADVICE = "dosing_advice"
    DIAGNOSIS_OR_TREATMENT = "diagnosis_or_treatment"
    PATIENT_SPECIFIC_INTERACTION = "patient_specific_interaction"
    EMERGENCY_MEDICAL_GUIDANCE = "emergency_medical_guidance"

    OUT_OF_SCOPE = "out_of_scope"
    UNKNOWN = "unknown"


class QueryRequest(BaseOntologyModel):
    """Incoming user query request.

    This is the external API-facing request shape for POST /query.
    """

    query: NonEmptyString

    client_request_id: str | None = None
    user_id_hash: str | None = None

    requested_drug_names: list[str] = Field(default_factory=list)
    requested_source_types: list[str] = Field(default_factory=list)

    include_pubmed: bool = True
    include_graph_paths: bool = True
    include_audit_trace: bool = True

    request_metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class QueryClassification(BaseOntologyModel):
    """Classification result for a user query.

    The classifier determines whether the query is safe, what kind of
    evidence path it needs, and whether it should be blocked early.
    """

    query_id: NonEmptyString | None = None
    query_text: NonEmptyString

    query_type: QueryType
    confidence: ConfidenceScore | None = None

    is_safe_evidence_query: bool
    requires_safety_refusal: bool = False

    safety_reason: SafetyDecisionReason | None = None
    response_mode: ResponseMode = ResponseMode.ANSWER_WITH_EVIDENCE

    matched_terms: list[str] = Field(default_factory=list)
    extracted_drug_terms: list[str] = Field(default_factory=list)
    extracted_risk_terms: list[str] = Field(default_factory=list)

    classification_reason: str | None = None
    classification_metadata: dict[str, Any] = Field(default_factory=dict)

    classified_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class NormalizedQuery(BaseOntologyModel):
    """Query state after extraction and normalization.

    This contract preserves the original query while adding extracted
    entities and normalized ontology object IDs.
    """

    query_id: NonEmptyString
    original_query: NonEmptyString

    query_type: QueryType
    classification: QueryClassification

    extracted_entities: list[ExtractedBiomedicalEntity] = Field(default_factory=list)

    normalized_entity_object_ids: list[OntologyObjectId] = Field(default_factory=list)
    normalized_drug_object_ids: list[OntologyObjectId] = Field(default_factory=list)
    normalized_risk_object_ids: list[OntologyObjectId] = Field(default_factory=list)
    normalized_population_object_ids: list[OntologyObjectId] = Field(default_factory=list)

    label_section_terms: list[str] = Field(default_factory=list)
    evidence_focus_terms: list[str] = Field(default_factory=list)

    safe_for_retrieval: bool = True
    retrieval_intent: str | None = None

    normalization_warnings: list[str] = Field(default_factory=list)
    normalized_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class BlockedQueryResult(BaseOntologyModel):
    """Structured result for a blocked unsafe or out-of-scope query."""

    query_id: NonEmptyString
    original_query: NonEmptyString

    query_type: QueryType
    blocked: bool = True

    safety_reason: SafetyDecisionReason
    response_mode: ResponseMode = ResponseMode.SAFE_REFUSAL

    user_visible_message: NonEmptyString
    safe_redirect: str | None = None

    matched_terms: list[str] = Field(default_factory=list)
    blocked_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    safety_decision_object_id: OntologyObjectId | None = None
    refusal_response_object_id: OntologyObjectId | None = None

    result_metadata: dict[str, Any] = Field(default_factory=dict)
