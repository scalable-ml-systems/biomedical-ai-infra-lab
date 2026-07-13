"""Biomedical domain entity contracts.

These contracts represent biomedical ontology objects such as drugs,
ingredients, risks, populations, and label section concepts.
"""

from typing import Annotated

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


class BiomedicalEntity(OntologyObject):
    """Base contract for biomedical domain objects.

    Biomedical entities are real domain concepts, not source documents.
    Examples include drugs, ingredients, risks, populations, and concepts.
    """

    display_name: NonEmptyString
    normalized_name: NonEmptyString | None = None
    synonyms: list[str] = Field(default_factory=list)
    description: str | None = None


class Drug(BiomedicalEntity):
    """Normalized drug concept.

    In the MVP, drug identity should be anchored by RxNorm when available.
    """

    object_type: OntologyObjectType = OntologyObjectType.DRUG
    source_system: SourceSystem = SourceSystem.RXNORM

    rxnorm_concept_id: SourceObjectId | None = None
    generic_name: str | None = None
    brand_names: list[str] = Field(default_factory=list)
    ingredient_names: list[str] = Field(default_factory=list)
    drug_class_names: list[str] = Field(default_factory=list)


class Ingredient(BiomedicalEntity):
    """Active ingredient or normalized ingredient concept."""

    object_type: OntologyObjectType = OntologyObjectType.INGREDIENT
    source_system: SourceSystem = SourceSystem.RXNORM

    rxnorm_concept_id: SourceObjectId | None = None


class BrandName(BiomedicalEntity):
    """Brand name associated with a normalized drug concept."""

    object_type: OntologyObjectType = OntologyObjectType.BRAND_NAME
    source_system: SourceSystem = SourceSystem.RXNORM

    rxnorm_concept_id: SourceObjectId | None = None
    generic_name: str | None = None


class DrugClass(BiomedicalEntity):
    """Drug class or therapeutic category."""

    object_type: OntologyObjectType = OntologyObjectType.DRUG_CLASS

    class_system: str | None = None


class RiskConcept(BiomedicalEntity):
    """Risk, warning, adverse effect, or safety concept.

    Examples:
    - bleeding risk
    - liver injury
    - hypoglycemia
    - renal impairment
    """

    object_type: OntologyObjectType = OntologyObjectType.RISK_CONCEPT

    risk_category: str | None = None
    severity_hint: str | None = None


class ClinicalConcept(BiomedicalEntity):
    """General biomedical or clinical concept.

    This is intentionally broad and should be used when a more specific
    entity type does not yet exist.
    """

    object_type: OntologyObjectType = OntologyObjectType.CLINICAL_CONCEPT

    concept_category: str | None = None


class Population(BiomedicalEntity):
    """Population or patient group mentioned in public evidence.

    Examples:
    - pregnancy
    - pediatric patients
    - geriatric patients
    - renal impairment
    """

    object_type: OntologyObjectType = OntologyObjectType.POPULATION

    population_category: str | None = None


class LabelSectionConcept(BiomedicalEntity):
    """Concept representing a drug-label section type.

    This is a domain concept such as 'warnings and precautions'.
    It is different from a retrieved DailyMedSection evidence object.
    """

    object_type: OntologyObjectType = OntologyObjectType.LABEL_SECTION

    section_code: str | None = None
    section_title: NonEmptyString


class ExtractedBiomedicalEntity(BaseOntologyModel):
    """Entity mention extracted from a user query before normalization.

    This object captures what was found in the query before it is mapped
    to a normalized ontology object such as Drug or RiskConcept.
    """

    raw_text: NonEmptyString
    entity_type: OntologyObjectType
    start_char: int | None = Field(default=None, ge=0)
    end_char: int | None = Field(default=None, ge=0)
    confidence: ConfidenceScore | None = None
    normalized_object_id: OntologyObjectId | None = None
    validation_status: ValidationStatus = ValidationStatus.NOT_CHECKED
