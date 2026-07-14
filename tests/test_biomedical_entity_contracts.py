from app.contracts.biomedical_entities import (
    Drug,
    ExtractedBiomedicalEntity,
    RiskConcept,
)
from app.contracts.ontology_base import (
    OntologyObjectType,
    SourceSystem,
    ValidationStatus,
    build_ontology_object_id,
)


def test_drug_contract_instantiates() -> None:
    drug = Drug(
        object_id=build_ontology_object_id(
            OntologyObjectType.DRUG,
            SourceSystem.RXNORM,
            "warfarin",
        ),
        source_object_id="warfarin",
        display_name="warfarin",
        normalized_name="warfarin",
        rxnorm_concept_id="warfarin",
        generic_name="warfarin",
        brand_names=["Coumadin"],
        confidence=0.98,
        validation_status=ValidationStatus.SUPPORTED,
    )

    assert drug.object_type == OntologyObjectType.DRUG
    assert drug.source_system == SourceSystem.RXNORM
    assert drug.display_name == "warfarin"
    assert drug.brand_names == ["Coumadin"]


def test_risk_concept_contract_instantiates() -> None:
    risk = RiskConcept(
        object_id=build_ontology_object_id(
            OntologyObjectType.RISK_CONCEPT,
            SourceSystem.SYSTEM,
            "bleeding_risk",
        ),
        source_system=SourceSystem.SYSTEM,
        source_object_id="bleeding_risk",
        display_name="bleeding risk",
        normalized_name="bleeding risk",
        risk_category="safety_warning",
        severity_hint="high",
    )

    assert risk.object_type == OntologyObjectType.RISK_CONCEPT
    assert risk.display_name == "bleeding risk"
    assert risk.risk_category == "safety_warning"


def test_extracted_biomedical_entity_contract_instantiates() -> None:
    entity = ExtractedBiomedicalEntity(
        raw_text="Coumadin",
        entity_type=OntologyObjectType.DRUG,
        start_char=0,
        end_char=8,
        confidence=0.92,
    )

    assert entity.raw_text == "Coumadin"
    assert entity.entity_type == OntologyObjectType.DRUG
    assert entity.confidence == 0.92
