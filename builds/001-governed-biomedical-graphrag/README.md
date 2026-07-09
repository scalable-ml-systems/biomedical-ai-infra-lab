# Build 1 — Governed Biomedical GraphRAG Pipeline with Evidence Contracts

**Medical RAG Is Broken Without Evidence Contracts**

---

## Project summary

This build demonstrates a governed biomedical GraphRAG pipeline for public drug-label and biomedical literature evidence.

The system combines:

- RxNorm drug-name normalization
- DailyMed drug-label retrieval
- PubMed literature retrieval
- vector search over biomedical text
- graph-based drug relationship validation
- claim-level evidence contracts
- strict no-medical-advice safety checks
- audit logging
- Streamlit evidence-trace UI

The goal is to show that biomedical RAG should not be a simple “retrieve chunks and ask an LLM” workflow.

In biomedical and pharma contexts, the system must show:

```text
What evidence was retrieved?
Which claim came from which source?
What relationship does the graph support?
Did the answer overstate the evidence?
Was the answer safe to return?
Can the answer be audited later?

### Core thesis

Generic RAG retrieves relevant text.

Governed biomedical GraphRAG must go further:

- Vector search finds relevant passages.
- Graph lookup validates biomedical relationships.
- Evidence contracts bind generated claims to sources.
- Safety policies block personal medical advice.
- Audit logs preserve every decision.

This build is designed to reduce hallucination risk by forcing generated biomedical claims to pass through validation before being returned.

### System type

This is:

a governed biomedical GraphRAG pipeline

This is not:

an autonomous medical agent
a clinical decision-support system
a medical chatbot
a dosing tool
a diagnosis tool

Future versions may add bounded agentic behavior, but version 1 is a governed pipeline.

MVP data sources

This build uses public sources only:

Source	Purpose
DailyMed	Official drug-label sections
RxNorm / RxNav	Drug-name normalization
PubMed / NCBI E-utilities	Biomedical literature abstracts
Initial supported drugs

The MVP starts with a small controlled drug set:

metformin
warfarin
atorvastatin
semaglutide
ibuprofen
acetaminophen
amoxicillin
lisinopril

This keeps the graph small enough to inspect manually while still covering several useful medication categories.

### Supported question types

The system should answer safe, public-evidence questions such as:

What does the official label say about warnings for metformin?

What contraindications are listed for warfarin?

What are common adverse reactions listed for atorvastatin?

What does the label say about pregnancy for lisinopril?

What PubMed evidence discusses semaglutide and cardiovascular outcomes?

What label warnings and PubMed evidence discuss bleeding risk with warfarin and ibuprofen?

### Blocked question types

The system must block or redirect personal medical-advice questions such as:

Should I take this medication?

Should I stop taking this medication?

What dose should I take?

Can I combine these two medications?

Is this drug safe for me?

Is my symptom caused by this drug?

Which medication is better for me?

### Safe behavior:

I cannot provide personal medical advice or determine whether a medication is appropriate for you. I can summarize what public drug labels and biomedical literature say, but you should consult a qualified healthcare professional for personal decisions.

### High-level architecture

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
        ├── PubMed literature retrieval
        ├── vector retrieval
        └── graph relationship lookup
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
Streamlit evidence-trace UI

### Evidence contract concept

The system should not return only free text.

It should return structured claims:

GeneratedAnswer
  answer_text
  claims[]
  citations[]
  validation_result
  safety_result
  audit_id

Each claim should include:

claim_text
claim_type
drug_entities
relationship_type
supporting_source_ids
graph_path_ids
allowed_strength
validation_status

This is the central engineering idea of the build.

### Example GraphRAG query

Example user query:

What label warnings and PubMed evidence discuss bleeding risk with warfarin and ibuprofen?

### Expected system behavior:

1. Classify as multi-hop evidence question.
2. Extract warfarin, ibuprofen, and bleeding risk.
3. Normalize drug names through RxNorm.
4. Retrieve DailyMed label sections for both drugs.
5. Retrieve relevant PubMed abstracts.
6. Query the graph for warning or interaction relationships.
7. Generate an answer using retrieved evidence only.
8. Validate claim-source support.
9. Validate graph relationship strength.
10. Block any personal medical advice.
11. Store a full audit trace.

### Project Repo

001-governed-biomedical-graphrag/
  README.md

  docs/
    scope.md
    technical_specification.md
    implementation_plan.md
    system_design.md
    safety_boundaries.md
    evidence_contracts.md
    graph_schema.md
    evaluation_plan.md
    failure_modes.md

  app/
    api/
    contracts/
    retrieval/
    graph/
    generation/
    validation/
    audit/
    dashboard/
    config/

  data/
    cached_sources/
      dailymed/
      pubmed/
    graph_seed/

  evals/

  tests/

## Technical stack

### MVP stack:

Python
FastAPI
Streamlit
Pydantic
httpx
Chroma
Neo4j
DuckDB or SQLite
External LLM API
pytest
ruff

### Safety disclaimer

This project is for educational and technical purposes only.

It is not medical advice, diagnosis, treatment, or a recommendation to start, stop, or change any medication, dose, or care plan. Always consult a qualified healthcare professional for personal health decisions.

This project uses publicly available biomedical sources and does not use private patient data, proprietary company data, or confidential clinical data. The system is designed to summarize public evidence and demonstrate governed AI architecture, not to provide clinical decision support.
