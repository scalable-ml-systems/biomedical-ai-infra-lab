from app.contracts.evidence_sources import (
    Citation,
    DailyMedSection,
    PubMedArticle,
    SourceChunk,
)
from app.contracts.ontology_base import (
    OntologyObjectType,
    SourceSystem,
    ValidationStatus,
    build_ontology_object_id,
)


def test_dailymed_section_contract_instantiates() -> None:
    parent_label_id = build_ontology_object_id(
        OntologyObjectType.DAILYMED_LABEL,
        SourceSystem.DAILYMED,
        "warfarin-label-demo",
    )

    section = DailyMedSection(
        object_id=build_ontology_object_id(
            OntologyObjectType.DAILYMED_SECTION,
            SourceSystem.DAILYMED,
            "warfarin-label-demo-warnings",
        ),
        source_object_id="warfarin-label-demo-warnings",
        parent_label_object_id=parent_label_id,
        dailymed_set_id="warfarin-label-demo",
        drug_name="warfarin",
        section_name="warnings and precautions",
        section_text="Placeholder public label warning text.",
    )

    assert section.object_type == OntologyObjectType.DAILYMED_SECTION
    assert section.source_system == SourceSystem.DAILYMED
    assert section.drug_name == "warfarin"


def test_pubmed_article_contract_instantiates() -> None:
    article = PubMedArticle(
        object_id=build_ontology_object_id(
            OntologyObjectType.PUBMED_ARTICLE,
            SourceSystem.PUBMED,
            "12345678",
        ),
        source_object_id="12345678",
        pmid="12345678",
        title="Demo PubMed Article About Warfarin",
        abstract="Placeholder PubMed abstract text.",
        journal="Demo Journal",
        publication_year=2024,
        mesh_terms=["Warfarin", "Hemorrhage"],
    )

    assert article.object_type == OntologyObjectType.PUBMED_ARTICLE
    assert article.source_system == SourceSystem.PUBMED
    assert article.pmid == "12345678"


def test_source_chunk_preserves_parent_lineage() -> None:
    parent_source_id = build_ontology_object_id(
        OntologyObjectType.DAILYMED_SECTION,
        SourceSystem.DAILYMED,
        "warfarin-label-demo-warnings",
    )

    chunk = SourceChunk(
        object_id=build_ontology_object_id(
            OntologyObjectType.SOURCE_CHUNK,
            SourceSystem.LOCAL_CACHE,
            "warfarin-warning-chunk-0",
        ),
        source_system=SourceSystem.LOCAL_CACHE,
        source_object_id="warfarin-warning-chunk-0",
        parent_source_object_id=parent_source_id,
        chunk_index=0,
        chunk_text="Placeholder chunk text from a public label section.",
        section_name="warnings and precautions",
        retrieval_score=0.87,
    )

    assert chunk.parent_source_object_id == parent_source_id
    assert chunk.chunk_index == 0


def test_citation_contract_instantiates() -> None:
    source_id = build_ontology_object_id(
        OntologyObjectType.DAILYMED_SECTION,
        SourceSystem.DAILYMED,
        "warfarin-label-demo-warnings",
    )

    citation = Citation(
        citation_id="citation-001",
        source_object_id=source_id,
        source_system=SourceSystem.DAILYMED,
        source_title="Warfarin Sodium Label",
        source_type=OntologyObjectType.DAILYMED_SECTION,
        section_name="warnings and precautions",
        quoted_text="Placeholder quoted evidence text.",
        confidence=0.95,
        validation_status=ValidationStatus.SUPPORTED,
    )

    assert citation.citation_id == "citation-001"
    assert citation.source_system == SourceSystem.DAILYMED
    assert citation.validation_status == ValidationStatus.SUPPORTED
