from app.contracts.ontology_base import (
    OntologyObject,
    OntologyObjectType,
    RelationshipType,
    SourceSystem,
    ValidationStatus,
    build_ontology_object_id,
)


def test_build_ontology_object_id() -> None:
    object_id = build_ontology_object_id(
        OntologyObjectType.DRUG,
        SourceSystem.RXNORM,
        "warfarin",
    )

    assert object_id == "drug:rxnorm:warfarin"


def test_base_ontology_object_instantiates() -> None:
    obj = OntologyObject(
        object_id="drug:rxnorm:warfarin",
        object_type=OntologyObjectType.DRUG,
        source_system=SourceSystem.RXNORM,
        source_object_id="warfarin",
        confidence=0.98,
        validation_status=ValidationStatus.SUPPORTED,
        metadata={"normalized_name": "warfarin"},
    )

    assert obj.object_type == OntologyObjectType.DRUG
    assert obj.source_system == SourceSystem.RXNORM
    assert obj.validation_status == ValidationStatus.SUPPORTED
    assert obj.metadata["normalized_name"] == "warfarin"


def test_relationship_type_enum_contains_graph_edges() -> None:
    assert RelationshipType.HAS_WARNING == "HAS_WARNING"
    assert RelationshipType.SUPPORTED_BY == "SUPPORTED_BY"
