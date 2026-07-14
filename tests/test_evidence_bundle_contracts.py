from app.contracts.evidence_bundle import (
    EvidenceBundle,
    EvidenceSufficiencyStatus,
    RetrievedEvidenceSet,
)
from app.contracts.ontology_base import (
    OntologyObjectType,
    SourceSystem,
    ValidationStatus,
    build_ontology_object_id,
)


def test_retrieved_evidence_set_counts_references() -> None:
    section_id = build_ontology_object_id(
        OntologyObjectType.DAILYMED_SECTION,
        SourceSystem.DAILYMED,
        "warfarin-label-demo-warnings",
    )

    evidence_set = RetrievedEvidenceSet(
        dailymed_section_object_ids=[section_id],
        graph_path_ids=["path-warfarin-bleeding-warning"],
        citation_ids=["citation-001"],
    )

    assert evidence_set.total_evidence_count == 3


def test_evidence_bundle_contract_instantiates() -> None:
    drug_id = build_ontology_object_id(
        OntologyObjectType.DRUG,
        SourceSystem.RXNORM,
        "warfarin",
    )

    section_id = build_ontology_object_id(
        OntologyObjectType.DAILYMED_SECTION,
        SourceSystem.DAILYMED,
        "warfarin-label-demo-warnings",
    )

    bundle = EvidenceBundle(
        object_id=build_ontology_object_id(
            OntologyObjectType.EVIDENCE_BUNDLE,
            SourceSystem.SYSTEM,
            "evidence-bundle-001",
        ),
        source_object_id="evidence-bundle-001",
        query_id="query-001",
        normalized_query_id="query-001-normalized",
        original_query="What does the official label say about warnings for warfarin?",
        query_type="warning_question",
        primary_entity_object_ids=[drug_id],
        normalized_drug_object_ids=[drug_id],
        evidence_focus_terms=["warnings"],
        label_section_terms=["warnings and precautions"],
        evidence_set=RetrievedEvidenceSet(
            dailymed_section_object_ids=[section_id],
            graph_path_ids=["path-warfarin-bleeding-warning"],
            citation_ids=["citation-001"],
        ),
        sufficiency_status=EvidenceSufficiencyStatus.SUFFICIENT,
        generation_allowed=True,
        validation_status=ValidationStatus.SUPPORTED,
    )

    assert bundle.object_type == OntologyObjectType.EVIDENCE_BUNDLE
    assert bundle.sufficiency_status == EvidenceSufficiencyStatus.SUFFICIENT
    assert bundle.generation_allowed is True
