"""Shared base types for ontology-aligned biomedical contracts."""

from datetime import UTC, datetime
from enum import StrEnum
from typing import Annotated, Any

from pydantic import BaseModel, ConfigDict, Field

OntologyObjectId = Annotated[str, Field(min_length=1)]
SourceObjectId = Annotated[str, Field(min_length=1)]
ConfidenceScore = Annotated[float, Field(ge=0.0, le=1.0)]


class OntologyObjectType(StrEnum):
    """High-level object categories in the biomedical ontology."""

    DRUG = "drug"
    INGREDIENT = "ingredient"
    BRAND_NAME = "brand_name"
    DRUG_CLASS = "drug_class"
    LABEL_SECTION = "label_section"
    WARNING = "warning"
    CONTRAINDICATION = "contraindication"
    ADVERSE_REACTION = "adverse_reaction"
    DRUG_INTERACTION = "drug_interaction"
    POPULATION = "population"
    RISK_CONCEPT = "risk_concept"
    CLINICAL_CONCEPT = "clinical_concept"

    DAILYMED_LABEL = "dailymed_label"
    DAILYMED_SECTION = "dailymed_section"
    PUBMED_ARTICLE = "pubmed_article"
    PUBMED_ABSTRACT = "pubmed_abstract"
    SOURCE_DOCUMENT = "source_document"
    SOURCE_CHUNK = "source_chunk"
    CITATION = "citation"

    GRAPH_NODE = "graph_node"
    GRAPH_EDGE = "graph_edge"
    GRAPH_PATH = "graph_path"

    SYSTEM_ACTION = "system_action"
    GENERATED_ANSWER = "generated_answer"
    EVIDENCE_BUNDLE = "evidence_bundle"
    EVIDENCE_CLAIM = "evidence_claim"
    EVIDENCE_CONTRACT = "evidence_contract"
    VALIDATION_RESULT = "validation_result"
    SAFETY_DECISION = "safety_decision"
    REFUSAL_RESPONSE = "refusal_response"
    AUDIT_EVENT = "audit_event"
    AUDIT_TRACE = "audit_trace"
    AUDIT_RECORD = "audit_record"


class SourceSystem(StrEnum):
    """Systems or sources that can create or support ontology objects."""

    USER = "user"
    SYSTEM = "system"
    RXNORM = "rxnorm"
    DAILYMED = "dailymed"
    PUBMED = "pubmed"
    MESH = "mesh"
    NEO4J = "neo4j"
    VECTOR_STORE = "vector_store"
    EXTERNAL_LLM = "external_llm"
    AUDIT_LOG = "audit_log"
    LOCAL_CACHE = "local_cache"


class ValidationStatus(StrEnum):
    """Shared validation state for claims, relationships, and objects."""

    NOT_CHECKED = "not_checked"
    SUPPORTED = "supported"
    PARTIALLY_SUPPORTED = "partially_supported"
    UNSUPPORTED = "unsupported"
    CONFLICTING = "conflicting"
    INVALID = "invalid"


class RelationshipType(StrEnum):
    """Ontology relationship types used by graph and evidence contracts."""

    NORMALIZED_TO = "NORMALIZED_TO"
    HAS_INGREDIENT = "HAS_INGREDIENT"
    HAS_BRAND_NAME = "HAS_BRAND_NAME"
    HAS_LABEL_SECTION = "HAS_LABEL_SECTION"
    HAS_WARNING = "HAS_WARNING"
    HAS_CONTRAINDICATION = "HAS_CONTRAINDICATION"
    HAS_ADVERSE_REACTION = "HAS_ADVERSE_REACTION"
    HAS_INTERACTION = "HAS_INTERACTION"
    HAS_POPULATION_WARNING = "HAS_POPULATION_WARNING"
    DISCUSSES = "DISCUSSES"
    SUPPORTED_BY = "SUPPORTED_BY"
    HAS_GRAPH_PATH = "HAS_GRAPH_PATH"


class ActionStatus(StrEnum):
    """Execution state for traceable system actions."""

    NOT_STARTED = "not_started"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    SKIPPED = "skipped"


class BaseOntologyModel(BaseModel):
    """Shared Pydantic configuration for all ontology contracts."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=False,
        validate_assignment=True,
    )


class OntologyObject(BaseOntologyModel):
    """Base object shape for ontology-aligned records.

    This should be inherited by domain objects, evidence objects,
    graph objects, governance objects, and audit objects when useful.
    """

    object_id: OntologyObjectId
    object_type: OntologyObjectType
    source_system: SourceSystem
    source_object_id: SourceObjectId | None = None
    confidence: ConfidenceScore | None = None
    validation_status: ValidationStatus = ValidationStatus.NOT_CHECKED
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


def build_ontology_object_id(
    object_type: OntologyObjectType,
    source_system: SourceSystem,
    source_object_id: str,
) -> str:
    """Build a stable ontology object ID from type, source, and source ID.

    Example:
        drug:rxnorm:855332
        dailymed_section:dailymed:setid-abc-warnings
        pubmed_article:pubmed:12345678
    """

    cleaned_source_object_id = source_object_id.strip().replace(" ", "_")

    return f"{object_type.value}:{source_system.value}:{cleaned_source_object_id}"
