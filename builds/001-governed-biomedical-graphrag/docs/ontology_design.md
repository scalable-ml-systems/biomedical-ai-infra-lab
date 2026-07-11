# Ontology Design

## Build

Build 1 — Governed Biomedical GraphRAG Pipeline with Evidence Contracts

## Public title

Medical RAG Is Broken Without Evidence Contracts

---

## 1. Why ontology matters

Biomedical data should not be treated as plain text alone.

A drug label, a PubMed abstract, a warning, a contraindication, and a generated claim are not just chunks of text.

They are different types of objects with different meanings, relationships, provenance, and safety requirements.

A generic RAG system usually thinks in this shape:

```text
documents
  → chunks
  → embeddings
  → prompt
  → answer
```

That is not enough for biomedical systems.

A governed biomedical AI system needs to think in this shape:

```text
biomedical objects
  → evidence objects
  → relationships
  → system actions
  → validation results
  → safety decisions
  → audit records
```

The purpose of the ontology is to make those objects and relationships explicit.

---

## 2. Core ontology thesis

This system treats biomedical RAG as an ontology-governed evidence workflow, not as a document search problem.

Drugs, ingredients, labels, literature, warnings, claims, validations, safety decisions, and audit records are modeled as first-class objects with governed relationships and traceable actions.

The LLM is not the system of record.

The system of record is:

```text
normalized biomedical entities
retrieved public evidence
graph relationships
evidence contracts
validation results
safety decisions
audit logs
```

---

## 3. Palantir-style thinking for this build

Palantir-style ontology thinking means the application is organized around real-world objects, their properties, their relationships, and the actions that operate on them.

For this build, the ontology is not just a graph database.

It is the operating model for the system.

The ontology should answer:

```text
What real-world object is this?
What source created or supports it?
What identifier anchors it?
What other objects is it related to?
What action produced this state?
What validation state does it have?
Can it be audited?
```

Example:

```text
Drug: warfarin

Represents:
  a normalized medication concept

Anchored by:
  RxNorm identifier

Related to:
  ingredient
  brand names
  DailyMed label sections
  warnings
  contraindications
  adverse reactions
  PubMed articles
  evidence claims

Produced or used by:
  DrugNormalizationAction
  EvidenceRetrievalAction
  GraphValidationAction

Auditable:
  yes
```

---

## 4. Five ontology layers

The Build 1 ontology has five layers:

```text
1. Domain objects
2. Evidence objects
3. Relationship objects
4. System action objects
5. Governance objects
```

These layers are implemented first as Pydantic contracts.

Later, selected objects and relationships will also be represented in Neo4j.

---

## 5. Layer 1 — Domain objects

Domain objects represent biomedical concepts.

Initial domain objects:

```text
Drug
Ingredient
BrandName
DrugClass
LabelSection
Warning
Contraindication
AdverseReaction
DrugInteraction
Population
RiskConcept
ClinicalConcept
```

Example domain objects:

```text
Drug: warfarin
Ingredient: warfarin
RiskConcept: bleeding risk
LabelSection: warnings and precautions
Population: pregnancy
```

The domain object layer prevents the system from treating all biomedical text as equivalent.

A drug is not the same kind of object as a warning.

A warning is not the same kind of object as a PubMed article.

A PubMed article is not the same kind of object as a generated claim.

---

## 6. Layer 2 — Evidence objects

Evidence objects represent public sources and source fragments.

Initial evidence objects:

```text
DailyMedLabel
DailyMedSection
PubMedArticle
PubMedAbstract
SourceDocument
SourceChunk
Citation
```

Example:

```text
DailyMedSection
  source_name: DailyMed
  drug_name: warfarin
  section_name: warnings and precautions
  section_text: ...
  source_id: ...
```

Example:

```text
PubMedArticle
  pmid: ...
  title: ...
  abstract: ...
  journal: ...
  publication_year: ...
```

Evidence objects are important because the system must know exactly where a claim came from.

---

## 7. Layer 3 — Relationship objects

Relationship objects describe how ontology objects connect.

Initial relationship types:

```text
NORMALIZED_TO
HAS_INGREDIENT
HAS_BRAND_NAME
HAS_LABEL_SECTION
HAS_WARNING
HAS_CONTRAINDICATION
HAS_ADVERSE_REACTION
HAS_INTERACTION
HAS_POPULATION_WARNING
DISCUSSES
SUPPORTED_BY
HAS_GRAPH_PATH
```

Example relationship:

```text
Drug(warfarin)
  -[:HAS_WARNING]->
Warning(bleeding risk)
```

Example evidence relationship:

```text
EvidenceClaim("Warfarin is associated with bleeding-related warnings")
  -[:SUPPORTED_BY]->
DailyMedSection("Warnings and Precautions")
```

The relationship layer is what makes this GraphRAG instead of plain vector search.

---

## 8. Layer 4 — System action objects

System action objects represent work performed by the pipeline.

Initial system actions:

```text
QueryClassificationAction
SafetyPrecheckAction
DrugExtractionAction
DrugNormalizationAction
DailyMedRetrievalAction
PubMedRetrievalAction
VectorRetrievalAction
GraphRetrievalAction
EvidenceBundleBuildAction
AnswerGenerationAction
CitationValidationAction
ClaimValidationAction
GraphConsistencyValidationAction
FinalSafetyCheckAction
AuditLoggingAction
```

Each action should eventually record:

```text
action_id
action_type
input_summary
output_summary
status
error_message
started_at
completed_at
```

This matters because a governed system should be able to explain not only the final answer, but also the operational path that produced it.

---

## 9. Layer 5 — Governance objects

Governance objects represent validation, safety, and audit state.

Initial governance objects:

```text
EvidenceClaim
EvidenceContract
ValidationResult
CitationValidationResult
ClaimValidationResult
GraphValidationResult
SafetyDecision
RefusalResponse
InsufficientEvidenceResult
AuditRecord
```

Example:

```text
SafetyDecision
  allowed: false
  reason: personal_medical_advice
  response_mode: safe_refusal
```

Example:

```text
ValidationResult
  status: supported
  supported_claim_ids: [...]
  unsupported_claim_ids: []
  warnings: []
```

This is the layer that makes the system suitable for a regulated-domain portfolio build.

---

## 10. Ontology object map

```text
BiomedicalEntity
  ├── Drug
  ├── Ingredient
  ├── BrandName
  ├── DrugClass
  ├── RiskConcept
  ├── Population
  └── ClinicalConcept

EvidenceSource
  ├── DailyMedLabel
  ├── DailyMedSection
  ├── PubMedArticle
  ├── PubMedAbstract
  └── SourceChunk

OntologyRelationship
  ├── NORMALIZED_TO
  ├── HAS_INGREDIENT
  ├── HAS_LABEL_SECTION
  ├── HAS_WARNING
  ├── HAS_CONTRAINDICATION
  ├── HAS_ADVERSE_REACTION
  ├── HAS_INTERACTION
  ├── DISCUSSES
  ├── SUPPORTED_BY
  └── HAS_GRAPH_PATH

SystemAction
  ├── QueryClassificationAction
  ├── DrugNormalizationAction
  ├── EvidenceRetrievalAction
  ├── AnswerGenerationAction
  ├── ClaimValidationAction
  ├── GraphValidationAction
  ├── SafetyPolicyAction
  └── AuditLoggingAction

GovernanceObject
  ├── EvidenceContract
  ├── EvidenceClaim
  ├── ValidationResult
  ├── SafetyDecision
  ├── RefusalResponse
  └── AuditRecord
```

---

## 11. Ontology-first data flow

```text
UserQuery
  ↓
QueryClassificationAction
  ↓
SafetyDecision
  ↓
DrugExtractionAction
  ↓
DrugNormalizationAction
  ↓
NormalizedDrug
  ↓
EvidenceRetrievalAction
  ↓
DailyMedSection + PubMedArticle + SourceChunk
  ↓
GraphRetrievalAction
  ↓
GraphPath
  ↓
EvidenceBundle
  ↓
AnswerGenerationAction
  ↓
GeneratedAnswer + EvidenceClaim[]
  ↓
ValidationResult
  ↓
FinalSafetyCheckAction
  ↓
AuditRecord
  ↓
StructuredResponse
```

---

## 12. Difference from a normal knowledge graph

A normal knowledge graph might store:

```text
Drug → has warning → Warning
Drug → has ingredient → Ingredient
Article → discusses → Drug
```

That is useful, but incomplete.

This project also models:

```text
who retrieved the evidence
what action generated the answer
which claim was supported
which claim was unsupported
which policy allowed or blocked the answer
which audit record captured the trace
```

That is why this is an ontology-governed evidence workflow, not just a knowledge graph.

---

## 13. Difference from plain RAG

Plain RAG:

```text
find chunks
send chunks to LLM
return answer
```

Ontology-governed GraphRAG:

```text
normalize entities
retrieve evidence
resolve relationships
generate structured claims
validate claims against sources
validate relationships against graph
enforce safety policy
store audit trail
return evidence trace
```

Plain RAG optimizes for answer generation.

This system optimizes for governed answer production.

---

## 14. Phase 1 implication

Phase 1 should not be called only “Core data contracts.”

Phase 1 should be treated as:

```text
Phase 1 — Ontology-Aligned Data Contracts
```

The contracts should be organized around the ontology layers:

```text
ontology_base.py
biomedical_entities.py
evidence_sources.py
ontology_relationships.py
system_actions.py
governance.py
query_contracts.py
response_contracts.py
```

This keeps the code aligned with the operating model.

---

## 15. Design rule for every object

Every major object should answer these questions:

```text
What real-world object does this represent?
What identifier anchors it?
What source supports it?
What relationships does it have?
What action produced it?
What validation state does it have?
Can it be audited?
```

If an object cannot answer these questions, it may be a temporary helper object rather than a core ontology object.

---

## 16. MVP boundary

The MVP does not need to implement the full ontology in Neo4j immediately.

The MVP should first implement the ontology as typed contracts.

Storage can evolve in stages:

```text
Stage 1: Pydantic contracts
Stage 2: local JSON/DuckDB audit records
Stage 3: Neo4j graph representation
Stage 4: graph-backed validation
Stage 5: richer ontology operations
```

This lets the project move quickly without losing architectural discipline.

---

## 17. Final ontology statement

Build 1 is an ontology-governed biomedical evidence system.

It does not treat retrieval, generation, validation, safety, and audit as separate afterthoughts.

It models them as connected objects in one operating model.

That is the foundation for safer biomedical AI infrastructure.

