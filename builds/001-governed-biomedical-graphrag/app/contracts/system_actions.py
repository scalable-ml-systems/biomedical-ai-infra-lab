"""Traceable system action contracts for pipeline execution.

These contracts represent the operational steps performed by the governed
biomedical GraphRAG pipeline. They make classification, retrieval,
generation, validation, safety, and audit steps inspectable.
"""

from datetime import UTC, datetime
from enum import StrEnum
from typing import Annotated, Any

from pydantic import Field

from app.contracts.ontology_base import (
    ActionStatus,
    BaseOntologyModel,
    ConfidenceScore,
    OntologyObject,
    OntologyObjectId,
    OntologyObjectType,
    SourceSystem,
)

NonEmptyString = Annotated[str, Field(min_length=1)]


class SystemActionType(StrEnum):
    """Types of traceable actions performed by the pipeline."""

    QUERY_CLASSIFICATION = "query_classification"
    SAFETY_PRECHECK = "safety_precheck"
    DRUG_EXTRACTION = "drug_extraction"
    DRUG_NORMALIZATION = "drug_normalization"
    DAILYMED_RETRIEVAL = "dailymed_retrieval"
    PUBMED_RETRIEVAL = "pubmed_retrieval"
    VECTOR_RETRIEVAL = "vector_retrieval"
    GRAPH_RETRIEVAL = "graph_retrieval"
    EVIDENCE_BUNDLE_BUILD = "evidence_bundle_build"
    ANSWER_GENERATION = "answer_generation"
    CITATION_VALIDATION = "citation_validation"
    CLAIM_VALIDATION = "claim_validation"
    GRAPH_CONSISTENCY_VALIDATION = "graph_consistency_validation"
    FINAL_SAFETY_CHECK = "final_safety_check"
    AUDIT_LOGGING = "audit_logging"


class ActionError(BaseOntologyModel):
    """Structured error attached to a failed or partially failed action."""

    error_type: NonEmptyString
    error_message: NonEmptyString
    recoverable: bool = True
    details: dict[str, Any] = Field(default_factory=dict)


class SystemAction(OntologyObject):
    """Base contract for a traceable pipeline action.

    Every meaningful pipeline step should create a SystemAction record.
    These records will later be stored inside AuditTrace and AuditRecord.
    """

    object_type: OntologyObjectType = OntologyObjectType.SYSTEM_ACTION
    source_system: SourceSystem = SourceSystem.SYSTEM

    action_type: SystemActionType
    status: ActionStatus = ActionStatus.NOT_STARTED

    trace_id: NonEmptyString | None = None
    parent_action_id: OntologyObjectId | None = None

    input_object_ids: list[OntologyObjectId] = Field(default_factory=list)
    output_object_ids: list[OntologyObjectId] = Field(default_factory=list)

    input_summary: str | None = None
    output_summary: str | None = None

    started_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    completed_at: datetime | None = None

    error: ActionError | None = None
    action_metadata: dict[str, Any] = Field(default_factory=dict)

    @property
    def duration_ms(self) -> float | None:
        """Return action duration in milliseconds when completed."""

        if self.completed_at is None:
            return None

        duration = self.completed_at - self.started_at
        return duration.total_seconds() * 1000


class QueryClassificationAction(SystemAction):
    """Action record for classifying a user query."""

    action_type: SystemActionType = SystemActionType.QUERY_CLASSIFICATION

    query_text: NonEmptyString
    classified_query_type: str | None = None
    classification_reason: str | None = None
    confidence: ConfidenceScore | None = None


class SafetyPrecheckAction(SystemAction):
    """Action record for early safety screening before retrieval."""

    action_type: SystemActionType = SystemActionType.SAFETY_PRECHECK

    query_text: NonEmptyString
    allowed: bool
    safety_reason: str | None = None
    response_mode: str | None = None


class DrugExtractionAction(SystemAction):
    """Action record for extracting biomedical entities from a query."""

    action_type: SystemActionType = SystemActionType.DRUG_EXTRACTION

    query_text: NonEmptyString
    extracted_entity_object_ids: list[OntologyObjectId] = Field(default_factory=list)
    extracted_entity_count: int = Field(default=0, ge=0)


class DrugNormalizationAction(SystemAction):
    """Action record for normalizing extracted drug mentions."""

    action_type: SystemActionType = SystemActionType.DRUG_NORMALIZATION

    raw_drug_text: NonEmptyString
    normalized_drug_object_id: OntologyObjectId | None = None
    normalized_name: str | None = None
    rxnorm_concept_id: str | None = None
    confidence: ConfidenceScore | None = None


class EvidenceRetrievalAction(SystemAction):
    """Action record for retrieving biomedical evidence.

    This class is shared across DailyMed, PubMed, vector, and graph retrieval.
    Use action_type to distinguish which retrieval path ran.
    """

    action_type: SystemActionType

    retrieval_query: NonEmptyString
    retrieval_source: SourceSystem
    retrieved_object_ids: list[OntologyObjectId] = Field(default_factory=list)
    retrieved_count: int = Field(default=0, ge=0)
    cache_hit: bool = False


class AnswerGenerationAction(SystemAction):
    """Action record for generating a structured answer from evidence."""

    action_type: SystemActionType = SystemActionType.ANSWER_GENERATION

    evidence_bundle_id: OntologyObjectId | None = None
    generated_answer_object_id: OntologyObjectId | None = None
    generated_claim_object_ids: list[OntologyObjectId] = Field(default_factory=list)
    llm_provider: str | None = None
    llm_model: str | None = None


class ValidationAction(SystemAction):
    """Action record for citation, claim, graph, or safety validation."""

    action_type: SystemActionType

    validation_target_object_ids: list[OntologyObjectId] = Field(default_factory=list)
    validation_result_object_id: OntologyObjectId | None = None
    validation_status: str | None = None
    unsupported_object_ids: list[OntologyObjectId] = Field(default_factory=list)


class AuditLoggingAction(SystemAction):
    """Action record for writing the final audit trace."""

    action_type: SystemActionType = SystemActionType.AUDIT_LOGGING

    audit_record_object_id: OntologyObjectId | None = None
    audit_storage_path: str | None = None
    event_count: int = Field(default=0, ge=0)
