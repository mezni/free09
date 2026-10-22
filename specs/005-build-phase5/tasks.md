# Tasks: build-phase5

**Input**: Design documents from `/home/dali/WORK/telco-si/specs/005-build-phase5/`
**Spec**: `specs/005-build-phase5/spec.md`
**Plan**: `specs/005-build-phase5/plan.md`
**Research**: `specs/005-build-phase5/research.md`
**Data model**: `specs/005-build-phase5/data-model.md`
**Contracts**: `specs/005-build-phase5/contracts/`
**Quickstart**: `specs/005-build-phase5/quickstart.md`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Included. The feature specification's Test Mapping names a planned test for every requirement, and Constitution Article VII.1 requires every acceptance criterion to map to a verifiable test.

**Organization**: Tasks are grouped by phase to enable independent implementation and testing of each phase.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

This is a **monorepo** of project setup and governance artifacts. Paths below
follow `specs/005-build-phase5/`:

- `specs/005-build-phase5/` — this feature's artefacts
- `contracts/` — interface contracts and alignment documents
- `docs/` — governance and design prose


**Status**: Implemented — 59 of 59 tasks complete.

> Completion markers reflect the state of the repository as of 2026-10-22 and
> were verified against the artifacts each task names. The OpenTelemetry SDK
> and OTLP/HTTP exporter are declared dependencies, all four services wire the
> tracing middleware, API key management and webhook validation are complete,
> and the benchmark harness compares the current metrics with the phase-3
> baseline.

---

## Phase 1: Setup (Shared Infrastructure)

- [x] T103 Create project structure per implementation plan
- [x] T104 Initialize project with dependencies per plan.md
- [x] T105 .python-version pinning to 3.13
- [x] T106 [P] Configure linting and formatting tools (ruff, black)
- [x] T107 [P] Configure code quality tools (mypy, pylint)
- [x] T108 [P] Declare the OpenTelemetry dependencies in `pyproject.toml` and verify `uv sync`
- [x] T109 [P] Create `services/auth-service/pyproject.toml`
- [x] T110 [P] Create `services/crm-service/pyproject.toml`
- [x] T111 [P] Create `services/billing-service/pyproject.toml`
- [x] T112 [P] Create `services/inventory-service/pyproject.toml`
- [x] T113 Extend `.gitignore` with the Phase 0 exclusions (Python/DB/Docker) and build-phase5 patterns
- [x] T114 Create `Makefile` as a thin alias layer over nox
- [x] T115 Generate `uv.lock` with `uv lock` and verify `uv sync` works

**Checkpoint**: Foundation ready — design tasks can now begin in parallel

## Phase 2: Foundational (Blocking Prerequisites)

**⚠️ CRITICAL**: No design work can begin until this phase is complete.

- [x] T116 Constitution reconciliation between docs/ and .specify/
- [x] T117 Ratify constitution with date and signatures
- [x] T118 Set spec.md status to Approved
- [x] T119 Implement configuration loader in config.py (pydantic-settings)
- [x] T120 Create .env.example with placeholder values (OTEL, ERROR, WEBHOOK, KEY)
- [x] T121 Implement session framework in noxfile.py (trace, key, webhook, benchmark, test)
- [x] T122 Create ci/run-checks.sh as single entry point (lint, validate, test, trace, key, webhook)
- [x] T123 Create tests/conftest.py with marker registration (trace, key, webhook, health, error)

**Checkpoint**: Foundation ready — design tasks can now begin in parallel

## Phase 3: Design & Contracts (API Contract Layer Advanced)

**This phase advances User Stories 1–5: Tracing, Error Tracking, Health Checks, API Key Management, Webhooks**

- [x] T124 [P] [US1] Design OpenTelemetry configuration across all services
- [x] T125 [P] [US1] Create test for OpenTelemetry baseline verification
- [x] T126 [P] [US1] Create test for language baseline unchanged
- [x] T127 [P] [US1] Create test for setup prerequisites
- [x] T128 [P] [US1] Design and configure Jaeger/OpenTelemetry collector
- [x] T129 [P] [US1] Implement distributed tracing middleware using OpenTelemetry
- [x] T130 [P] [US1] Integrate tracing into auth-service pipeline
- [x] T131 [P] [US1] Integrate tracing into crm-service pipeline
- [x] T132 [P] [US1] Integrate tracing into billing-service pipeline
- [x] T133 [P] [US1] Integrate tracing into inventory-service pipeline
- [x] T134 [P] [US1] Test OpenTelemetry end-to-end with an in-process span exporter
- [x] T135 [P] [US1] Run complete required check set and confirm PASS (trace)
- [x] T136 [P] [Shared] Reconcile constitution documents (docs/ vs .specify/)
- [x] T137 [P] [Shared] Record ADR-0001 final decision status
- [x] T138 [P] [Shared] Update traceability matrix with TM104–TM124
- [x] T139 [P] [Shared] Update requirements.md to implemented state
- [x] T140 [P] [Shared] Fresh clone verification (45 min)
- [x] T141 [P] [Shared] Set spec.md status to Implemented after acceptance evidence

**Checkpoint**: US1 complete — Distributed tracing operational across all services

## Phase 4: US2 — Centralized Error Tracking

- [x] T142 [P] [US2] Implement centralized error tracking system
- [x] T143 [P] [US2] Add integration tests for error tracking
- [x] T144 [P] [US2] Implement webhook validation and processing
- [x] T145 [P] [US2] Add API key management UI (CRUD)
- [x] T146 [P] [US2] Implement request/response logging middleware
- [x] T147 [P] [US1] Add the performance benchmark harness and phase-3 baseline comparison (FR-046)
- [x] T148 [P] [US3] Configure centralized error tracking
- [x] T149 [P] [US3] Implement health check endpoints
- [x] T150 [P] [US4] Add comprehensive documentation
- [x] T151 [P] [US4] Update traceability matrix for all stories
- [x] T152 [P] [Shared] Final fresh clone verification (45 min)
- [x] T153 [P] [Shared] Set all spec.md statuses to Implemented after acceptance evidence

**Checkpoint**: US2–US5 complete — Advanced features implemented, documentation complete

## Phase 7: Polish & Cross-Cutting Concerns

- [x] T154 [P] [Shared] Set spec.md status to Implemented
- [x] T155 [Shared] Run complete required check set and confirm PASS
- [x] T156 [P] [Shared] Reconcile constitution documents
- [x] T157 [P] [Shared] Record ADR-0001 final decision status
- [x] T158 [P] [Shared] Update traceability matrix
- [x] T159 [P] [Shared] Update requirements.md to implemented state
- [x] T160 [P] [Shared] Fresh clone verification (30 min)
- [x] T161 [Shared] Set spec.md status to Implemented after acceptance evidence

## Dependencies & Execution Order

- Phase 1 (T103–T115): Foundation — can run immediately
- Phase 2 (T116–T123): Blocking prerequisites — must complete before Phase 3
- Phase 3 (T124–T141): US1 — Distributed Tracing — depends on Phase 2 complete
- Phase 4 (T142–T153): US2–US5 — Advanced Features — depends on US1 complete
- Phase 7 (T154–T161): Polish — depends on all prior phases complete

## Parallel Execution Examples

### Parallel: Tracing SDK Generation (P tasks)
- T128: Configure Jaeger/OpenTelemetry collector (different file from T129)
- T129: Implement distributed tracing middleware using OpenTelemetry (different file, no Python dependency)
- Both can run concurrently on separate workers

### Parallel: Middleware Implementation (P tasks)
- T130: Integrate tracing into auth-service pipeline
- T131: Integrate tracing into crm-service pipeline
- T132: Integrate tracing into billing-service pipeline
- T133: Integrate tracing into inventory-service pipeline
- All four can run in parallel, each modifying different files

### Parallel: Checklist Updates (P tasks)
- T136–T139: Constitution reconciliation, ADR recording, traceability, requirements update
- All can run once US1 acceptance evidence is collected

### Parallel: SDK and API Key (P tasks)
- T144: Implement webhook validation and processing (different file from T145)
- T145: Add API key management UI (CRUD) (different file, no Python dependency)
- T146: Implement request/response logging middleware (different concern)
- T147: Add distributed tracing (OpenTelemetry) — repeat/supplement (different concern)
- T148: Configure centralized error tracking (different concern)
- T149: Implement health check endpoints (different concern)
- All five can run in parallel, each modifying different files
