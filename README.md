# Agentic QE

A small, working MVP that demonstrates how an agentic system can take approved
software requirements, retrieve project knowledge, design and prioritize
tests, prepare test data, execute approved tests, analyze evidence, re-plan
when needed, and produce an auditable report.

This is a **learning project** — not a production platform, and not merely an
LLM test-script generator.

## Architecture

- **LLM** — reasoning, interpretation, and recommendations.
- **RAG** — retrieval of approved project knowledge and evidence.
- **Rules Engine** — deterministic validation, governance, and boundaries.
- **Tools** — perform real actions and collect ground-truth evidence.
- **Agents** — coordinate specialized QE activities.
- **Memory** — state, history, and audit trail.
- **Human** — governance, ambiguity, exceptions, and controlled autonomy approval.

**Core principle:** LLM reasoning is never treated as ground-truth. Tool
results and collected evidence are the source of truth.

## Core Workflow

    PLAN -> EXECUTE -> OBSERVE -> ANALYZE -> RE-PLAN -> CONTINUE

## Controlled Autonomy

- **GREEN** — proceed autonomously within approved requirements, test cases,
  tools, and rules.
- **YELLOW** — human approval required for requirement ambiguity/conflicts,
  approved-baseline changes, security exceptions, significant scope changes,
  and other governance-sensitive decisions.
- **RED** — no destructive operations, unauthorized production changes,
  unauthorized security actions, or deletion of artifacts.

## Day-14 MVP Scope

A Customer Management API with: create, retrieve, update, customer
validation, country validation, response/status validation, response-time
validation, authentication/authorization, and error handling.

## Project Layout

- `agents/` — specialized QE agents (requirements, knowledge, test design,
  test data, automation, execution, evidence, RCA, re-planning, reporting).
- `tools/` — real-action tools (document reading, OpenAPI parsing, API calls,
  test running, filesystem).
- `rag/` — local document-based knowledge store and retriever.
- `rules/` — deterministic governance, validation, and prioritization rules.
- `memory/` — task state, execution state, evidence store, and history.
- `planner/` — plan construction and prioritization.
- `execution/` — test execution and scheduling.
- `evidence/` — evidence collection and validation.
- `reports/` — generated audit reports.
- `requirements/` — approved software requirements (baseline).
- `technical_docs/` — supporting technical documentation.
- `testcases/` — generated/approved test cases.
- `testdata/` — generated test data.
- `defects/` — recorded defects.
- `execution_history/` — preserved execution history.
- `approvals/` — human approval records.
- `tests/` — project test suite.

This repository currently contains only the initial project skeleton.
