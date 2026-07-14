from app.contracts.governance import (
    ClaimType,
    EvidenceClaim,
    EvidenceContract,
    EvidenceStrength,
    ResponseMode,
    SafetyDecision,
    SafetyDecisionReason,
)
from app.contracts.ontology_base import (
    OntologyObjectType,
    RelationshipType,
    SourceSystem,
    ValidationStatus,
    build_ontology_object_id,
)


def test_evidence_claim_contract_instantiates() -> None:
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

    claim = EvidenceClaim(
        object_id=build_ontology_object_id(
            OntologyObjectType.EVIDENCE_CLAIM,
            SourceSystem.SYSTEM,
            "claim-warfarin-warning-001",
        ),
        source_object_id="claim-warfarin-warning-001",
        claim_text="Warfarin label evidence discusses bleeding-related warnings.",
        claim_type=ClaimType.WARNING,
        subject_object_ids=[drug_id],
        related_object_ids=[section_id],
        relationship_type=RelationshipType.HAS_WARNING,
        supporting_source_object_ids=[section_id],
        supporting_citation_ids=["citation-001"],
        supporting_graph_path_ids=["path-warfarin-bleeding-warning"],
        evidence_strength=EvidenceStrength.DIRECTLY_SUPPORTED,
        validation_status=ValidationStatus.SUPPORTED,
    )

    assert claim.claim_type == ClaimType.WARNING
    assert claim.evidence_strength == EvidenceStrength.DIRECTLY_SUPPORTED
    assert claim.validation_status == ValidationStatus.SUPPORTED


def test_safety_decision_contract_instantiates() -> None:
    decision = SafetyDecision(
        object_id=build_ontology_object_id(
            OntologyObjectType.SAFETY_DECISION,
            SourceSystem.SYSTEM,
            "safety-decision-001",
        ),
        source_object_id="safety-decision-001",
        allowed=False,
        reason=SafetyDecisionReason.PERSONAL_MEDICAL_ADVICE,
        response_mode=ResponseMode.SAFE_REFUSAL,
        checked_text="Should I take warfarin with ibuprofen?",
    )

    assert decision.allowed is False
    assert decision.reason == SafetyDecisionReason.PERSONAL_MEDICAL_ADVICE
    assert decision.response_mode == ResponseMode.SAFE_REFUSAL


def test_evidence_contract_instantiates() -> None:
    claim_id = build_ontology_object_id(
        OntologyObjectType.EVIDENCE_CLAIM,
        SourceSystem.SYSTEM,
        "claim-warfarin-warning-001",
    )

    contract = EvidenceContract(
        object_id=build_ontology_object_id(
            OntologyObjectType.EVIDENCE_CONTRACT,
            SourceSystem.SYSTEM,
            "evidence-contract-001",
        ),
        source_object_id="evidence-contract-001",
        claim_object_ids=[claim_id],
        citation_ids=["citation-001"],
        graph_path_ids=["path-warfarin-bleeding-warning"],
        contract_status=ValidationStatus.SUPPORTED,
        evidence_strength=EvidenceStrength.DIRECTLY_SUPPORTED,
    )

    assert contract.object_type == OntologyObjectType.EVIDENCE_CONTRACT
    assert contract.contract_status == ValidationStatus.SUPPORTED
    assert contract.claim_object_ids == [claim_id]
