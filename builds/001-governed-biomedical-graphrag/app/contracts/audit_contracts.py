"""Audit record and audit trace contracts.

These contracts represent the flight-recorder layer of the governed
biomedical GraphRAG pipeline. They preserve the query, actions, evidence,
claims, validation results, safety decisions, response, and errors.
"""

from datetime import UTC, datetime
from enum import StrEnum
from typing import Annotated, Any

from pydantic import Field

from app.contracts.governance import ResponseMode
from app.contracts.ontology_base import (
    BaseOntologyModel,
    OntologyObject,
    OntologyObjectId,
    OntologyObjectType,
    SourceSystem,
    ValidationStatus,
)
from app.contracts.query_contracts import QueryType
from app.contracts.response_contracts import ResponseStatus

NonEmptyString = Annotated[str, Field(min_length=1)]


class AuditEventType(StrEnum):
    """Types of events that may appear in an audit trace."""

    QUERY_RECEIVED = "query_received"
    QUERY_CLASSIFIED = "query_classified"
    SAFETY_PRECHECK_COMPLETED = "safety_precheck_completed"
    ENTITY_EXTRACTION_COMPLETED = "entity_extraction_completed"
    DRUG_NORMALIZATION_COMPLETED = "drug_normalization_completed"
    EVIDENCE_RETRIEVAL_COMPLETED = "evidence_retrieval_completed"
    EVIDENCE_BUNDLE_CREATED = "evidence_bundle_created"
    ANSWER_GENERATED = "answer_generated"
    VALIDATION_COMPLETED = "validation_completed"
    FINAL_SAFETY_CHECK_COMPLETED = "final_safety_check_completed"
    RESPONSE_CREATED = "response_created"
    AUDIT_RECORD_CREATED = "audit_record_created"
    ERROR_RECORDED = "error_recorded"


class AuditSeverity(StrEnum):
    """Severity level for audit events."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AuditEvent(OntologyObject):
    """Single event in the governed query lifecycle.

    Audit events are lightweight timeline entries. They should reference
    ontology objects rather than embedding large source documents directly.
    """

    object_type: OntologyObjectType = OntologyObjectType.AUDIT_EVENT
    source_system: SourceSystem = SourceSystem.AUDIT_LOG

    trace_id: NonEmptyString
    event_type: AuditEventType
    severity: AuditSeverity = AuditSeverity.INFO

    message: NonEmptyString

    related_object_ids: list[OntologyObjectId] = Field(default_factory=list)
    related_action_object_id: OntologyObjectId | None = None

    event_time: datetime = Field(default_factory=lambda: datetime.now(UTC))
    event_metadata: dict[str, Any] = Field(default_factory=dict)


class AuditTrace(OntologyObject):
    """Ordered trace of audit events and system actions for one query."""

    object_type: OntologyObjectType = OntologyObjectType.AUDIT_TRACE
    source_system: SourceSystem = SourceSystem.AUDIT_LOG

    trace_id: NonEmptyString
    query_id: NonEmptyString

    action_object_ids: list[OntologyObjectId] = Field(default_factory=list)
    event_object_ids: list[OntologyObjectId] = Field(default_factory=list)

    started_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    completed_at: datetime | None = None

    status: ResponseStatus | None = None
    validation_status: ValidationStatus = ValidationStatus.NOT_CHECKED

    warnings: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)

    trace_metadata: dict[str, Any] = Field(default_factory=dict)

    @property
    def duration_ms(self) -> float | None:
        """Return trace duration in milliseconds when completed."""

        if self.completed_at is None:
            return None

        duration = self.completed_at - self.started_at
        return duration.total_seconds() * 1000

    @property
    def action_count(self) -> int:
        """Return the number of system actions referenced by the trace."""

        return len(self.action_object_ids)

    @property
    def event_count(self) -> int:
        """Return the number of audit events referenced by the trace."""

        return len(self.event_object_ids)


class AuditRecord(OntologyObject):
    """Final audit record for a governed biomedical query.

    This is the persisted audit object that ties together the full query
    lifecycle: request, classification, safety, normalization, retrieval,
    evidence bundle, answer, validation, response, and trace.
    """

    object_type: OntologyObjectType = OntologyObjectType.AUDIT_RECORD
    source_system: SourceSystem = SourceSystem.AUDIT_LOG

    audit_id: NonEmptyString
    trace_id: NonEmptyString

    query_id: NonEmptyString
    original_query: NonEmptyString
    query_type: QueryType | None = None

    response_status: ResponseStatus
    response_mode: ResponseMode

    query_classification_object_id: OntologyObjectId | None = None
    normalized_query_object_id: OntologyObjectId | None = None

    safety_decision_object_ids: list[OntologyObjectId] = Field(default_factory=list)

    extracted_entity_object_ids: list[OntologyObjectId] = Field(default_factory=list)
    normalized_entity_object_ids: list[OntologyObjectId] = Field(default_factory=list)

    evidence_bundle_object_id: OntologyObjectId | None = None
    evidence_contract_object_id: OntologyObjectId | None = None
    generated_answer_object_id: OntologyObjectId | None = None

    retrieved_source_object_ids: list[OntologyObjectId] = Field(default_factory=list)
    graph_path_ids: list[str] = Field(default_factory=list)
    citation_ids: list[str] = Field(default_factory=list)
    claim_object_ids: list[OntologyObjectId] = Field(default_factory=list)

    validation_result_object_ids: list[OntologyObjectId] = Field(default_factory=list)

    response_object_id: str | None = None
    final_answer_text: str | None = None
    user_visible_message: str | None = None

    action_object_ids: list[OntologyObjectId] = Field(default_factory=list)
    event_object_ids: list[OntologyObjectId] = Field(default_factory=list)

    warnings: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)

    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    completed_at: datetime | None = None

    audit_metadata: dict[str, Any] = Field(default_factory=dict)


class AuditSummary(BaseOntologyModel):
    """Small user-facing or UI-facing summary of an audit record."""

    audit_id: NonEmptyString
    query_id: NonEmptyString
    response_status: ResponseStatus
    response_mode: ResponseMode

    evidence_bundle_object_id: OntologyObjectId | None = None
    evidence_contract_object_id: OntologyObjectId | None = None

    claim_count: int = Field(default=0, ge=0)
    citation_count: int = Field(default=0, ge=0)
    graph_path_count: int = Field(default=0, ge=0)
    validation_result_count: int = Field(default=0, ge=0)

    warning_count: int = Field(default=0, ge=0)
    error_count: int = Field(default=0, ge=0)

    created_at: datetime
