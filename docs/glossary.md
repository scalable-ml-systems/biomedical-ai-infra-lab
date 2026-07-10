# Glossary

## GraphRAG

GraphRAG combines text retrieval with graph-based relationship lookup.

In this project, vector search helps find relevant biomedical text, while graph lookup helps validate relationships between drugs, label sections, warnings, contraindications, adverse reactions, and literature evidence.

## Evidence contract

An evidence contract is a structured record that connects a generated claim to the source evidence that supports it.

The goal is to avoid returning unsupported biomedical claims.

## Claim validation

Claim validation checks whether a generated claim is supported by retrieved evidence.

## Graph consistency validation

Graph consistency validation checks whether a generated relationship is consistent with known graph relationships.

## Safety policy

A safety policy blocks or redirects unsafe requests, especially personal medical-advice questions.

## Audit log

An audit log records the query, retrieved evidence, generated answer, validation results, safety result, and final response.
