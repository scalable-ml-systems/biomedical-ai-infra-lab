from datetime import UTC, datetime

from app.contracts.audit_contracts import (
    AuditEvent,
    AuditEventType,
    AuditRecord,
    AuditSeverity,
    AuditTrace,
)
from app.contracts.governance import ResponseMode
from app.contracts.ontology_base import (
    OntologyObjectType,
    SourceSystem,
    ValidationStatus,
    build_ontology_object_id,
)
from app.contracts.query_contracts import QueryType
from app.contracts.response_contracts import ResponseStatus


def test_audit_event_contract_instantiates() -> None:
    event = AuditEvent(
        object_id=build_ontology_object_id(
            OntologyObjectType.AUDIT_EVENT,
            SourceSystem.AUDIT_LOG,
            "audit-event-001",
        ),
        source_object_id="audit-event-001",
        trace_id="trace-001",
        event_type=AuditEventType.QUERY_RECEIVED,
        severity=AuditSeverity.INFO,
        message="Query was received by the governed biomedical GraphRAG API.",
    )

    assert event.object_type == OntologyObjectType.AUDIT_EVENT
    assert event.event_type == AuditEventType.QUERY_RECEIVED
    assert event.severity == AuditSeverity.INFO


def test_audit_trace_contract_instantiates_and_counts() -> None:
    action_id = build_ontology_object_id(
        OntologyObjectType.SYSTEM_ACTION,
        SourceSystem.SYSTEM,
        "query-classification-001",
    )

    event_id = build_ontology_object_id(
        OntologyObjectType.AUDIT_EVENT,
        SourceSystem.AUDIT_LOG,
        "audit-event-001",
    )

    trace = AuditTrace(
        object_id=build_ontology_object_id(
            OntologyObjectType.AUDIT_TRACE,
            SourceSystem.AUDIT_LOG,
            "trace-001",
        ),
        source_object_id="trace-001",
        trace_id="trace-001",
        query_id="query-001",
        action_object_ids=[action_id],
        event_object_ids=[event_id],
        completed_at=datetime.now(UTC),
        status=ResponseStatus.SUCCEEDED,
        validation_status=ValidationStatus.SUPPORTED,
    )

    assert trace.action_count == 1
    assert trace.event_count == 1
    assert trace.duration_ms is not None


def test_audit_record_contract_instantiates() -> None:
    record = AuditRecord(
        object_id=build_ontology_object_id(
            OntologyObjectType.AUDIT_RECORD,
            SourceSystem.AUDIT_LOG,
            "audit-001",
        ),
        source_object_id="audit-001",
        audit_id="audit-001",
        trace_id="trace-001",
        query_id="query-001",
        original_query="What does the official label say about warnings for warfarin?",
        query_type=QueryType.WARNING_QUESTION,
        response_status=ResponseStatus.SUCCEEDED,
        response_mode=ResponseMode.ANSWER_WITH_EVIDENCE,
        final_answer_text=(
            "Public label evidence for warfarin includes warnings related to "
            "bleeding risk. This is an educational evidence summary only."
        ),
        completed_at=datetime.now(UTC),
        validation_status=ValidationStatus.SUPPORTED,
    )

    assert record.object_type == OntologyObjectType.AUDIT_RECORD
    assert record.audit_id == "audit-001"
    assert record.response_status == ResponseStatus.SUCCEEDED
