from app.contracts.ontology_base import (
    OntologyObjectType,
    RelationshipType,
    SourceSystem,
    ValidationStatus,
    build_ontology_object_id,
)
from app.contracts.ontology_relationships import GraphEdge, GraphNode, GraphPath


def test_graph_path_contract_instantiates_and_counts_hops() -> None:
    drug_id = build_ontology_object_id(
        OntologyObjectType.DRUG,
        SourceSystem.RXNORM,
        "warfarin",
    )

    risk_id = build_ontology_object_id(
        OntologyObjectType.RISK_CONCEPT,
        SourceSystem.SYSTEM,
        "bleeding_risk",
    )

    drug_node = GraphNode(
        node_id="node-warfarin",
        object_id=drug_id,
        object_type=OntologyObjectType.DRUG,
        display_name="warfarin",
        labels=["Drug"],
        source_system=SourceSystem.RXNORM,
    )

    risk_node = GraphNode(
        node_id="node-bleeding-risk",
        object_id=risk_id,
        object_type=OntologyObjectType.RISK_CONCEPT,
        display_name="bleeding risk",
        labels=["RiskConcept"],
        source_system=SourceSystem.SYSTEM,
    )

    edge = GraphEdge(
        edge_id="edge-warfarin-has-warning",
        relationship_type=RelationshipType.HAS_WARNING,
        source_node_id=drug_node.node_id,
        target_node_id=risk_node.node_id,
        source_object_id=drug_id,
        target_object_id=risk_id,
        confidence=0.95,
        validation_status=ValidationStatus.SUPPORTED,
    )

    path = GraphPath(
        graph_path_id="path-warfarin-bleeding-warning",
        start_object_id=drug_id,
        end_object_id=risk_id,
        nodes=[drug_node, risk_node],
        edges=[edge],
        validation_status=ValidationStatus.SUPPORTED,
    )

    assert path.graph_path_id == "path-warfarin-bleeding-warning"
    assert path.hop_count == 1
    assert path.validation_status == ValidationStatus.SUPPORTED
