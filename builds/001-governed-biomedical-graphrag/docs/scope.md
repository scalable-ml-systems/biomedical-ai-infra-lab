# Build 1 — Governed Biomedical GraphRAG Pipeline with Evidence Contracts

**Medical RAG Is Broken Without Evidence Contracts**

## Project label

**Governed Biomedical GraphRAG Pipeline with Evidence Contracts**

---

## 1. Project purpose

This project builds a public-data-only biomedical RAG system that combines:

* vector retrieval over drug-label and PubMed text,
* graph-based validation of drug relationships,
* claim-level evidence contracts,
* strict no-medical-advice safety boundaries,
* and audit logging for every answer.

The goal is to demonstrate that biomedical RAG should not be a simple “retrieve chunks and ask an LLM” workflow. In regulated or safety-sensitive domains, the system must show what evidence was used, which claim came from which source, whether the answer stayed within scope, and whether the output can be audited later.

This is a **governed GraphRAG pipeline**, not an autonomous agent in version 1.

---

## 2. Core thesis

Generic RAG retrieves relevant text.

Biomedical GraphRAG must go further:

```text
Vector search finds relevant passages.
Graph lookup validates entities and relationships.
Evidence contracts bind generated claims to sources.
Safety policies block medical advice.
Audit logs preserve the full trace.
```

The core demonstration is:

> A biomedical RAG system becomes more trustworthy when generated claims are validated against both retrieved text and structured biomedical relationships before the answer is shown.

Important wording: this system is designed to **reduce hallucination risk**, not eliminate hallucinations completely.

---

## 3. Why this build matters

Drug labels contain regulated, clinically important information, but they are long, heterogeneous, and difficult for general LLMs to summarize safely. DailyMed provides access to current Structured Product Label information through RESTful web services, RxNorm provides normalized names for clinical drugs, and NCBI E-utilities provide public API access to PubMed and other Entrez databases.

This build shows how to turn those public biomedical sources into a governed retrieval and validation workflow.

It also aligns with the regulatory direction that AI systems used in drug and biological product contexts need a clearly defined context of use and credibility assessment. FDA’s 2025 AI guidance describes a risk-based framework for establishing AI model credibility for a specific context of use.

---

## 4. Target audience

Primary audience:

```text
AI infrastructure engineers
RAG engineers
healthtech founders
pharma AI teams
clinical informatics teams
LLM evaluation teams
regulatory-minded AI builders
```

Secondary audience:

```text
technical clinicians
pharmacists interested in AI
biomedical researchers
medical content teams
students learning biomedical AI systems
```

---

## 5. What this project demonstrates

This build demonstrates:

```text
regulated-domain RAG architecture
drug-name normalization
public biomedical data ingestion
hybrid vector + graph retrieval
claim-to-source validation
graph-based relationship checking
strict safety policy enforcement
audit logging
foundation for future bounded biomedical agents
```

The key portfolio signal is:

> I can build AI systems for regulated biomedical workflows where retrieval, validation, safety, and auditability matter as much as answer generation.

---

## 6. What this project is not

This project is not:

```text
not medical advice
not diagnosis
not treatment recommendation
not dosing guidance
not drug-interaction decision support for patients
not a replacement for pharmacists, clinicians, FDA labeling, or clinical judgment
not connected to private patient data
not using proprietary pharma data
not an autonomous medical agent
```

The system must always stay in an educational and research-support posture.

---

## 7. Safety disclaimer

Use this disclaimer in the README, Streamlit UI, newsletter article, and demo video description:

```text
This project is for educational and technical purposes only. It is not medical advice, diagnosis, treatment, or a recommendation to start, stop, or change any medication, dose, or care plan. Always consult a qualified healthcare professional for personal health decisions.

This project uses publicly available biomedical sources and does not use private patient data, proprietary company data, or confidential clinical data. The system is designed to summarize public evidence and demonstrate governed AI architecture, not to provide clinical decision support.
```

---

## 8. Data sources

### MVP data sources

Use three public sources in version 1:

```text
DailyMed        → official drug-label sections
RxNorm / RxNav  → normalized drug names and identifiers
PubMed / NCBI   → biomedical literature abstracts
```

DailyMed’s API provides access to current Structured Product Label information. RxNorm provides normalized clinical drug names and links drug names across commonly used vocabularies. NCBI E-utilities provide public API access to Entrez databases, including PubMed.

### Explicitly excluded from MVP

Do not include these in version 1:

```text
openFDA FAERS adverse-event data
private patient data
real EHR data
claims data
proprietary drug databases
clinical decision support databases
commercial drug-interaction databases
```

openFDA FAERS belongs later in **Build 4 — Pharmacovigilance Signal Triage Agent**, not in the first MVP.

---

## 9. Initial supported drugs

Start with a small, controlled set of common drugs:

```text
metformin
warfarin
atorvastatin
semaglutide
ibuprofen
acetaminophen
amoxicillin
lisinopril
```

Reason: this set gives useful coverage across diabetes, anticoagulation, statins, GLP-1 therapy, OTC pain medications, antibiotics, and cardiovascular medication while keeping the graph small enough to inspect manually.

---

## 10. Supported question types

### Allowed question types

The MVP should answer safe, public-evidence questions such as:

```text
What does the official label say about warnings for metformin?
What contraindications are listed for warfarin?
What are common adverse reactions listed for atorvastatin?
What does the label say about pregnancy for lisinopril?
What PubMed evidence discusses semaglutide and cardiovascular outcomes?
What label evidence discusses liver-related warnings for acetaminophen?
What label warnings and PubMed evidence discuss bleeding risk with warfarin and ibuprofen?
```

### Blocked or redirected question types

The system must block or redirect personal medical-advice questions such as:

```text
Should I take this medication?
Should I stop taking this medication?
What dose should I take?
Can I combine these two medications?
Is this drug safe for me?
Is my symptom caused by this drug?
Which medication is better for me?
Can I take ibuprofen with warfarin?
```

Safe redirect pattern:

```text
I cannot provide personal medical advice or determine whether a medication is appropriate for you. I can summarize what public drug labels and biomedical literature say, but you should consult a qualified healthcare professional for personal decisions.
```

---

## 11. High-level architecture

```text
User question
        ↓
FastAPI query endpoint
        ↓
Query classifier
        ↓
Drug/entity extractor
        ↓
RxNorm normalizer
        ↓
Hybrid evidence retrieval
        ├── DailyMed label retrieval
        ├── PubMed vector retrieval
        └── Graph relationship lookup
        ↓
Evidence bundle builder
        ↓
External LLM answer generator
        ↓
Evidence contract validator
        ↓
Graph consistency validator
        ↓
Safety policy checker
        ↓
Audit logger
        ↓
Streamlit UI displays answer, citations, graph path, validation result, and audit trace
```

---

## 12. System type

Version 1 is:

```text
governed biomedical GraphRAG pipeline
```

Version 1 is not:

```text
autonomous agent
clinical decision support system
medical chatbot
drug-interaction recommender
```

Future version 2 may become a bounded evidence agent if we add:

```text
source planner
retrieval retry policy
evidence sufficiency judge
claim critic
human review route
```

But version 1 should be presented as a governed pipeline.

---

## 13. Core system components

### 13.1 FastAPI backend

Responsibilities:

```text
receive user query
run query classification
call retrieval services
assemble evidence bundle
call external LLM
run validation
return structured response
store audit log
```

Primary endpoint:

```text
POST /query
```

Optional later endpoints:

```text
GET /audit/{audit_id}
GET /drugs
GET /graph/{drug_name}
GET /health
```

---

### 13.2 Streamlit frontend

Responsibilities:

```text
submit query
display normalized drug entities
show retrieved label sections
show PubMed evidence
show graph paths
show generated answer
show claim-level citations
show safety result
show validation result
show audit trace
```

The UI should make the pipeline visible. The demo should not hide the validation layer.

---

### 13.3 Query classifier

Classifies user intent.

Possible classes:

```text
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

Purpose:

```text
decide whether the system can answer
choose retrieval path
trigger safety refusal when needed
```

---

### 13.4 Drug/entity extractor

Extracts drug names and clinical entities from the query.

Example:

```text
Query:
"What label evidence discusses bleeding risk with warfarin and ibuprofen?"

Extracted entities:
drug_entities = ["warfarin", "ibuprofen"]
clinical_entities = ["bleeding risk"]
```

---

### 13.5 RxNorm normalizer

Normalizes drug names and aliases.

Examples:

```text
Tylenol      → acetaminophen
Advil        → ibuprofen
Glucophage   → metformin
Coumadin     → warfarin
```

Purpose:

```text
avoid treating brand names, generics, and spelling variants as unrelated entities
```

---

### 13.6 DailyMed retriever

Retrieves official label sections.

Initial label sections:

```text
boxed warning
warnings and precautions
contraindications
adverse reactions
drug interactions
use in specific populations
dosage and administration
clinical pharmacology
```

Important: dosage sections may be retrieved for label completeness, but the system must not convert them into personal dosing advice.

---

### 13.7 PubMed retriever

Retrieves supporting biomedical literature.

MVP behavior:

```text
query PubMed via NCBI E-utilities
retrieve article metadata and abstracts
embed abstracts or abstract chunks
perform vector search over the local PubMed evidence cache
rank results by semantic relevance and entity match
```

PubMed is included in MVP because it gives credible public biomedical literature context, but PubMed evidence must not override label-grounded safety boundaries.

---

### 13.8 Vector retrieval layer

Purpose:

```text
find semantically relevant passages from DailyMed sections and PubMed abstracts
```

MVP vector store options:

```text
Chroma for speed
Postgres + pgvector later for stronger production signal
```

Recommendation for MVP:

```text
Use Chroma first if speed matters.
Design interfaces so pgvector can be added later.
```

---

### 13.9 Graph layer

Purpose:

```text
represent normalized drug entities and structured relationships
validate that generated claims do not exceed supported relationships
show graph paths behind claims
```

Recommended graph engine:

```text
Neo4j Community Edition via Docker
```

Fallback if setup friction becomes too high:

```text
NetworkX for local MVP
```

Preferred portfolio path:

```text
Neo4j
```

Reason: Neo4j makes the graph layer visible and easier to demonstrate.

---

## 14. Knowledge graph scope

Do not build a broad biomedical ontology in version 1.

Build a small, purpose-built graph for the initial 8 drugs.

### Node types

```text
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

### Edge types

```text
Drug HAS_INGREDIENT Ingredient
Drug HAS_BRAND_NAME BrandName
Drug HAS_LABEL_SECTION LabelSection
Drug HAS_WARNING Warning
Drug HAS_CONTRAINDICATION Contraindication
Drug HAS_ADVERSE_REACTION AdverseReaction
Drug HAS_INTERACTION DrugInteraction
Drug HAS_POPULATION_WARNING Population
PubMedArticle DISCUSSES Drug
PubMedArticle DISCUSSES Warning
PubMedArticle DISCUSSES AdverseReaction
EvidenceClaim SUPPORTED_BY LabelSection
EvidenceClaim SUPPORTED_BY PubMedArticle
EvidenceClaim HAS_GRAPH_PATH Drug/Relationship/Source
```

### Example graph path

```text
warfarin
  → HAS_WARNING
  → bleeding
  → SUPPORTED_BY
  → DailyMed warnings and precautions section
```

For a multi-hop query:

```text
warfarin
  → HAS_INTERACTION
  → NSAID-related bleeding risk
  → RELATED_DRUG
  → ibuprofen
  → SUPPORTED_BY
  → DailyMed drug interactions section
```

---

## 15. Hybrid retrieval behavior

The hybrid retrieval layer combines:

```text
semantic vector retrieval
structured graph lookup
source priority rules
```

### Example query

```text
What label warnings and PubMed evidence discuss bleeding risk with warfarin and ibuprofen?
```

### Retrieval steps

```text
1. Extract entities:
   warfarin, ibuprofen, bleeding risk

2. Normalize drugs:
   map names through RxNorm

3. Retrieve DailyMed sections:
   warnings, precautions, drug interactions, adverse reactions

4. Retrieve PubMed abstracts:
   search for warfarin + ibuprofen + bleeding risk

5. Query graph:
   check whether known relationships support warning, interaction, or adverse reaction

6. Build evidence bundle:
   include passages, graph paths, source metadata, and relationship types
```

---

## 16. Evidence contract

The evidence contract is the heart of the project.

The system should not return only a free-text answer. It should return structured claims.

### GeneratedAnswer

```text
answer_text
claims[]
citations[]
safety_boundary
validation_status
audit_id
```

### EvidenceClaim

```text
claim_id
claim_text
claim_type
drug_entities
relationship_type
supporting_sources
graph_path
allowed_strength
validation_status
```

### Claim types

```text
label_warning
contraindication
adverse_reaction
drug_interaction
population_specific_warning
literature_summary
uncertainty_statement
safety_refusal
```

### Allowed strength

The system must distinguish between:

```text
label states
label warns
label lists
PubMed discusses
evidence suggests
association reported
causality established
contraindicated
personal recommendation
```

This matters because many hallucinations happen when the model upgrades a weak evidence statement into a strong clinical claim.

---

## 17. Validators

### 17.1 Citation validator

Checks:

```text
each major claim has at least one source
citation IDs exist in retrieved evidence
citation text supports the claim
answer does not cite unrelated sources
```

---

### 17.2 Claim validator

Checks:

```text
claim does not introduce unsupported drug entities
claim does not introduce unsupported adverse events
claim does not overstate evidence
claim does not contradict retrieved label evidence
```

---

### 17.3 Graph consistency validator

Checks:

```text
drug entities exist in graph
relationship type exists or is marked unknown
claim type matches graph relationship
claim does not call a warning a contraindication
claim does not call an association a proven cause
claim graph path connects entities to evidence source
```

Example failure:

```text
Generated claim:
"Ibuprofen is contraindicated with warfarin."

Graph validation:
FAIL — graph supports warning/interaction risk, not contraindication.
```

---

### 17.4 Safety policy checker

Blocks:

```text
personal medication advice
dose recommendations
stop/start medication suggestions
individual safety determinations
symptom causality claims
drug substitution recommendations
```

Allowed:

```text
public label summaries
public literature summaries
educational explanations
source-grounded uncertainty statements
```

---

## 18. Audit log

Every response should create an audit record.

### AuditRecord

```text
audit_id
timestamp
user_query
query_classification
extracted_entities
normalized_drugs
retrieved_dailymed_sections
retrieved_pubmed_articles
graph_paths
llm_model
prompt_version
generated_answer
claim_validation_result
citation_validation_result
graph_validation_result
safety_policy_result
latency_ms
final_response_status
```

This becomes the foundation for **Build 6 — Regulated AI Evidence Flight Recorder**.

---

## 19. MVP vertical slice

Start with one focused workflow.

### Vertical Slice 1

Question type:

```text
Warnings and precautions for a normalized drug
```

Example query:

```text
What does the official label say about warnings and precautions for warfarin?
```

Pipeline:

```text
query
  → classify as warning_question
  → extract warfarin
  → normalize through RxNorm
  → retrieve DailyMed warnings section
  → retrieve PubMed abstracts if query requests literature context
  → graph lookup for Drug → HAS_WARNING → Warning → SUPPORTED_BY → LabelSection
  → generate answer
  → validate claims
  → safety check
  → display answer and trace
```

### Vertical Slice 2

Question type:

```text
Multi-hop drug relationship question
```

Example query:

```text
What label warnings and PubMed evidence discuss bleeding risk with warfarin and ibuprofen?
```

This is the GraphRAG demo slice.

---

## 20. MVP deliverables

### Required deliverables

```text
FastAPI backend
Streamlit frontend
RxNorm client
DailyMed client
PubMed client
vector retrieval layer
small Neo4j graph
hybrid evidence retriever
external LLM answer generator
evidence contract schemas
citation validator
graph consistency validator
strict safety checker
audit logger
small evaluation set
README
architecture diagram
demo video
newsletter article
```

### Optional MVP deliverables

```text
Docker Compose for API + Streamlit + Neo4j
sample graph visualization
source-ranking debug view
latency metrics
basic pytest suite
```

---

## 21. Technical stack

### MVP stack

```text
Python
FastAPI
Streamlit
Pydantic
httpx
Chroma or local vector store
Neo4j Community Edition
external LLM API
SQLite or DuckDB for audit logs
Pytest
```

### Later stack

```text
Postgres + pgvector
OpenTelemetry
Docker Compose
Kubernetes
vLLM backend
Grafana dashboard
structured eval harness
```

Do not use Kubernetes or vLLM in the MVP. Those can be added after the governed evidence pipeline works.

---

## 22. Suggested repository structure

```text
biomedical-ai-infra-lab/
  001-governed-biomedical-graphrag/
    README.md

    docs/
      scope.md
      system_design.md
      safety_boundaries.md
      evidence_contracts.md
      graph_schema.md
      evaluation_plan.md
      failure_modes.md

    app/
      api/
        query_api.py

      contracts/
        drug_query.py
        normalized_drug.py
        evidence_source.py
        drug_label_section.py
        pubmed_evidence.py
        evidence_bundle.py
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

      dashboard/
        streamlit_app.py

    evals/
      safe_label_questions.jsonl
      unsafe_medical_advice_questions.jsonl
      multi_hop_graphrag_questions.jsonl
      hallucination_trap_questions.jsonl

    tests/
      test_drug_normalization.py
      test_dailymed_retrieval.py
      test_pubmed_retrieval.py
      test_graph_queries.py
      test_citation_validation.py
      test_graph_consistency_validation.py
      test_safety_policy.py
```

---

## 23. Evaluation plan

Create a small evaluation set.

### Evaluation categories

```text
safe label questions
multi-hop graph questions
unsafe medical-advice questions
citation stress questions
hallucination trap questions
```

### Example eval counts

```text
30 safe label questions
20 multi-hop GraphRAG questions
20 unsafe medical-advice questions
20 citation stress questions
10 hallucination trap questions
```

### Metrics

```text
citation coverage rate
unsupported claim rate
graph consistency pass rate
correct refusal rate
retrieval relevance
answer faithfulness
safety-policy pass rate
latency
```

---

## 24. Failure modes to intentionally demonstrate

The project should show both success and failure cases.

Important failure modes:

```text
wrong drug normalization
retrieved wrong label section
PubMed article mentions drug but not the specific claim
LLM upgrades warning into contraindication
LLM claims causality from weak evidence
LLM gives personal medical advice
citation attached to unsupported claim
graph path missing for a generated relationship
label and literature appear to differ in strength of claim
```

These failure modes are valuable for content and portfolio credibility.

---

## 25. Content deliverables

This build should produce:

```text
1 Stackbytes newsletter article
1 architecture diagram
1 YouTube walkthrough
3–5 LinkedIn posts
1 GitHub repo
1 demo screen recording
1 failure-mode article
```

### Suggested article title

```text
Medical RAG Is Broken Without Evidence Contracts
```

### Suggested YouTube title

```text
Building a Governed Biomedical GraphRAG Pipeline with Drug Labels, PubMed, and Evidence Contracts
```

### Suggested LinkedIn post sequence

```text
Post 1 — Why medical RAG cannot be simple chunk retrieval
Post 2 — Vector search finds evidence; graphs validate relationships
Post 3 — How evidence contracts bind claims to sources
Post 4 — Why no-medical-advice safety boundaries matter
Post 5 — Demo: warfarin + ibuprofen multi-hop evidence query
```

---

## 26. Monetization angle

This build supports future consulting offers such as:

```text
Evidence RAG audit
Healthcare RAG safety review
Citation validation implementation
Biomedical GraphRAG prototype
Regulated AI observability design
LLM evaluation harness for medical content systems
```

Potential buyers:

```text
healthtech startups
pharma AI teams
medical content companies
clinical workflow AI vendors
RAG platform teams
regulatory technology teams
```

---

## 27. Success criteria

### Technical success

```text
system answers safe label questions with citations
system retrieves DailyMed and PubMed evidence
system normalizes drugs through RxNorm
system builds a small graph for the initial drugs
system validates claim-source support
system catches at least one graph inconsistency
system refuses personal medical-advice queries
system audit-logs every answer
```

### Portfolio success

```text
architecture is clear
repo is clean
Pydantic contracts are visible
validation logic is testable
failure modes are documented
demo shows more than a generic RAG chatbot
```

### Content success

```text
readers understand why medical RAG needs governance
technical audience sees the GraphRAG architecture
healthtech audience sees safety maturity
people ask for Build 3 benchmark harness or Build 6 evidence flight recorder next
```

---

## 28. Out-of-scope for version 1

Do not include:

```text
patient-specific advice
real patient data
EHR integration
clinical decision support
drug-dosing recommendations
commercial drug-interaction databases
openFDA FAERS
autonomous agent planner
human clinician workflow
Kubernetes deployment
vLLM deployment
full ontology engineering
large-scale biomedical knowledge graph
```

These are intentionally deferred to keep Build 1 focused.

---

## 29. Phased implementation boundary

### Phase 1A — Governed RAG foundation

```text
FastAPI + Streamlit
RxNorm normalization
DailyMed retrieval
PubMed retrieval
evidence bundle schema
external LLM generation
citation validator
safety checker
audit log
```

### Phase 1B — GraphRAG extension

```text
Neo4j graph for initial drugs
graph loader
graph queries
graph path display
graph consistency validator
multi-hop query demo
```

### Phase 1C — Evaluation and content packaging

```text
eval datasets
failure-mode cases
demo walkthrough
README
architecture article
newsletter post
```

---

## 30. Final MVP statement

Build 1 will deliver a public-data-only governed biomedical GraphRAG pipeline that uses RxNorm for drug normalization, DailyMed for drug-label evidence, PubMed for biomedical literature, vector retrieval for passage discovery, graph lookup for relationship validation, evidence contracts for claim-source binding, strict safety policies to block medical advice, and audit logs to preserve every system decision.

The build demonstrates that in biomedical AI, answer generation is only one layer. The more important engineering problem is governance: evidence, validation, safety, and traceability.

