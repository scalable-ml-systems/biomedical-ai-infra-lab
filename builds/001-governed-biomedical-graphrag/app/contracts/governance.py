"""Governance contracts for claims, validation, safety, and refusal behavior.

These contracts represent the evidence-governance layer of the biomedical
GraphRAG pipeline. They make generated claims, validation results, safety
decisions, refusals, and insufficient-evidence states explicit.
"""

from datetime import UTC, datetime
from enum import StrEnum
from typing import Annotated, Any

from pydantic import Field

from app.contracts.ontology_base import (
    BaseOntologyModel,
    OntologyObject,
    OntologyObjectId,
    OntologyObjectType,
    RelationshipType,
    SourceSystem,
    ValidationStatus,
)

NonEmptyString = Annotated[str, Field(min_length=1)]


class ClaimType(StrEnum):
    """Types of biomedical claims the system may generate."""

    LABEL_SUMMARY = "label_summary"
    WARNING = "warning"
    CONTRAINDICATION = "contraindication"
    ADVERSE_REACTION = "adverse_reaction"
    DRUG_INTERACTION = "drug_interaction"
    POPULATION_WARNING = "population_warning"
    LITERATURE_SUMMARY = "literature_summary"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"
    SAFETY_REFUSAL = "safety_refusal"


class EvidenceStrength(StrEnum):
    """How strongly a claim may be stated."""

    DIRECTLY_SUPPORTED = "directly_supported"
    PARTIALLY_SUPPORTED = "partially_supported"
    BACKGROUND_CONTEXT = "background_context"
    INSUFFICIENT = "insufficient"
    UNSUPPORTED = "unsupported"


class SafetyDecisionReason(StrEnum):
    """Reasons a query or generated answer may be blocked or constrained."""

    SAFE_PUBLIC_EVIDENCE_QUERY = "safe_public_evidence_query"
    PERSONAL_MEDICAL_ADVICE = "personal_medical_advice"
    DOSING_ADVICE = "dosing_advice"
    DIAGNOSIS_OR_TREATMENT = "diagnosis_or_treatment"
    PATIENT_SPECIFIC_INTERACTION = "patient_specific_interaction"
    EMERGENCY_MEDICAL_GUIDANCE = "emergency_medical_guidance"
    OUT_OF_SCOPE = "out_of_scope"
    UNSAFE_GENERATED_TEXT = "unsafe_generated_text"


class ResponseMode(StrEnum):
    """How the system should respond after safety and validation checks."""

    ANSWER_WITH_EVIDENCE = "answer_with_evidence"
    ANSWER_WITH_LIMITATIONS = "answer_with_limitations"
    SAFE_REFUSAL = "safe_refusal"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"
    ERROR = "error"


class EvidenceClaim(OntologyObject):
    """A generated biomedical claim that must be supported by evidence.

    Claims should not be treated as valid simply because the LLM generated
    them. Each claim should map to source evidence, graph paths, and a
    validation status.
    """

    object_type: OntologyObjectType = OntologyObjectType.EVIDENCE_CLAIM
    source_system: SourceSystem = SourceSystem.SYSTEM

    claim_text: NonEmptyString
    claim_type: ClaimType

    subject_object_ids: list[OntologyObjectId] = Field(default_factory=list)
    related_object_ids: list[OntologyObjectId] = Field(default_factory=list)

    relationship_type: RelationshipType | None = None

    supporting_source_object_ids: list[OntologyObjectId] = Field(default_factory=list)
    supporting_citation_ids: list[str] = Field(default_factory=list)
    supporting_graph_path_ids: list[str] = Field(default_factory=list)

    evidence_strength: EvidenceStrength = EvidenceStrength.INSUFFICIENT
    validation_status: ValidationStatus = ValidationStatus.NOT_CHECKED

    limitations: list[str] = Field(default_factory=list)
    claim_metadata: dict[str, Any] = Field(default_factory=dict)


class ValidationResult(OntologyObject):
    """Base validation result for claims, citations, graph paths, or safety."""

    object_type: OntologyObjectType = OntologyObjectType.VALIDATION_RESULT
    source_system: SourceSystem = SourceSystem.SYSTEM

    validation_target_object_ids: list[OntologyObjectId] = Field(default_factory=list)
    status: ValidationStatus = ValidationStatus.NOT_CHECKED

    supported_object_ids: list[OntologyObjectId] = Field(default_factory=list)
    partially_supported_object_ids: list[OntologyObjectId] = Field(default_factory=list)
    unsupported_object_ids: list[OntologyObjectId] = Field(default_factory=list)
    conflicting_object_ids: list[OntologyObjectId] = Field(default_factory=list)

    explanation: str | None = None
    warnings: list[str] = Field(default_factory=list)
    validation_metadata: dict[str, Any] = Field(default_factory=dict)

    checked_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class CitationValidationResult(ValidationResult):
    """Validation result for claim-to-citation support."""

    checked_citation_ids: list[str] = Field(default_factory=list)
    missing_citation_claim_ids: list[OntologyObjectId] = Field(default_factory=list)
    citation_mismatch_claim_ids: list[OntologyObjectId] = Field(default_factory=list)


class ClaimValidationResult(ValidationResult):
    """Validation result for generated biomedical claims."""

    checked_claim_ids: list[OntologyObjectId] = Field(default_factory=list)
    unsupported_claim_reasons: dict[str, str] = Field(default_factory=dict)


class GraphValidationResult(ValidationResult):
    """Validation result for graph relationship and graph path support."""

    checked_graph_path_ids: list[str] = Field(default_factory=list)
    missing_graph_path_claim_ids: list[OntologyObjectId] = Field(default_factory=list)
    invalid_relationship_claim_ids: list[OntologyObjectId] = Field(default_factory=list)


class SafetyDecision(OntologyObject):
    """Safety decision for a user query or generated answer.

    Safety runs before retrieval and after generation.
    """

    object_type: OntologyObjectType = OntologyObjectType.SAFETY_DECISION
    source_system: SourceSystem = SourceSystem.SYSTEM

    allowed: bool
    reason: SafetyDecisionReason
    response_mode: ResponseMode

    user_visible_message: str | None = None
    blocked_terms: list[str] = Field(default_factory=list)
    policy_notes: list[str] = Field(default_factory=list)

    checked_text: str | None = None
    checked_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class RefusalResponse(OntologyObject):
    """Safe refusal response for personal medical-advice requests."""

    object_type: OntologyObjectType = OntologyObjectType.REFUSAL_RESPONSE
    source_system: SourceSystem = SourceSystem.SYSTEM

    refusal_reason: SafetyDecisionReason
    response_mode: ResponseMode = ResponseMode.SAFE_REFUSAL

    message: NonEmptyString
    safe_redirect: str | None = None

    safety_decision_object_id: OntologyObjectId | None = None


class InsufficientEvidenceResult(BaseOntologyModel):
    """Result returned when evidence is not strong enough to answer safely.

    This does not inherit from OntologyObject yet because Step 1.2 did not
    define a dedicated OntologyObjectType for insufficient-evidence results.
    It can still be attached to responses and audit records.
    """

    result_id: NonEmptyString
    response_mode: ResponseMode = ResponseMode.INSUFFICIENT_EVIDENCE

    reason: NonEmptyString
    missing_evidence_types: list[str] = Field(default_factory=list)
    retrieved_source_object_ids: list[OntologyObjectId] = Field(default_factory=list)

    user_visible_message: NonEmptyString
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class EvidenceContract(OntologyObject):
    """Contract connecting answer claims to evidence, validation, and safety.

    This is the central governance object of the build.
    """

    object_type: OntologyObjectType = OntologyObjectType.EVIDENCE_CONTRACT
    source_system: SourceSystem = SourceSystem.SYSTEM

    query_object_id: OntologyObjectId | None = None
    generated_answer_object_id: OntologyObjectId | None = None

    claim_object_ids: list[OntologyObjectId] = Field(default_factory=list)
    citation_ids: list[str] = Field(default_factory=list)
    graph_path_ids: list[str] = Field(default_factory=list)

    validation_result_object_ids: list[OntologyObjectId] = Field(default_factory=list)
    safety_decision_object_id: OntologyObjectId | None = None

    contract_status: ValidationStatus = ValidationStatus.NOT_CHECKED
    evidence_strength: EvidenceStrength = EvidenceStrength.INSUFFICIENT

    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    contract_metadata: dict[str, Any] = Field(default_factory=dict)
