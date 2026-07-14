"""Evidence bundle contracts for retrieved biomedical evidence.

The evidence bundle is the structured handoff between retrieval,
generation, validation, safety, and audit.
"""

from datetime import UTC, datetime
from enum import StrEnum
from typing import Annotated, Any

from pydantic import Field

from app.contracts.ontology_base import (
    BaseOntologyModel,
    ConfidenceScore,
    OntologyObject,
    OntologyObjectId,
    OntologyObjectType,
    SourceSystem,
    ValidationStatus,
)

NonEmptyString = Annotated[str, Field(min_length=1)]


class EvidenceSufficiencyStatus(StrEnum):
    """Whether retrieved evidence is strong enough to support generation."""

    NOT_ASSESSED = "not_assessed"
    SUFFICIENT = "sufficient"
    PARTIALLY_SUFFICIENT = "partially_sufficient"
    INSUFFICIENT = "insufficient"
    CONFLICTING = "conflicting"


class RetrievedEvidenceSet(BaseOntologyModel):
    """Set of retrieved evidence object IDs.

    This object stores references to evidence objects, not the full objects.
    The full objects live in the retrieval layer, cache, graph, or audit record.
    """

    dailymed_label_object_ids: list[OntologyObjectId] = Field(default_factory=list)
    dailymed_section_object_ids: list[OntologyObjectId] = Field(default_factory=list)

    pubmed_article_object_ids: list[OntologyObjectId] = Field(default_factory=list)
    pubmed_abstract_object_ids: list[OntologyObjectId] = Field(default_factory=list)

    source_chunk_object_ids: list[OntologyObjectId] = Field(default_factory=list)

    graph_path_ids: list[str] = Field(default_factory=list)
    citation_ids: list[str] = Field(default_factory=list)

    relationship_object_ids: list[OntologyObjectId] = Field(default_factory=list)

    @property
    def total_evidence_count(self) -> int:
        """Return the total number of retrieved evidence references."""

        return (
            len(self.dailymed_label_object_ids)
            + len(self.dailymed_section_object_ids)
            + len(self.pubmed_article_object_ids)
            + len(self.pubmed_abstract_object_ids)
            + len(self.source_chunk_object_ids)
            + len(self.graph_path_ids)
            + len(self.citation_ids)
            + len(self.relationship_object_ids)
        )


class EvidenceRetrievalResult(BaseOntologyModel):
    """Result of running one or more retrieval actions.

    This is produced before the final EvidenceBundle is assembled.
    """

    retrieval_result_id: NonEmptyString

    query_id: NonEmptyString
    normalized_query_id: NonEmptyString | None = None

    retrieval_action_object_ids: list[OntologyObjectId] = Field(default_factory=list)

    evidence_set: RetrievedEvidenceSet = Field(default_factory=RetrievedEvidenceSet)

    sufficiency_status: EvidenceSufficiencyStatus = EvidenceSufficiencyStatus.NOT_ASSESSED
    validation_status: ValidationStatus = ValidationStatus.NOT_CHECKED

    retrieval_warnings: list[str] = Field(default_factory=list)
    retrieval_errors: list[str] = Field(default_factory=list)

    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    retrieval_metadata: dict[str, Any] = Field(default_factory=dict)


class EvidenceBundle(OntologyObject):
    """Structured evidence package passed to answer generation.

    The EvidenceBundle is the controlled input to the LLM generation layer.
    It prevents the generator from receiving anonymous chunks without
    source lineage, graph paths, or sufficiency status.
    """

    object_type: OntologyObjectType = OntologyObjectType.EVIDENCE_BUNDLE
    source_system: SourceSystem = SourceSystem.SYSTEM

    query_id: NonEmptyString
    normalized_query_id: NonEmptyString | None = None

    original_query: NonEmptyString
    query_type: str | None = None

    primary_entity_object_ids: list[OntologyObjectId] = Field(default_factory=list)
    normalized_drug_object_ids: list[OntologyObjectId] = Field(default_factory=list)
    normalized_risk_object_ids: list[OntologyObjectId] = Field(default_factory=list)

    evidence_focus_terms: list[str] = Field(default_factory=list)
    label_section_terms: list[str] = Field(default_factory=list)

    evidence_set: RetrievedEvidenceSet = Field(default_factory=RetrievedEvidenceSet)

    retrieval_result_id: str | None = None
    retrieval_action_object_ids: list[OntologyObjectId] = Field(default_factory=list)

    sufficiency_status: EvidenceSufficiencyStatus = EvidenceSufficiencyStatus.NOT_ASSESSED
    sufficiency_reason: str | None = None

    generation_allowed: bool = False
    generation_constraints: list[str] = Field(default_factory=list)

    confidence: ConfidenceScore | None = None
    validation_status: ValidationStatus = ValidationStatus.NOT_CHECKED

    bundle_summary: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    bundle_metadata: dict[str, Any] = Field(default_factory=dict)
