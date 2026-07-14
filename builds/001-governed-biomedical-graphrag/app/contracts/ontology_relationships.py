"""Ontology relationship and graph path contracts.

These contracts represent typed relationships between ontology objects
before those relationships are stored or queried in Neo4j.
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
    RelationshipType,
    SourceObjectId,
    SourceSystem,
    ValidationStatus,
)

NonEmptyString = Annotated[str, Field(min_length=1)]


class OntologyRelationship(OntologyObject):
    """Typed relationship between two ontology objects.

    Example:
        Drug(warfarin) -[:HAS_WARNING]-> RiskConcept(bleeding risk)

    This contract is storage-agnostic. It can later be written to Neo4j,
    serialized into an audit record, or attached to an evidence contract.
    """

    object_type: OntologyObjectType = OntologyObjectType.GRAPH_EDGE

    relationship_type: RelationshipType

    from_object_id: OntologyObjectId
    from_object_type: OntologyObjectType

    to_object_id: OntologyObjectId
    to_object_type: OntologyObjectType

    relationship_label: NonEmptyString | None = None
    evidence_object_ids: list[OntologyObjectId] = Field(default_factory=list)

    relationship_source_system: SourceSystem | None = None
    relationship_source_object_id: SourceObjectId | None = None

    valid_from: datetime | None = None
    valid_to: datetime | None = None

    properties: dict[str, Any] = Field(default_factory=dict)


class GraphNode(BaseOntologyModel):
    """Graph node representation used in graph paths.

    This is a lightweight projection of an ontology object into a graph path.
    The full object may live elsewhere as Drug, RiskConcept, DailyMedSection,
    PubMedArticle, or another ontology object.
    """

    node_id: NonEmptyString
    object_id: OntologyObjectId
    object_type: OntologyObjectType
    display_name: NonEmptyString

    labels: list[str] = Field(default_factory=list)
    source_system: SourceSystem | None = None
    source_object_id: SourceObjectId | None = None
    properties: dict[str, Any] = Field(default_factory=dict)


class GraphEdge(BaseOntologyModel):
    """Graph edge representation used in graph paths.

    This is the graph-projection form of an OntologyRelationship.
    """

    edge_id: NonEmptyString
    relationship_type: RelationshipType

    source_node_id: NonEmptyString
    target_node_id: NonEmptyString

    source_object_id: OntologyObjectId
    target_object_id: OntologyObjectId

    relationship_object_id: OntologyObjectId | None = None
    evidence_object_ids: list[OntologyObjectId] = Field(default_factory=list)

    confidence: ConfidenceScore | None = None
    validation_status: ValidationStatus = ValidationStatus.NOT_CHECKED
    properties: dict[str, Any] = Field(default_factory=dict)


class GraphPath(BaseOntologyModel):
    """A path through ontology objects used to support a claim.

    Example:
        Drug(warfarin)
          -[:HAS_WARNING]->
        RiskConcept(bleeding risk)
          -[:SUPPORTED_BY]->
        DailyMedSection(warnings and precautions)

    A GraphPath should be attached to generated claims when graph evidence
    is used to support the answer.
    """

    graph_path_id: NonEmptyString

    start_object_id: OntologyObjectId
    end_object_id: OntologyObjectId

    nodes: list[GraphNode] = Field(default_factory=list)
    edges: list[GraphEdge] = Field(default_factory=list)

    path_summary: str | None = None
    evidence_object_ids: list[OntologyObjectId] = Field(default_factory=list)

    confidence: ConfidenceScore | None = None
    validation_status: ValidationStatus = ValidationStatus.NOT_CHECKED

    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    metadata: dict[str, Any] = Field(default_factory=dict)

    @property
    def hop_count(self) -> int:
        """Return the number of relationships in the path."""

        return len(self.edges)
