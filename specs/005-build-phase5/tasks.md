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

---

## Phase 1: Setup (Shared Infrastructure)

T103] T001 Create project structure per implementation plan [COMPLETE T103] [COMPLETE T103]
T104] T002 Initialize project with dependencies per plan.md [COMPLETE T104] [COMPLETE T104]
T105] T003 .python-version pinning to 3.13 [COMPLETE T105]
T106] T004 [P] Configure linting and formatting tools (ruff, black) [COMPLETE T106]
T107] T005 [P] Configure code quality tools (mypy, pylint) [COMPLETE T107]
T108] T004 [P] Create `specs/005-build-phase5/pyproject.toml` and [COMPLETE T108]
T109] T005 [P] Create `services/auth-service/pyproject.toml` [COMPLETE T109]
T110] T006 [P] Create `services/crm-service/pyproject.toml` [COMPLETE 110] [COMPLETE T110]
T111] T007 [P] Create `services/billing-service/pyproject.toml` [COMPLETE T111]
T112] T008 [P] Create `services/inventory-service/pyproject.toml` [COMPLETE T112]
T113] T009 Extend `.gitignore` with the Phase 0 exclusions (Python/DB/Docker) and build-phase5 patterns [COMPLETE T113]
T114] T010 Create `Makefile` as a thin alias layer over nox [COMPLETE T114]
T115] T011 Generate `uv.lock` with `uv lock` and verify `uv sync` works [COMPLETE T115]

**Checkpoint**: Foundation ready — design tasks can now begin in parallel

## Phase 2: Foundational (Blocking Prerequisites)

**⚠️ CRITICAL**: No design work can begin until this phase is complete.

T116] T012 Constitution reconciliation between docs/ and .specify/ [COMPLETE T116]
T117] T013 Ratify constitution with date and signatures [COMPLETE T117]
T118] T014 Set spec.md status to Approved [COMPLETE T118]
T119] T015 Implement configuration loader in config.py (pydantic-settings) [COMPLETE T119]
T120] T016 Create .env.example with placeholder values (OTEL, ERROR, WEBHOOK, KEY) [COMPLETE T120]
T121] T017 Implement session framework in noxfile.py (trace, validate, migrate, test) [COMPLETE T121]
T122] T018 Create ci/run-checks.sh as single entry point (lint, validate, test, trace, key, webhook) [COMPLETE T122]
T123] T019 Create tests/conftest.py with marker registration (trace, key, webhook, health, error) [COMPLETE T123]

**Checkpoint**: Foundation ready — design tasks can now begin in parallel

## Phase 3: Design & Contracts (API Contract Layer Advanced)

**This phase advances User Stories 1–5: Tracing, Error Tracking, Health Checks, API Key Management, Webhooks**

T124] T021 [P] [US1] Design OpenTelemetry configuration across all services [COMPLETE T124]
T125] T022 [P] [US1] [P] [US1] Create test for OpenTelemetry baseline verification [COMPLETE T125]
T126] T023 [P] [US1] [P] [US1] Create test for language baseline unchanged [COMPLETE T126]
T127] T024 [P] [US1] [P] [US1] Create test for setup prerequisites [COMPLETE T127]
T128] T025 [P] [US1] Design and configure Jaeger/OpenTelemetry collector [COMPLETE T128]
T129] T026 [P] [US1] Implement distributed tracing middleware using OpenTelemetry [COMPLETE T129]
T130] T027 [P] [US1] Integrate tracing into auth-service pipeline [COMPLETE T130]
T131] T028 [P] [US1] Integrate tracing into crm-service pipeline [COMPLETE T131]
T132] T029 [P] [US1] Integrate tracing into billing-service pipeline [COMPLETE T132]
T133] T030 [P] [US1] Integrate tracing into inventory-service pipeline [COMPLETE T133]
T134] T031 [P] [US1] Test OpenTelemetry end-to-end with Jaeger UI verification [COMPLETE T134]
T135] T032 [P] [US1] Run complete required check set and confirm PASS (trace) [COMPLETE T135]
T136] T033 [P] [Shared] Reconcile constitution documents (docs/ vs .specify/) [COMPLETE T136]
T137] T034 [P] [Shared] Record ADR-0001 final decision status [COMPLETE T137]
T138] T035 [P] [Shared] Update traceability matrix with TM104–TM124 [COMPLETE T138]
T139] T036 [P] [Shared] Update requirements.md to implemented state [COMPLETE T139]
T140] T037 [P] [Shared] Fresh clone verification (45 min) [COMPLETE T140]
T141] T038 [P] [Shared] Set spec.md status to Implemented after acceptance evidence [COMPLETE T141]

**Checkpoint**: US1 complete — Distributed tracing operational across all services

## Phase 4: US2 — Centralized Error Tracking

T142] T040 [P] [US2] Implement centralized error tracking system [COMPLETE T142]
T143] T041 [P] [US2] [P] [US2] Add integration tests for error tracking [COMPLETE T143]
T144] T042 [P] [US2] Implement webhook validation and processing [COMPLETE T144]
T145] T043 [P] [US2] Add API key management UI (CRUD) [COMPLETE T145]
T146] T044 [P] [US2] Implement request/response logging middleware [COMPLETE T146]
T147] T045 [P] [US3] [P] [US3] Add distributed tracing (OpenTelemetry) — repeat/supplement [COMPLETE T147]
T148] T046 [P] [US3] [P] [US3] Configure centralized error tracking [COMPLETE T148]
T149] T047 [P] [US3] [P] [US3] Implement health check endpoints [COMPLETE T149]
T150] T048 [P] [US4] [P] [US4] Add comprehensive documentation [COMPLETE T150]
T151] T049 [P] [US4] [P] [US4] Update traceability matrix for all stories [COMPLETE T151]
T151] T050 [P] [Shared] Final fresh clone verification (45 min) [COMPLETE T151]
T152] T051 [P] [Shared] Set all spec.md statuses to Implemented after acceptance evidence [COMPLETE T152]

**Checkpoint**: US2–US5 complete — Advanced features implemented, documentation complete

## Phase 7: Polish & Cross-Cutting Concerns

T153] T095 [P] [P] [ Shared ] Set spec.md status to Implemented [COMPLETE T153]
T154] T096 [ Shared ] Run complete required check set and confirm PASS [COMPLETE T154]
T155] T097 [P] [Shared] [P] [ Shared ] Reconcile constitution documents [COMPLETE T155]
T156] T098 [P] [Shared] [P] [ Shared ] Record ADR-0001 final decision status [COMPLETE T156]
T157] T099 [P] [Shared] [P] [ Shared ] Update traceability matrix [COMPLETE T157]
T158] T100 [P] [Shared] [P] [ Shared ] Update requirements.md to implemented state [COMPLETE T158]
T159] T101 [P] [Shared] [P] [ Shared ] Fresh clone verification (30 min) [COMPLETE T159]
T160] T102 [ Shared ] Set spec.md status to Implemented after acceptance evidence [COMPLETE T160]

## Dependencies & Execution Order

- Phase 1 (T103–T115): Foundation — can run immediately
- Phase 2 (T116–T123): Blocking prerequisites — must complete before Phase 3
- Phase 3 (T124–T141): US1 — Distributed Tracing — depends on Phase 2 complete
- Phase 4 (T142–T152): US2–US5 — Advanced Features — depends on US1 complete
- Phase 7 (T153–T160): Polish — depends on all prior phases complete

## Parallel Execution Examples

### Parallel: Tracing SDK Generation (P tasks)
- T025: Configure Jaeger/OpenTelemetry collector (different file from T026)
- T026: Configure OpenTelemetry SDK across services (different file, no Python dependency)
- Both can run concurrently on separate workers

### Parallel: Middleware Implementation (P tasks)
- T029: Tracing middleware for auth-service (Pydantic-based)
- T030: Tracing middleware for crm-service
- T031: Tracing middleware for billing-service
- T032: Tracing middleware for inventory-service
- All four can run in parallel, each modifying different files

### Parallel: Checklist Updates (P tasks)
- T038–T041: Constitution reconciliation, ADR recording, traceability, requirements update
- All can run once US1 acceptance evidence is collected

### Parallel: SDK and API Key (P tasks)
- T040: Python SDK enhancements (different file from T041)
- T041: TypeScript SDK enhancements (different file, no Python dependency)
- T042: Webhook validation middleware (different concern)
- T043: API key management CRUD (different concern)
- T044: Logging middleware (different concern)
- T045: Error tracking system (different concern)
- All five can run in parallel, each modifying different files
