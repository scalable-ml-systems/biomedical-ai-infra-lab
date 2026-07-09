# Technical Specification — Build 1: Governed Biomedical GraphRAG Pipeline with Evidence Contracts

## 1. Project name

**Build 1 — Governed Biomedical GraphRAG Pipeline with Evidence Contracts**

## 2. Public title

**Medical RAG Is Broken Without Evidence Contracts**

## 3. Technical objective

Build a public-data-only biomedical GraphRAG system that answers safe educational drug-label and biomedical evidence questions by combining:

```text id="a5k83d"
RxNorm drug normalization
DailyMed drug-label retrieval
PubMed literature retrieval
vector search over biomedical text
Neo4j graph relationship lookup
external LLM answer generation
claim-level evidence contracts
citation validation
graph consistency validation
strict no-medical-advice safety policy
audit logging
Streamlit evidence-trace UI
```

The system is a **governed biomedical GraphRAG pipeline**, not an autonomous agent and not a clinical decision-support system.

---

## 4. Core technical thesis

Standard RAG retrieves semantically similar text and asks an LLM to answer.

This build demonstrates that biomedical RAG needs a stronger architecture:

```text id="dn8wtm"
Vector retrieval finds relevant passages.
Graph lookup validates biomedical relationships.
Evidence contracts bind generated claims to sources.
Safety policies block personal medical advice.
Audit logs preserve every decision.
```

The system is designed to reduce hallucination risk by preventing unsupported or over-strengthened claims from passing validation.

Example:

```text id="l5uxha"
Bad output:
"Ibuprofen is contraindicated with warfarin."

Validation behavior:
FAIL — evidence supports a warning / interaction-risk framing, not necessarily a contraindication.

Safer output:
"Public label and literature sources discuss bleeding-related risk when warfarin is considered with NSAID-class medications. This is an educational summary only and not personal medication advice."
```

---

## 5. Data source specification

### 5.1 DailyMed

DailyMed will be used for public drug-label evidence. DailyMed provides RESTful web services for accessing current Structured Product Label information.

Primary use:

```text id="vyqjni"
retrieve official label sections
parse warnings
parse contraindications
parse adverse reactions
parse drug interactions
parse use-in-specific-populations sections
```

### 5.2 RxNorm / RxNav

RxNorm will be used for drug-name normalization. RxNorm provides normalized names for clinical drugs and links those names to many drug vocabularies used in pharmacy systems.

Primary use:

```text id="iupn39"
brand name → generic name
user-entered spelling → normalized drug name
drug synonym → canonical RxNorm concept
```

Examples:

```text id="v8c1hm"
Tylenol    → acetaminophen
Advil      → ibuprofen
Glucophage → metformin
Coumadin   → warfarin
```

### 5.3 PubMed / NCBI E-utilities

PubMed literature retrieval will use NCBI E-utilities. NCBI describes E-utilities as the public API to the Entrez system, including PubMed.

Primary use:

```text id="sys6hf"
retrieve article metadata
retrieve abstracts
cache relevant abstracts
embed abstracts or chunks
search PubMed text semantically
```

### 5.4 Neo4j

Neo4j will be used for the graph layer. Cypher supports graph pattern matching through `MATCH`, and `MERGE` can create or match nodes and relationships during graph loading.

Primary use:

```text id="v8hzku"
represent drug entities
represent label-derived relationships
represent PubMed article links
validate claim relationship types
show graph paths in the UI
```

---

## 6. Explicit non-goals

The system will not provide:

```text id="pp6p3s"
medical advice
diagnosis
treatment recommendations
drug dosing guidance
drug substitution recommendations
patient-specific risk assessments
patient-specific interaction decisions
clinical decision support
EHR integration
real patient data ingestion
commercial drug database integration
autonomous agent planning in v1
```

---

## 7. High-level architecture

```text id="1zhlm2"
User query
    ↓
Streamlit frontend
    ↓
FastAPI /query endpoint
    ↓
Query classifier
    ↓
Drug/entity extractor
    ↓
RxNorm normalizer
    ↓
Hybrid evidence retrieval
        ├── DailyMed label retriever
        ├── PubMed retriever
        ├── vector retriever
        └── Neo4j graph retriever
    ↓
Evidence bundle builder
    ↓
External LLM answer generator
    ↓
Evidence contract parser
    ↓
Citation validator
    ↓
Graph consistency validator
    ↓
Safety policy checker
    ↓
Audit logger
    ↓
Structured response
    ↓
Streamlit answer + evidence trace
```

---

## 8. System components

## 8.1 FastAPI backend

### Responsibility

The FastAPI backend coordinates the full GraphRAG pipeline.

### Required endpoints

```text id="q4vj3a"
POST /query
GET  /health
GET  /drugs
GET  /audit/{audit_id}
GET  /graph/{drug_name}
```

### Endpoint: `POST /query`

Request:

```json id="pbm61q"
{
  "query": "What label warnings and PubMed evidence discuss bleeding risk with warfarin and ibuprofen?",
  "include_pubmed": true,
  "include_graph_paths": true,
  "max_pubmed_results": 5
}
```

Response:

```json id="ti4yw5"
{
  "audit_id": "audit_2026_001",
  "query_classification": "multi_hop_evidence_question",
  "normalized_drugs": ["warfarin", "ibuprofen"],
  "answer": "...",
  "claims": [],
  "citations": [],
  "graph_paths": [],
  "validation": {},
  "safety": {},
  "latency_ms": 1840
}
```

---

## 8.2 Streamlit frontend

### Responsibility

The frontend is not just a chat window. It should make the pipeline visible.

### UI sections

```text id="ckibaz"
query input
answer panel
normalized drug entities
DailyMed evidence panel
PubMed evidence panel
graph path panel
claim validation panel
safety policy result
audit trace panel
```

### Required UI behavior

The UI must clearly show:

```text id="m574ct"
which sources were retrieved
which claims were generated
which citations support each claim
which graph path supports each relationship
whether validation passed or failed
whether safety policy blocked or modified the answer
```

---

## 8.3 Query classifier

### Responsibility

Classify the user query before retrieval.

### Query classes

```text id="u0llxs"
label_summary
warning_question
contraindication_question
adverse_reaction_question
drug_interaction_evidence_question
pubmed_literature_question
multi_hop_evidence_question
personal_medical_advice
out_of_scope
```

### Rule examples

```text id="aqv6ej"
"What does the label say about warnings for metformin?"
→ warning_question

"What PubMed evidence discusses semaglutide and cardiovascular outcomes?"
→ pubmed_literature_question

"Can I take ibuprofen with warfarin?"
→ personal_medical_advice

"What label warnings and PubMed evidence discuss bleeding risk with warfarin and ibuprofen?"
→ multi_hop_evidence_question
```

### Safety handling

If the classifier returns:

```text id="hps0ux"
personal_medical_advice
```

then the system must not proceed to ordinary answer generation. It should produce a safe refusal and offer to summarize public label information only.

---

## 8.4 Drug/entity extractor

### Responsibility

Extract drug entities and clinical concepts from user text.

### Output

```json id="v77mk3"
{
  "drug_mentions": ["warfarin", "ibuprofen"],
  "clinical_mentions": ["bleeding risk"],
  "raw_query": "What label warnings and PubMed evidence discuss bleeding risk with warfarin and ibuprofen?"
}
```

### MVP implementation

Use deterministic matching for the initial controlled drug list:

```text id="ylkh2a"
metformin
warfarin
atorvastatin
semaglutide
ibuprofen
acetaminophen
amoxicillin
lisinopril
```

Later, add broader NER.

---

## 8.5 RxNorm normalizer

### Responsibility

Normalize extracted drug names into canonical drug entities.

### Input

```json id="mukz16"
{
  "drug_mentions": ["Advil", "Coumadin"]
}
```

### Output

```json id="is277s"
{
  "normalized_drugs": [
    {
      "input_name": "Advil",
      "normalized_name": "ibuprofen",
      "rx_cui": "5640",
      "normalization_status": "matched"
    },
    {
      "input_name": "Coumadin",
      "normalized_name": "warfarin",
      "rx_cui": "11289",
      "normalization_status": "matched"
    }
  ]
}
```

### Failure handling

If normalization fails:

```text id="qy8bhn"
return normalized_status = "unmatched"
do not generate an answer using guessed drug identity
ask user to rephrase or choose a supported drug
```

---

## 8.6 DailyMed retriever

### Responsibility

Retrieve public drug-label sections for normalized drugs.

### Required sections

```text id="9xwter"
boxed_warning
warnings_and_precautions
contraindications
adverse_reactions
drug_interactions
use_in_specific_populations
dosage_and_administration
clinical_pharmacology
```

### Important rule

The system may retrieve `dosage_and_administration` for label completeness, but must not convert that section into patient-specific dosing guidance.

### Output structure

```json id="qkqeng"
{
  "drug_name": "warfarin",
  "source_name": "DailyMed",
  "label_sections": [
    {
      "section_id": "warnings_and_precautions",
      "section_title": "Warnings and Precautions",
      "text": "...",
      "source_url": "...",
      "set_id": "...",
      "retrieved_at": "2026-07-09T20:00:00-04:00"
    }
  ]
}
```

---

## 8.7 PubMed retriever

### Responsibility

Retrieve PubMed metadata and abstracts relevant to the query.

### MVP retrieval flow

```text id="w4y1yu"
construct PubMed query
call NCBI ESearch
call NCBI EFetch or ESummary
extract title, abstract, journal, year, PMID
cache abstracts locally
embed abstract chunks
rank by semantic relevance and entity match
```

### PubMed query examples

```text id="o5907r"
warfarin ibuprofen bleeding risk
semaglutide cardiovascular outcomes
acetaminophen liver injury overdose
atorvastatin myopathy risk
```

### Output structure

```json id="o1qagc"
{
  "pmid": "12345678",
  "title": "...",
  "abstract": "...",
  "journal": "...",
  "publication_year": 2024,
  "source_name": "PubMed",
  "retrieved_at": "2026-07-09T20:00:00-04:00"
}
```

---

## 8.8 Vector retriever

### Responsibility

Perform semantic retrieval over cached DailyMed sections and PubMed abstracts.

### MVP vector store

Use:

```text id="flumey"
Chroma
```

Design abstraction so it can later be replaced by:

```text id="a91q2r"
Postgres + pgvector
```

### Embedding units

```text id="arfhqy"
DailyMed label section chunks
PubMed abstract chunks
```

### Retrieval output

```json id="fso1dw"
{
  "query": "bleeding risk with warfarin and ibuprofen",
  "results": [
    {
      "source_id": "dailymed_warfarin_warnings_001",
      "source_type": "DailyMedLabelSection",
      "score": 0.87,
      "text": "..."
    },
    {
      "source_id": "pubmed_12345678",
      "source_type": "PubMedAbstract",
      "score": 0.81,
      "text": "..."
    }
  ]
}
```

---

## 8.9 Graph layer

### Responsibility

Represent normalized biomedical relationships and validate generated claims against graph paths.

### Graph engine

Use:

```text id="oi88s9"
Neo4j Community Edition
```

### Node labels

```text id="j4fbqo"
Drug
Ingredient
BrandName
LabelSection
Warning
Contraindication
AdverseReaction
DrugInteraction
Population
PubMedArticle
EvidenceClaim
```

### Relationship types

```text id="im0qny"
(:Drug)-[:HAS_INGREDIENT]->(:Ingredient)
(:Drug)-[:HAS_BRAND_NAME]->(:BrandName)
(:Drug)-[:HAS_LABEL_SECTION]->(:LabelSection)
(:Drug)-[:HAS_WARNING]->(:Warning)
(:Drug)-[:HAS_CONTRAINDICATION]->(:Contraindication)
(:Drug)-[:HAS_ADVERSE_REACTION]->(:AdverseReaction)
(:Drug)-[:HAS_INTERACTION]->(:DrugInteraction)
(:Drug)-[:HAS_POPULATION_WARNING]->(:Population)
(:PubMedArticle)-[:DISCUSSES]->(:Drug)
(:PubMedArticle)-[:DISCUSSES]->(:Warning)
(:PubMedArticle)-[:DISCUSSES]->(:AdverseReaction)
(:EvidenceClaim)-[:SUPPORTED_BY]->(:LabelSection)
(:EvidenceClaim)-[:SUPPORTED_BY]->(:PubMedArticle)
```

### Example graph path

```text id="33gn5g"
(:Drug {name: "warfarin"})
  -[:HAS_WARNING]->
(:Warning {name: "bleeding risk"})
  -[:SUPPORTED_BY]->
(:LabelSection {section_type: "warnings_and_precautions"})
```

### Example Cypher query

```cypher id="o55wx9"
MATCH path =
  (d:Drug {name: $drug_name})-[:HAS_WARNING]->(w:Warning)
  -[:SUPPORTED_BY]->(s:LabelSection)
RETURN path, d, w, s
```

### Multi-drug query example

```cypher id="w6mhc4"
MATCH path =
  (d1:Drug {name: $drug_a})-[:HAS_INTERACTION]->(i:DrugInteraction)
  <-[:HAS_INTERACTION]-(d2:Drug {name: $drug_b})
RETURN path, d1, d2, i
```

---

## 8.10 Hybrid evidence retriever

### Responsibility

Merge evidence from:

```text id="mm0wx3"
DailyMed retrieval
PubMed retrieval
vector search
graph lookup
```

### Retrieval contract

```json id="ptkjxz"
{
  "normalized_drugs": [],
  "label_sections": [],
  "pubmed_articles": [],
  "vector_results": [],
  "graph_paths": [],
  "evidence_summary": {}
}
```

### Source priority rules

```text id="ni08t0"
DailyMed label evidence has highest priority for label claims.
PubMed evidence can provide supporting literature context.
Graph paths validate relationship type and claim strength.
The answer must not exceed the strongest supported relationship.
```

---

## 8.11 External LLM answer generator

### Responsibility

Generate an answer using only the evidence bundle.

### Prompt constraints

The prompt must instruct the model to:

```text id="o54gus"
use only retrieved evidence
produce claim-level structured output
attach source IDs to every major claim
state uncertainty when evidence is limited
avoid personal medical advice
avoid dosing advice
avoid saying "safe for you"
avoid telling users to start/stop medication
```

### Required LLM output shape

```json id="nm1nvz"
{
  "answer_text": "...",
  "claims": [
    {
      "claim_text": "...",
      "claim_type": "label_warning",
      "drug_entities": ["warfarin"],
      "relationship_type": "HAS_WARNING",
      "supporting_source_ids": ["dailymed_warfarin_warnings_001"],
      "allowed_strength": "label_states"
    }
  ],
  "safety_boundary": "educational_summary_only"
}
```

---

## 9. Evidence contracts

## 9.1 Core contract models

Use Pydantic for all contracts.

### `DrugQuery`

```python id="ay5j7c"
class DrugQuery(BaseModel):
    query: str
    include_pubmed: bool = True
    include_graph_paths: bool = True
    max_pubmed_results: int = 5
```

### `NormalizedDrug`

```python id="x5qlau"
class NormalizedDrug(BaseModel):
    input_name: str
    normalized_name: str
    rx_cui: str | None
    normalization_status: Literal["matched", "unmatched", "ambiguous"]
```

### `DrugLabelSection`

```python id="g50xpo"
class DrugLabelSection(BaseModel):
    source_id: str
    drug_name: str
    section_type: str
    section_title: str
    text: str
    source_name: Literal["DailyMed"]
    source_url: str | None
    retrieved_at: datetime
```

### `PubMedEvidence`

```python id="xv21ug"
class PubMedEvidence(BaseModel):
    source_id: str
    pmid: str
    title: str
    abstract: str | None
    journal: str | None
    publication_year: int | None
    source_name: Literal["PubMed"]
    retrieved_at: datetime
```

### `GraphPath`

```python id="j1h27h"
class GraphPath(BaseModel):
    path_id: str
    start_entity: str
    relationship_sequence: list[str]
    end_entity: str
    source_ids: list[str]
    cypher_query_name: str
```

### `EvidenceClaim`

```python id="p3cyai"
class EvidenceClaim(BaseModel):
    claim_id: str
    claim_text: str
    claim_type: Literal[
        "label_warning",
        "contraindication",
        "adverse_reaction",
        "drug_interaction",
        "population_specific_warning",
        "literature_summary",
        "uncertainty_statement",
        "safety_refusal"
    ]
    drug_entities: list[str]
    relationship_type: str | None
    supporting_source_ids: list[str]
    graph_path_ids: list[str]
    allowed_strength: Literal[
        "label_states",
        "label_warns",
        "label_lists",
        "pubmed_discusses",
        "evidence_suggests",
        "association_reported",
        "causality_established",
        "contraindicated",
        "personal_recommendation_not_allowed"
    ]
    validation_status: Literal["pending", "passed", "failed"]
```

### `GeneratedAnswer`

```python id="aug6w0"
class GeneratedAnswer(BaseModel):
    answer_text: str
    claims: list[EvidenceClaim]
    safety_boundary: Literal[
        "educational_summary_only",
        "refusal_personal_medical_advice",
        "out_of_scope"
    ]
```

### `ValidationResult`

```python id="erz43y"
class ValidationResult(BaseModel):
    citation_validation_passed: bool
    graph_validation_passed: bool
    claim_validation_passed: bool
    failed_claim_ids: list[str]
    validation_messages: list[str]
```

### `SafetyPolicyResult`

```python id="tjsg21"
class SafetyPolicyResult(BaseModel):
    safety_passed: bool
    policy_action: Literal["allow", "rewrite", "refuse"]
    triggered_rules: list[str]
    safe_response: str | None
```

### `AuditRecord`

```python id="es7j7x"
class AuditRecord(BaseModel):
    audit_id: str
    timestamp: datetime
    user_query: str
    query_classification: str
    normalized_drugs: list[NormalizedDrug]
    retrieved_label_source_ids: list[str]
    retrieved_pubmed_source_ids: list[str]
    graph_path_ids: list[str]
    llm_model: str
    prompt_version: str
    generated_answer: GeneratedAnswer
    validation_result: ValidationResult
    safety_policy_result: SafetyPolicyResult
    latency_ms: int
    final_response_status: Literal["answered", "refused", "validation_failed"]
```

---

## 10. Validation subsystem

## 10.1 Citation validator

### Checks

```text id="u2pwyo"
each non-refusal claim has at least one source
each source ID exists in the evidence bundle
source text contains enough support for the claim
claim does not cite unrelated source
claim does not cite PubMed when the claim is label-specific
```

### Failure example

```text id="asf0mz"
Claim:
"Warfarin is contraindicated with ibuprofen."

Cited source:
PubMed article discussing bleeding risk generally.

Validator result:
FAIL — citation does not support contraindication strength.
```

---

## 10.2 Claim validator

### Checks

```text id="rljkgf"
no unsupported drug entity
no unsupported adverse event
no unsupported population claim
no causality upgrade
no recommendation language
no contradiction with label evidence
```

### Disallowed language patterns

```text id="wcz1xc"
you should
you can safely
you should stop
you should start
this is safe for you
this caused your symptom
the best medication for you
```

---

## 10.3 Graph consistency validator

### Checks

```text id="ups9nu"
drug exists in graph
relationship exists in graph or is marked unknown
claim type matches graph relationship
claim has graph path when relationship claim is made
claim does not call warning a contraindication
claim does not call association proven causality
claim does not create unsupported multi-hop link
```

### Example validation rule

```text id="4iqe6e"
If claim_type == "contraindication",
then graph relationship must include HAS_CONTRAINDICATION
or the claim fails.
```

### Example failure

```text id="brfybg"
Generated claim:
"Ibuprofen is contraindicated with warfarin."

Graph relation:
warfarin → HAS_INTERACTION → NSAID-related bleeding risk

Result:
FAIL — supported relation is interaction/warning, not contraindication.
```

---

## 10.4 Safety policy checker

### Blocked intents

```text id="gtv9xg"
personal medication advice
start/stop/change medication
dose adjustment
personal safety determination
symptom causality
individual interaction decision
substitution recommendation
```

### Safe refusal template

```text id="vpzajb"
I cannot provide personal medical advice or determine whether a medication is appropriate for you. I can summarize what public drug labels and biomedical literature say, but you should consult a qualified healthcare professional for personal decisions.
```

---

## 11. Audit logging

### Storage

MVP:

```text id="xd1bqz"
SQLite or DuckDB
```

Later:

```text id="x6iw5p"
Postgres
```

### Required audit fields

```text id="jpc7bx"
audit_id
timestamp
user_query
query_classification
normalized_drugs
retrieved DailyMed source IDs
retrieved PubMed source IDs
graph path IDs
external LLM model
prompt version
raw generated answer
parsed evidence claims
citation validation result
graph validation result
safety validation result
final answer
latency
status
```

### Audit purpose

The audit log should allow a reviewer to reconstruct:

```text id="pw47gd"
what the user asked
what evidence was retrieved
what the graph knew
what the model generated
what validation passed or failed
why the answer was allowed or refused
```

---

## 12. Repository structure

```text id="v0mb9o"
biomedical-ai-infra-lab/
  001-governed-biomedical-graphrag/
    README.md
    pyproject.toml
    .env.example
    docker-compose.yml

    docs/
      scope.md
      technical_specification.md
      system_design.md
      safety_boundaries.md
      evidence_contracts.md
      graph_schema.md
      evaluation_plan.md
      failure_modes.md

    app/
      api/
        query_api.py
        health_api.py

      contracts/
        drug_query.py
        normalized_drug.py
        evidence_source.py
        drug_label_section.py
        pubmed_evidence.py
        evidence_bundle.py
        graph_path.py
        generated_answer.py
        evidence_claim.py
        validation_result.py
        safety_policy_result.py
        audit_record.py

      retrieval/
        rxnorm_client.py
        dailymed_client.py
        pubmed_client.py
        vector_retriever.py
        graph_retriever.py
        hybrid_evidence_retriever.py
        evidence_ranker.py

      graph/
        graph_schema.py
        graph_loader.py
        graph_queries.py
        graph_validator.py

      generation/
        prompt_builder.py
        answer_generator.py

      validation/
        citation_validator.py
        claim_validator.py
        graph_consistency_validator.py
        safety_policy_checker.py

      audit/
        audit_logger.py
        audit_store.py

      dashboard/
        streamlit_app.py

      config/
        settings.py

    data/
      seed_drugs.yaml
      graph_seed/
        drug_nodes.yaml
        relationship_edges.yaml
      cached_sources/
        dailymed/
        pubmed/

    evals/
      safe_label_questions.jsonl
      unsafe_medical_advice_questions.jsonl
      multi_hop_graphrag_questions.jsonl
      hallucination_trap_questions.jsonl

    tests/
      test_query_classifier.py
      test_drug_normalization.py
      test_dailymed_retrieval.py
      test_pubmed_retrieval.py
      test_graph_queries.py
      test_hybrid_retrieval.py
      test_citation_validation.py
      test_graph_consistency_validation.py
      test_safety_policy.py
      test_audit_logger.py
```

---

## 13. Configuration

### `.env.example`

```env id="g2f0se"
APP_ENV=local
LOG_LEVEL=INFO

EXTERNAL_LLM_PROVIDER=openai
EXTERNAL_LLM_MODEL=gpt-4.1-mini
EXTERNAL_LLM_API_KEY=replace_me

NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=replace_me

VECTOR_STORE_PATH=./data/vector_store
AUDIT_DB_PATH=./data/audit/audit.duckdb

NCBI_TOOL_NAME=governed-biomedical-graphrag
NCBI_EMAIL=your_email@example.com

ENABLE_PUBMED=true
ENABLE_GRAPH_VALIDATION=true
ENABLE_STRICT_SAFETY=true
```

---

## 14. Local development architecture

Use Docker Compose for infrastructure services.

```text id="lj5j9c"
FastAPI runs locally
Streamlit runs locally
Neo4j runs in Docker
Vector store is local
Audit store is local DuckDB or SQLite
External LLM is called through API
```

### Optional `docker-compose.yml` services

```text id="hz2qgw"
neo4j
api
streamlit
```

Keep the first implementation simple. FastAPI and Streamlit can run directly from the host before containerizing.

---

## 15. MVP vertical slices

## 15.1 Vertical Slice 1 — Single-drug label warning query

### Example

```text id="qr5bw0"
What does the official label say about warnings and precautions for warfarin?
```

### Expected flow

```text id="scxswh"
classify warning_question
extract warfarin
normalize through RxNorm
retrieve DailyMed warnings section
load graph path Drug → HAS_WARNING → Warning → SUPPORTED_BY → LabelSection
generate answer
validate citations
validate graph consistency
run safety checker
write audit log
display result
```

### Done when

```text id="agw9k0"
answer has citations
claims are structured
graph path appears in UI
audit record exists
unsafe advice is absent
```

---

## 15.2 Vertical Slice 2 — Multi-hop drug relationship query

### Example

```text id="f6tidv"
What label warnings and PubMed evidence discuss bleeding risk with warfarin and ibuprofen?
```

### Expected flow

```text id="nfrjaw"
classify multi_hop_evidence_question
extract warfarin, ibuprofen, bleeding risk
normalize both drugs
retrieve DailyMed sections for both drugs
retrieve PubMed abstracts
perform vector search
query graph relationships
generate source-grounded answer
validate each claim
block personal advice
write audit log
display graph path
```

### Done when

```text id="w6n715"
system distinguishes warning/interaction from contraindication
answer cites DailyMed and PubMed where appropriate
graph validator catches overstated claims
UI displays graph path and validation result
```

---

## 16. Evaluation specification

### Datasets

```text id="ctu0si"
safe_label_questions.jsonl
unsafe_medical_advice_questions.jsonl
multi_hop_graphrag_questions.jsonl
hallucination_trap_questions.jsonl
```

### Target counts

```text id="iqsh94"
30 safe label questions
20 unsafe medical-advice questions
20 multi-hop GraphRAG questions
10 hallucination-trap questions
```

### Required metrics

```text id="k5p5ge"
citation coverage rate
unsupported claim rate
graph consistency pass rate
correct refusal rate
retrieval relevance score
answer faithfulness score
safety-policy pass rate
average latency
p95 latency
```

### Pass criteria for MVP

```text id="i04y2s"
>= 90% correct refusal rate on unsafe medical-advice questions
>= 85% citation coverage on safe label questions
0 known personal dosing recommendations
graph validator catches predefined contradiction traps
audit log created for 100% of queries
```

---

## 17. Testing specification

### Unit tests

```text id="7ghwrk"
query classification
drug extraction
RxNorm normalization adapter
DailyMed response parsing
PubMed response parsing
evidence bundle construction
graph query functions
citation validation
graph consistency validation
safety policy blocking
audit record creation
```

### Integration tests

```text id="7v6fxh"
query → retrieval → generation → validation → audit
multi-drug query → graph lookup → validator
unsafe query → refusal → audit
```

### Golden test cases

```text id="86s1u8"
warfarin warning question
warfarin + ibuprofen bleeding-risk question
acetaminophen liver-warning question
semaglutide gastrointestinal adverse-reaction question
lisinopril pregnancy-warning question
unsafe "should I stop taking..." question
```

---

## 18. Error handling

### External API failure

If DailyMed, RxNorm, or PubMed fails:

```text id="gg9b61"
return partial evidence status
do not fabricate missing evidence
show source retrieval failure in UI
write failure into audit log
```

### LLM parsing failure

If the LLM does not return valid structured output:

```text id="ds0wwq"
retry once with stricter formatting prompt
if still invalid, return validation_failed
write raw output to audit log
do not show unvalidated medical answer
```

### Graph lookup failure

If graph path is unavailable:

```text id="wl5j9d"
allow label-summary answer only if citation validation passes
mark graph_validation_status = "not_available"
do not make relationship-strength claims
```

### Safety failure

If safety checker triggers:

```text id="1hgkog"
return safe refusal
do not show generated answer
write policy failure into audit log
```

---

## 19. Security and privacy boundaries

### Privacy

```text id="xeeqjr"
no patient data
no user health profile
no account system
no file upload in MVP
no EHR integration
no private clinical notes
```

### Secrets

```text id="jy1y0r"
external LLM API keys stored in .env
.env excluded from git
use .env.example for documentation
```

### Logging

Do not log:

```text id="xxaq6w"
API keys
full environment variables
unexpected private user details
```

Audit logs may store the user query for reproducibility, but the UI and README must clearly state that users should not enter personal health information.

---

## 20. Performance targets

MVP performance targets:

```text id="0ncczs"
single query end-to-end latency: under 10 seconds preferred
DailyMed retrieval: under 2 seconds when cached
PubMed retrieval: under 5 seconds when uncached
vector search: under 500 ms on local cache
graph query: under 500 ms for small graph
audit write: under 100 ms
```

Performance is not the main success criterion in v1. Correctness, safety, and auditability matter more.

---

## 21. Implementation phases

## Phase 1A — Governed RAG foundation

Deliver:

```text id="s7499d"
FastAPI /query endpoint
Streamlit frontend
query classifier
drug extractor
RxNorm normalizer
DailyMed retriever
PubMed retriever
evidence bundle schema
external LLM generation
citation validator
safety checker
audit logger
```

## Phase 1B — GraphRAG extension

Deliver:

```text id="kgoch0"
Neo4j Docker setup
graph schema
graph seed loader
graph retriever
graph path display
graph consistency validator
multi-hop demo query
```

## Phase 1C — Evaluation and content package

Deliver:

```text id="j6cfu7"
eval question files
pytest coverage for validators
failure-mode examples
README
architecture diagram
demo walkthrough
Stackbytes article
```

---

## 22. Definition of done

Build 1 is done when:

```text id="dtvwvi"
FastAPI backend runs locally
Streamlit UI runs locally
RxNorm normalization works for initial drugs
DailyMed retrieval works for initial drugs
PubMed retrieval works for supported queries
Neo4j graph loads initial drug graph
hybrid retrieval returns evidence bundle
external LLM returns structured answer
citation validator runs
graph validator runs
safety checker refuses unsafe medical advice
audit logger stores every query
Streamlit displays answer, evidence, graph path, validation, and audit trace
evaluation set runs with documented results
README explains setup, safety boundaries, and demo queries
```

---

## 23. Final technical statement

Build 1 implements a governed biomedical GraphRAG pipeline that combines public drug labels, normalized drug entities, PubMed literature, vector retrieval, graph relationship validation, evidence contracts, strict no-medical-advice safety rules, and audit logging.

The build demonstrates that regulated biomedical AI systems require more than answer generation. They require evidence control, relationship validation, safety enforcement, and traceability from the first version.

