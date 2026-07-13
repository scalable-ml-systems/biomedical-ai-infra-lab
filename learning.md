1. Go deep here (non‑negotiable)
These are your learning priorities and your differentiation. Spend real time and care:

a) Ontology base & design
ontology_base.py:

OntologyObjectType, SourceSystem, ID scheme, timestamps, validation states.

Clear design decisions:

How you name things

How IDs are constructed

How you think about “source of truth” for each entity

This is where you build your ontology muscle.

b) Core biomedical entities & evidence sources
biomedical_entities.py:

BiomedicalEntity, Drug, maybe 1–2 others (e.g., WarningConcept).

evidence_sources.py:

SourceDocument, Citation, maybe DailyMedSection and PubMedArticle.

Keep the number of classes small, but:

Make the patterns clean and reusable.

Think about how these will scale when you add more entities later.

c) Governance & validation contracts
governance.py:

EvidenceClaim, ValidationResult, maybe one or two subtypes.

Explicit states:

supported, unsupported, insufficient_evidence, etc.

This is where you learn how to encode governance in types, which is rare and valuable.

d) Query/response contracts
query_contracts.py:

QueryRequest, QueryClassification, NormalizedQuery.

response_contracts.py:

StructuredQueryResponse, GeneratedAnswer.

These tie the ontology to the API and UI.

Why this is deep + fast:

You’re not building 50 classes; you’re building 10–15 well-designed ones.

This depth is what you’ll talk about in interviews and posts:

“Here’s how I designed the ontology spine so every claim is traceable.”

2. Go shallow here (just enough for the demo)
These layers matter, but you don’t need to master them fully right now.

a) Retrieval
Stub or minimal implementation:

Hard-code a few evidence items for your controlled drug set.

Or implement a very simple “retrieve from a small JSON file” pattern.

Focus:

Show that retrieval plugs into the ontology (e.g., returns SourceDocument + Citation objects).

Don’t worry about:

sophisticated ranking

full DailyMed/PubMed integration yet

b) Generation
Use a simple LLM call:

Prompt: “Given this evidence bundle, produce a structured answer with claims.”

Don’t optimize for:

perfect prompt engineering

multi-turn strategies

advanced reasoning patterns

Focus:

Show that generation consumes your contracts and produces claims tied to sources.

c) Validation logic
Implement basic validators:

Citation presence check

Simple claim support check (e.g., “does the claim text appear in the cited chunk?”)

Don’t build:

full entailment models

complex multi-validator orchestration yet

Focus:

Demonstrate the pattern: claims → validators → ValidationResult.

d) Audit & persistence
In-memory or simple JSON file:

Store audit records as JSON lines.

Don’t worry about:

DB schema design

complex querying

Focus:

Show that every response has an audit_id and a full trace.

e) UI
One Streamlit page:

Input: query text

Output:

classification

normalized entities

2–3 evidence items

generated answer with claims

validation status

audit ID

Don’t build:

multi-page dashboards

fancy filters, search, etc.

Why this is deep + fast:

You’re learning the integration pattern, not mastering every component.

You can say: “Retrieval and generation are minimal by design; the depth is in the ontology and governance.”

==============================================
INTERVIEW/WRITING TIPS
===============================================

“I’m optimizing for both depth and speed. -> know where to go deep and where to stay lean to ship fast!!

Depth: I went deep on the ontology layer and Pydantic contracts so the system is governed and auditable by design.
Speed: I kept retrieval, generation, and the UI minimal so I could ship a working demo in a few weeks.

The result is a vertical slice that shows:

how an ontology-backed contract layer works

how claims are validated against evidence

how every response is auditable

I can now extend the retrieval and generation parts without changing the core governance model.”

==================================================
