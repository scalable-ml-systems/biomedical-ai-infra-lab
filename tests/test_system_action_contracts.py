from datetime import UTC, datetime

from app.contracts.ontology_base import (
    ActionStatus,
    OntologyObjectType,
    SourceSystem,
    build_ontology_object_id,
)
from app.contracts.system_actions import (
    ActionError,
    EvidenceRetrievalAction,
    QueryClassificationAction,
    SystemActionType,
)


def test_query_classification_action_contract_instantiates() -> None:
    action = QueryClassificationAction(
        object_id=build_ontology_object_id(
            OntologyObjectType.SYSTEM_ACTION,
            SourceSystem.SYSTEM,
            "query-classification-001",
        ),
        source_object_id="query-classification-001",
        status=ActionStatus.SUCCEEDED,
        query_text="What does the official label say about warnings for warfarin?",
        classified_query_type="warning_question",
        classification_reason="The query asks for public label warning evidence.",
        confidence=0.97,
        completed_at=datetime.now(UTC),
    )

    assert action.action_type == SystemActionType.QUERY_CLASSIFICATION
    assert action.status == ActionStatus.SUCCEEDED
    assert action.duration_ms is not None


def test_failed_evidence_retrieval_action_contract_instantiates() -> None:
    action = EvidenceRetrievalAction(
        object_id=build_ontology_object_id(
            OntologyObjectType.SYSTEM_ACTION,
            SourceSystem.SYSTEM,
            "pubmed-retrieval-failed-001",
        ),
        source_object_id="pubmed-retrieval-failed-001",
        action_type=SystemActionType.PUBMED_RETRIEVAL,
        status=ActionStatus.FAILED,
        retrieval_query="warfarin bleeding risk",
        retrieval_source=SourceSystem.PUBMED,
        retrieved_count=0,
        error=ActionError(
            error_type="source_unavailable",
            error_message="PubMed retrieval failed in demo validation.",
            recoverable=True,
        ),
        completed_at=datetime.now(UTC),
    )

    assert action.action_type == SystemActionType.PUBMED_RETRIEVAL
    assert action.status == ActionStatus.FAILED
    assert action.error is not None
    assert action.error.recoverable is True
