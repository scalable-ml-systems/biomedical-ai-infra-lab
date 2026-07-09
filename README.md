# Biomedical AI Infrastructure Lab

Biomedical AI Infrastructure Lab is for building AI infrastructure systems for biomedical, pharma, and life-sciences workflows.

The focus is not generic healthcare chatbots.

The focus is on the infrastructure layers required for trustworthy biomedical AI:

- evidence retrieval
- biomedical entity normalization
- GraphRAG
- claim-to-source validation
- safety policy enforcement
- audit logging
- evaluation harnesses
- model benchmarking
- GPU-backed biomedical workloads

---

## Core thesis

Biomedical AI systems require more than answer generation.

They need governed infrastructure:

```text
public biomedical sources
        ↓
retrieval and normalization
        ↓
evidence graph / vector search
        ↓
LLM generation
        ↓
claim-level validation
        ↓
safety boundary enforcement
        ↓
audit trail

The goal of this lab is to demonstrate how AI systems should be designed when the domain is safety-sensitive, evidence-heavy, and regulated.

Build 1
Governed Biomedical GraphRAG Pipeline with Evidence Contracts

Public title:

Medical RAG Is Broken Without Evidence Contracts

Build folder:

builds/001-governed-biomedical-graphrag/

Build 1 demonstrates a public-data-only biomedical GraphRAG pipeline that combines:

RxNorm drug normalization
DailyMed drug-label retrieval
PubMed literature retrieval
vector search over biomedical text
graph-based relationship validation
claim-level evidence contracts
strict no-medical-advice safety checks
audit logging
Streamlit evidence-trace UI

This is a governed GraphRAG pipeline, not an autonomous medical agent and not a clinical decision-support system.

Repository structure
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
      app/
      data/
      evals/
      tests/
Safety boundary

This lab is for educational and technical purposes only.

It does not provide:

medical advice
diagnosis
treatment recommendations
drug dosing guidance
personal medication decisions
patient-specific drug-interaction advice
clinical decision support

All biomedical examples must use public sources, synthetic data, or clearly documented open research datasets.

Private patient data, proprietary pharma data, confidential company information, EHR exports, and commercial drug databases are out of scope unless explicitly documented and legally permitted in a future setting.

Public data sources for Build 1

Build 1 uses:

DailyMed
RxNorm / RxNav
PubMed / NCBI E-utilities

Build 1 does not use:

real patient data
EHR data
claims data
commercial drug databases
proprietary pharma data
confidential company data

## Disclaimer

This project is for educational and technical purposes only.

It is not medical advice, diagnosis, treatment, or a recommendation to start, stop, or change any medication, dose, or care plan. Always consult a qualified healthcare professional for personal health decisions.

This project uses publicly available biomedical sources and does not use private patient data, proprietary company data, or confidential clinical data. The system is designed to summarize public evidence and demonstrate governed AI architecture, not to provide clinical decision support.
