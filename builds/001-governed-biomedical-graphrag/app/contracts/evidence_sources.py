"""Evidence source contracts for public biomedical data.

These contracts represent public biomedical evidence objects such as
DailyMed labels, DailyMed sections, PubMed articles, source chunks,
and citations.
"""

from datetime import UTC, datetime
from typing import Annotated, Any

from pydantic import Field

from app.contracts.ontology_base import (
    BaseOntologyModel,
    ConfidenceScore,
    OntologyObject,
    OntologyObjectId,
    OntologyObjectType,
    SourceObjectId,
    SourceSystem,
    ValidationStatus,
)

NonEmptyString = Annotated[str, Field(min_length=1)]


class SourceDocument(OntologyObject):
    """Base contract for a retrieved public source document.

    Examples:
    - a full DailyMed label
    - a PubMed article record
    - a locally cached source document
    """

    object_type: OntologyObjectType = OntologyObjectType.SOURCE_DOCUMENT

    title: NonEmptyString
    source_url: str | None = None
    language: str = "en"
    retrieved_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    raw_text: str | None = None
    source_metadata: dict[str, Any] = Field(default_factory=dict)


class SourceChunk(OntologyObject):
    """A smaller evidence chunk derived from a source document.

    Source chunks are used by vector retrieval and claim validation.
    They must preserve lineage back to the source document.
    """

    object_type: OntologyObjectType = OntologyObjectType.SOURCE_CHUNK

    parent_source_object_id: OntologyObjectId
    chunk_index: int = Field(ge=0)
    chunk_text: NonEmptyString
    source_url: str | None = None
    section_name: str | None = None
    start_char: int | None = Field(default=None, ge=0)
    end_char: int | None = Field(default=None, ge=0)
    token_count: int | None = Field(default=None, ge=0)
    embedding_model: str | None = None
    retrieval_score: float | None = None


class DailyMedLabel(SourceDocument):
    """DailyMed drug label document.

    This represents the label-level source object.
    Individual label sections are represented by DailyMedSection.
    """

    object_type: OntologyObjectType = OntologyObjectType.DAILYMED_LABEL
    source_system: SourceSystem = SourceSystem.DAILYMED

    dailymed_set_id: SourceObjectId
    drug_name: NonEmptyString
    label_version: str | None = None
    effective_time: str | None = None
    section_names: list[str] = Field(default_factory=list)


class DailyMedSection(OntologyObject):
    """Specific section from a DailyMed drug label.

    Examples:
    - boxed warning
    - warnings and precautions
    - contraindications
    - adverse reactions
    - drug interactions
    - use in specific populations
    """

    object_type: OntologyObjectType = OntologyObjectType.DAILYMED_SECTION
    source_system: SourceSystem = SourceSystem.DAILYMED

    parent_label_object_id: OntologyObjectId
    dailymed_set_id: SourceObjectId
    drug_name: NonEmptyString
    section_name: NonEmptyString
    section_code: str | None = None
    section_text: NonEmptyString
    source_url: str | None = None
    retrieved_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class PubMedArticle(SourceDocument):
    """PubMed article metadata and abstract-level source object."""

    object_type: OntologyObjectType = OntologyObjectType.PUBMED_ARTICLE
    source_system: SourceSystem = SourceSystem.PUBMED

    pmid: SourceObjectId
    title: NonEmptyString
    abstract: str | None = None
    journal: str | None = None
    publication_year: int | None = Field(default=None, ge=1800)
    publication_date: str | None = None
    authors: list[str] = Field(default_factory=list)
    mesh_terms: list[str] = Field(default_factory=list)
    publication_types: list[str] = Field(default_factory=list)


class PubMedAbstract(OntologyObject):
    """PubMed abstract text as a specific evidence object.

    This is separated from PubMedArticle so that the system can validate
    claims against the abstract text specifically.
    """

    object_type: OntologyObjectType = OntologyObjectType.PUBMED_ABSTRACT
    source_system: SourceSystem = SourceSystem.PUBMED

    parent_article_object_id: OntologyObjectId
    pmid: SourceObjectId
    title: NonEmptyString
    abstract_text: NonEmptyString
    source_url: str | None = None
    retrieved_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class Citation(BaseOntologyModel):
    """Citation shown to the user or attached to an evidence claim."""

    citation_id: NonEmptyString
    source_object_id: OntologyObjectId
    source_system: SourceSystem
    source_title: NonEmptyString
    source_type: OntologyObjectType
    source_url: str | None = None
    section_name: str | None = None
    quoted_text: str | None = None
    confidence: ConfidenceScore | None = None
    validation_status: ValidationStatus = ValidationStatus.NOT_CHECKED
