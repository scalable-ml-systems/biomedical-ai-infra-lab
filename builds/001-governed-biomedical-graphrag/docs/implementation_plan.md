# Implementation Plan — Build 1: Governed Biomedical GraphRAG Pipeline with Evidence Contracts

## Repo

```text
biomedical-ai-infra-lab/
```

## Build folder

```text
biomedical-ai-infra-lab/
  builds/
    001-governed-biomedical-graphrag/
```

## Build label

**Build 1 — Governed Biomedical GraphRAG Pipeline with Evidence Contracts**

## Public title

**Medical RAG Is Broken Without Evidence Contracts**

---

# Implementation principle

Build this in thin vertical slices.

Do not start by building the full graph, full PubMed pipeline, full UI, and all validators at once.

The correct order is:

```text
1. Scaffold clean project structure
2. Define data contracts
3. Build safe query classification
4. Add drug normalization
5. Add DailyMed retrieval
6. Add PubMed retrieval
7. Build evidence bundle
8. Add external LLM generation
9. Add evidence contract validation
10. Add strict safety checker
11. Add audit logging
12. Add Streamlit trace UI
13. Add graph layer
14. Add graph consistency validation
15. Add evaluation set
16. Package demo and content
```

The system should work end-to-end before it becomes sophisticated.

---

# Phase 0 — Project scaffold

## Goal

Create the repo structure and make the project runnable locally.

## Why

A clean scaffold prevents the build from becoming a messy prototype. This project is meant to demonstrate regulated-domain engineering maturity, so structure matters from day one.

## Implement

Create:

```text
biomedical-ai-infra-lab/
  README.md
  pyproject.toml
  .env.example
  docker-compose.yml

  docs/
    roadmap.md
    safety_boundaries.md
    data_sources.md
    glossary.md

  shared/
    biomedical_ai_infra/
      __init__.py

  builds/
    001-governed-biomedical-graphrag/
      README.md

      docs/
        scope.md
        technical_specification.md
        implementation_plan.md

      app/
        __init__.py

        api/
          __init__.py
          query_api.py
          health_api.py

        contracts/
          __init__.py

        retrieval/
          __init__.py

        graph/
          __init__.py

        generation/
          __init__.py

        validation/
          __init__.py

        audit/
          __init__.py

        dashboard/
          __init__.py

        config/
          __init__.py
          settings.py

      data/
        seed_drugs.yaml
        cached_sources/
          dailymed/
          pubmed/

      evals/

      tests/
```

## Done when

```text
repo installs locally
FastAPI health endpoint runs
Streamlit placeholder page runs
pytest discovers tests
.env.example exists
README explains project purpose and safety boundary
```

---

# Phase 1 — Core data contracts

## Goal

Define the structured objects that move through the pipeline.

## Why

The strongest part of this build is not the LLM. It is the evidence contract layer. We need structured contracts before retrieval and generation become complicated.

## Implement

Create Pydantic models:

```text
app/contracts/drug_query.py
app/contracts/normalized_drug.py
app/contracts/drug_label_section.py
app/contracts/pubmed_evidence.py
app/contracts/evidence_bundle.py
app/contracts/graph_path.py
app/contracts/evidence_claim.py
app/contracts/generated_answer.py
app/contracts/validation_result.py
app/contracts/safety_policy_result.py
app/contracts/audit_record.py
```

Minimum models:

```text
DrugQuery
NormalizedDrug
DrugLabelSection
PubMedEvidence
EvidenceBundle
GraphPath
EvidenceClaim
GeneratedAnswer
ValidationResult
SafetyPolicyResult
AuditRecord
```

## Key design rule

Every generated answer must eventually become:

```text
answer_text
claims[]
citations[]
validation_result
safety_result
audit_id
```

Do not allow unstructured free-text answers to bypass validation.

## Done when

```text
all contracts import cleanly
contracts have tests
sample objects can serialize to JSON
sample EvidenceBundle can include DailyMed + PubMed + graph evidence
```

---

# Phase 2 — Configuration and settings

## Goal

Centralize environment variables and runtime settings.

## Why

This build uses external APIs, an external LLM, local storage, and later Neo4j. Hardcoding these values will make the project brittle.

## Implement

Create:

```text
app/config/settings.py
```

Settings should include:

```text
APP_ENV
LOG_LEVEL

EXTERNAL_LLM_PROVIDER
EXTERNAL_LLM_MODEL
EXTERNAL_LLM_API_KEY

NCBI_TOOL_NAME
NCBI_EMAIL

VECTOR_STORE_PATH
AUDIT_DB_PATH

NEO4J_URI
NEO4J_USERNAME
NEO4J_PASSWORD

ENABLE_PUBMED
ENABLE_GRAPH_VALIDATION
ENABLE_STRICT_SAFETY
```

Create `.env.example`.

## Done when

```text
settings load from environment
missing required secrets produce clear error messages
tests can override settings
```

---

# Phase 3 — FastAPI skeleton

## Goal

Create the backend API shape before implementing the full pipeline.

## Why

This lets every later component plug into a stable request/response flow.

## Implement

Create:

```text
app/api/health_api.py
app/api/query_api.py
```

Endpoints:

```text
GET /health
POST /query
GET /audit/{audit_id}
GET /drugs
```

Initial `/query` can return a placeholder structured response.

## Done when

```text
GET /health returns healthy status
POST /query accepts DrugQuery
POST /query returns structured response shape
OpenAPI docs load
```

---

# Phase 4 — Query classifier

## Goal

Classify whether a user query is safe and what retrieval path it needs.

## Why

Biomedical systems must know when not to answer. This classifier is the first safety gate.

## Implement

Create:

```text
app/retrieval/query_classifier.py
```

Initial classes:

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

Start with deterministic rules, not LLM classification.

Examples:

```text
"What does the label say about warnings for metformin?"
→ warning_question

"What PubMed evidence discusses semaglutide and cardiovascular outcomes?"
→ pubmed_literature_question

"Can I take ibuprofen with warfarin?"
→ personal_medical_advice
```

## Done when

```text
safe label questions classify correctly
unsafe personal medication questions classify as personal_medical_advice
classification result is included in the API response
tests cover safe, unsafe, and out-of-scope queries
```

---

# Phase 5 — Drug entity extraction

## Goal

Extract drug names from the query.

## Why

The system must identify biomedical entities before normalization, retrieval, and graph lookup.

## Implement

Create:

```text
app/retrieval/drug_entity_extractor.py
```

For MVP, use a controlled drug list:

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

Also include common brand aliases later:

```text
Tylenol → acetaminophen
Advil → ibuprofen
Glucophage → metformin
Coumadin → warfarin
```

## Done when

```text
extracts one drug from simple questions
extracts two drugs from multi-hop questions
returns empty list when no supported drug appears
does not guess unsupported drugs
```

---

# Phase 6 — RxNorm normalization

## Goal

Normalize drug mentions to canonical drug entities.

## Why

Medical RAG fails when it treats brand names, generics, spelling variants, and synonyms as unrelated terms.

## Implement

Create:

```text
app/retrieval/rxnorm_client.py
```

Behavior:

```text
input drug mention
  → call RxNorm / RxNav
  → return normalized name and RxCUI
```

For speed, add a fallback local mapping for the initial drugs.

## Done when

```text
warfarin normalizes correctly
Coumadin normalizes to warfarin
Advil normalizes to ibuprofen
unknown drug returns unmatched
normalization result is included in audit trace
```

---

# Phase 7 — DailyMed retrieval

## Goal

Retrieve official drug-label sections.

## Why

DailyMed label evidence is the grounding layer for drug-label questions. It should have priority over generic web evidence.

## Implement

Create:

```text
app/retrieval/dailymed_client.py
```

Initial sections:

```text
boxed_warning
warnings_and_precautions
contraindications
adverse_reactions
drug_interactions
use_in_specific_populations
dosage_and_administration
clinical_pharmacology
```

Important implementation boundary:

```text
Retrieve dosage sections if needed for label completeness.
Never generate patient-specific dosing advice.
```

Cache retrieved label sections under:

```text
data/cached_sources/dailymed/
```

## Done when

```text
DailyMed retrieval works for at least 3 initial drugs
label sections are parsed into DrugLabelSection objects
retrieved sections include source IDs
cached files can be reused without repeated API calls
```

---

# Phase 8 — PubMed retrieval

## Goal

Retrieve credible public biomedical literature context.

## Why

PubMed adds trusted public literature evidence and makes the build more credible than label-only RAG.

## Implement

Create:

```text
app/retrieval/pubmed_client.py
```

Flow:

```text
construct PubMed query
call NCBI ESearch
call ESummary or EFetch
extract title, abstract, PMID, journal, year
cache abstract metadata
return PubMedEvidence objects
```

Initial queries:

```text
warfarin ibuprofen bleeding risk
semaglutide cardiovascular outcomes
acetaminophen liver injury overdose
atorvastatin myopathy risk
lisinopril pregnancy warning
```

Cache under:

```text
data/cached_sources/pubmed/
```

## Done when

```text
PubMed retrieval returns article metadata
abstracts are parsed when available
results are cached
PubMed evidence can be included in EvidenceBundle
```

---

# Phase 9 — Evidence bundle builder

## Goal

Merge normalized drugs, label sections, PubMed evidence, and later graph paths into one structured bundle.

## Why

The LLM should not receive loose chunks. It should receive a controlled evidence bundle.

## Implement

Create:

```text
app/retrieval/evidence_bundle_builder.py
```

Bundle contains:

```text
normalized_drugs
label_sections
pubmed_articles
vector_results
graph_paths
source_priority
retrieval_status
```

## Done when

```text
one query produces one EvidenceBundle
evidence bundle serializes to JSON
each source has stable source_id
evidence bundle can be passed to answer generator
```

---

# Phase 10 — Vector retrieval

## Goal

Add semantic search over cached DailyMed sections and PubMed abstracts.

## Why

Vector search finds relevant passages when keyword search is not enough.

## Implement

Create:

```text
app/retrieval/vector_retriever.py
```

MVP store:

```text
Chroma
```

Later replacement path:

```text
Postgres + pgvector
```

Index:

```text
DailyMed label section chunks
PubMed abstract chunks
```

Return:

```text
source_id
source_type
score
text
metadata
```

## Done when

```text
cached sources can be embedded
query returns top-k relevant chunks
retrieved chunks preserve source IDs
vector results can be included in EvidenceBundle
```

---

# Phase 11 — External LLM answer generation

## Goal

Generate structured answers from retrieved evidence.

## Why

The LLM should summarize evidence, but it should not be trusted as the final authority.

## Implement

Create:

```text
app/generation/prompt_builder.py
app/generation/answer_generator.py
```

Prompt must require:

```text
use only retrieved evidence
produce structured JSON
attach source IDs to each major claim
include uncertainty when needed
avoid personal medical advice
avoid dosing guidance
avoid start/stop medication language
```

LLM output shape:

```text
answer_text
claims[]
safety_boundary
```

## Done when

```text
LLM returns parseable GeneratedAnswer
claims include supporting_source_ids
unsafe language is not encouraged by prompt
generation failure does not expose unvalidated answer
```

---

# Phase 12 — Citation validator

## Goal

Validate that every major claim has source support.

## Why

This is the evidence-contract core of the build.

## Implement

Create:

```text
app/validation/citation_validator.py
```

Checks:

```text
each non-refusal claim has at least one source
source IDs exist in EvidenceBundle
claim does not cite unrelated source
label-specific claims cite DailyMed
literature-summary claims cite PubMed
```

## Done when

```text
valid claims pass
missing citations fail
fake source IDs fail
PubMed-only citation cannot support label-specific claim
validation result is returned to API and UI
```

---

# Phase 13 — Claim validator

## Goal

Detect unsupported or over-strengthened claims.

## Why

Many medical hallucinations happen because the model upgrades “label warns” into “contraindicated” or “associated with” into “causes.”

## Implement

Create:

```text
app/validation/claim_validator.py
```

Rules:

```text
no unsupported drug entity
no unsupported adverse event
no unsupported population claim
no causality upgrade
no recommendation language
no contradiction with label evidence
```

Disallowed language:

```text
you should
you can safely
you should stop
you should start
this is safe for you
this caused your symptom
the best medication for you
```

## Done when

```text
overclaiming is caught
personal recommendation language is caught
unsupported drug mentions are caught
claim validation result is visible in UI
```

---

# Phase 14 — Strict safety policy checker

## Goal

Block personal medical advice.

## Why

This project must stay educational and technical. The safety checker is non-negotiable.

## Implement

Create:

```text
app/validation/safety_policy_checker.py
```

Blocked intents:

```text
personal medication advice
start / stop / change medication
dose adjustment
personal safety determination
symptom causality
individual interaction decision
drug substitution recommendation
```

Safe refusal template:

```text
I cannot provide personal medical advice or determine whether a medication is appropriate for you. I can summarize what public drug labels and biomedical literature say, but you should consult a qualified healthcare professional for personal decisions.
```

## Done when

```text
unsafe query is refused before normal generation
unsafe generated output is blocked after generation
safety result is audit-logged
Streamlit clearly shows safety decision
```

---

# Phase 15 — Audit logging

## Goal

Store a trace for every query.

## Why

Auditability is a core regulated-domain signal. Every answer must be reconstructable.

## Implement

Create:

```text
app/audit/audit_store.py
app/audit/audit_logger.py
```

MVP storage:

```text
DuckDB or SQLite
```

Audit fields:

```text
audit_id
timestamp
user_query
query_classification
normalized_drugs
retrieved DailyMed source IDs
retrieved PubMed source IDs
graph path IDs
LLM model
prompt version
generated answer
citation validation result
claim validation result
graph validation result
safety policy result
latency
final response status
```

## Done when

```text
every query creates an audit record
unsafe refusals create audit records
validation failures create audit records
GET /audit/{audit_id} returns trace
```

---

# Phase 16 — Streamlit evidence-trace UI

## Goal

Create a visual demo interface.

## Why

The value of this project is the visible governance pipeline. The UI should show how the answer was produced and validated.

## Implement

Create:

```text
app/dashboard/streamlit_app.py
```

UI panels:

```text
Query input
Final answer
Normalized drug entities
DailyMed evidence
PubMed evidence
Graph paths
Claims table
Citation validation result
Graph validation result
Safety policy result
Audit trace
```

## Done when

```text
user can submit a query
answer appears with citations
retrieved sources are visible
claim validation is visible
safety result is visible
audit ID is visible
```

---

# Phase 17 — Neo4j setup

## Goal

Add the graph database.

## Why

The graph layer is what makes this GraphRAG instead of ordinary RAG.

## Implement

Add Neo4j to:

```text
docker-compose.yml
```

Create:

```text
app/graph/graph_schema.py
app/graph/graph_loader.py
app/graph/graph_queries.py
```

Seed graph data:

```text
data/graph_seed/drug_nodes.yaml
data/graph_seed/relationship_edges.yaml
```

Initial node types:

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

Initial edge types:

```text
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
```

## Done when

```text
Neo4j runs locally
initial drugs load into graph
label-derived relationships load into graph
simple Cypher queries return graph paths
```

---

# Phase 18 — Graph retriever

## Goal

Query graph relationships for normalized drugs.

## Why

The graph tells the system what relationship type is supported: warning, contraindication, adverse reaction, interaction, or unknown.

## Implement

Create:

```text
app/retrieval/graph_retriever.py
```

Queries:

```text
get warnings for drug
get contraindications for drug
get adverse reactions for drug
get interactions involving two drugs
get graph paths supporting evidence claim
```

## Done when

```text
single-drug graph query works
two-drug relationship query works
graph paths return source IDs
graph paths are included in EvidenceBundle
```

---

# Phase 19 — Graph consistency validator

## Goal

Validate generated claims against graph paths.

## Why

This is what catches relationship overreach.

## Implement

Create:

```text
app/validation/graph_consistency_validator.py
```

Rules:

```text
drug must exist in graph
relationship must exist or be marked unknown
claim type must match graph relationship
contraindication claim requires HAS_CONTRAINDICATION
warning claim requires HAS_WARNING or supported equivalent
interaction claim requires HAS_INTERACTION
claim cannot call warning a contraindication
claim cannot call association proven causality
```

## Done when

```text
valid graph-supported claims pass
unsupported relationships fail
warning mislabeled as contraindication fails
graph failure appears in UI
graph failure is audit-logged
```

---

# Phase 20 — Hybrid evidence retriever

## Goal

Combine DailyMed, PubMed, vector search, and graph lookup into one retrieval interface.

## Why

The rest of the system should not need to know how many retrieval systems exist. It should receive one evidence bundle.

## Implement

Create:

```text
app/retrieval/hybrid_evidence_retriever.py
```

Flow:

```text
normalized drugs
  → DailyMed retrieval
  → PubMed retrieval
  → vector search
  → graph lookup
  → ranked evidence bundle
```

Source priority:

```text
DailyMed label evidence is highest priority for label claims.
PubMed supports literature context.
Graph validates relationship type.
LLM answer must not exceed strongest supported relation.
```

## Done when

```text
single interface returns complete EvidenceBundle
retrieval path changes based on query class
multi-hop query returns text evidence + graph evidence
```

---

# Phase 21 — Evaluation datasets

## Goal

Create test cases that prove the system works and fails safely.

## Why

Without evals, this is just a demo. Evals make it a credible engineering artifact.

## Implement

Create:

```text
evals/safe_label_questions.jsonl
evals/unsafe_medical_advice_questions.jsonl
evals/multi_hop_graphrag_questions.jsonl
evals/hallucination_trap_questions.jsonl
```

Target MVP size:

```text
30 safe label questions
20 unsafe medical-advice questions
20 multi-hop GraphRAG questions
10 hallucination-trap questions
```

## Done when

```text
eval files exist
eval runner can call /query
metrics are calculated
results are saved to a report
```

---

# Phase 22 — Evaluation runner

## Goal

Run the system against the evaluation sets.

## Why

This gives measurable proof that governance improved the system.

## Implement

Create:

```text
app/evals/eval_runner.py
app/evals/metrics.py
```

Metrics:

```text
citation coverage rate
unsupported claim rate
graph consistency pass rate
correct refusal rate
retrieval relevance
answer faithfulness
safety-policy pass rate
average latency
p95 latency
```

Pass criteria:

```text
>= 90% correct refusal rate on unsafe medical-advice questions
>= 85% citation coverage on safe label questions
0 known personal dosing recommendations
graph validator catches predefined contradiction traps
100% audit log creation
```

## Done when

```text
eval runner executes locally
metrics report is generated
README includes latest eval results
```

---

# Phase 23 — Failure-mode demonstrations

## Goal

Create intentionally bad cases to show why governance matters.

## Why

The content angle becomes much stronger when you show what ordinary RAG gets wrong.

## Implement

Document failure modes:

```text
wrong drug normalization
retrieved wrong label section
PubMed article mentions drug but not claim
LLM upgrades warning into contraindication
LLM claims causality from weak evidence
LLM gives personal medical advice
citation attached to unsupported claim
graph path missing for relationship claim
```

Create examples under:

```text
docs/failure_modes.md
```

## Done when

```text
at least 5 failure modes are documented
at least 3 are reproducible in evals
Streamlit demo can show validation failure
```

---

# Phase 24 — Documentation package

## Goal

Make the project portfolio-ready.

## Why

The build needs to communicate clearly to both technical and non-technical audiences.

## Implement

Docs:

```text
docs/scope.md
docs/technical_specification.md
docs/implementation_plan.md
docs/system_design.md
docs/safety_boundaries.md
docs/evidence_contracts.md
docs/graph_schema.md
docs/evaluation_plan.md
docs/failure_modes.md
```

README sections:

```text
what this project demonstrates
what this project is not
architecture
setup
demo queries
safety disclaimer
data sources
evaluation results
future work
```

## Done when

```text
README explains the build in under 2 minutes
setup steps are reproducible
demo queries are listed
safety disclaimer is visible
architecture diagram exists
```

---

# Phase 25 — Content package

## Goal

Turn the build into public authority.

## Why

This build is not only a technical artifact. It is also the first pillar for the biomedical AI infrastructure channel.

## Deliver

```text
1 Stackbytes article
1 architecture diagram
1 YouTube walkthrough
3–5 LinkedIn posts
1 demo screen recording
1 failure-mode post
```

Suggested Stackbytes title:

```text
Medical RAG Is Broken Without Evidence Contracts
```

Suggested YouTube title:

```text
Building a Governed Biomedical GraphRAG Pipeline with Drug Labels, PubMed, and Evidence Contracts
```

Suggested LinkedIn sequence:

```text
Post 1 — Why medical RAG cannot be simple chunk retrieval
Post 2 — Vector search finds evidence; graphs validate relationships
Post 3 — Evidence contracts bind generated claims to sources
Post 4 — Strict safety boundaries: no medical advice
Post 5 — Demo: warfarin + ibuprofen multi-hop evidence query
```

## Done when

```text
repo is public or portfolio-ready
article draft is ready
demo video script is ready
LinkedIn post sequence is ready
```

---

# Recommended implementation order summary

```text
Phase 0   — Project scaffold
Phase 1   — Core data contracts
Phase 2   — Configuration and settings
Phase 3   — FastAPI skeleton
Phase 4   — Query classifier
Phase 5   — Drug entity extraction
Phase 6   — RxNorm normalization
Phase 7   — DailyMed retrieval
Phase 8   — PubMed retrieval
Phase 9   — Evidence bundle builder
Phase 10  — Vector retrieval
Phase 11  — External LLM answer generation
Phase 12  — Citation validator
Phase 13  — Claim validator
Phase 14  — Strict safety policy checker
Phase 15  — Audit logging
Phase 16  — Streamlit evidence-trace UI
Phase 17  — Neo4j setup
Phase 18  — Graph retriever
Phase 19  — Graph consistency validator
Phase 20  — Hybrid evidence retriever
Phase 21  — Evaluation datasets
Phase 22  — Evaluation runner
Phase 23  — Failure-mode demonstrations
Phase 24  — Documentation package
Phase 25  — Content package
```

---

# MVP cut line

If we need a strict MVP boundary, stop after:

```text
Phase 16 — Streamlit evidence-trace UI
```

That gives a complete governed RAG system.

Then add:

```text
Phase 17–20
```

to turn it into full GraphRAG.

But because GraphRAG is the differentiator, the repo and contracts should be designed for graph support from the start.

---

# Final build outcome

At the end of this implementation plan, Build 1 should demonstrate:

```text
A user asks a safe biomedical evidence question.
The system normalizes drug names.
It retrieves DailyMed and PubMed evidence.
It uses vector retrieval for semantic evidence discovery.
It uses a graph to validate drug relationships.
It generates a structured answer.
It validates every claim against sources.
It blocks personal medical advice.
It stores a full audit trace.
It displays the entire evidence path in Streamlit.
```

That is the full implementation target for **Build 1 — Governed Biomedical GraphRAG Pipeline with Evidence Contracts**.

