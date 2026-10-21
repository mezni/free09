# Tasks: build-phase3

**Input**: Design documents from `/home/dali/WORK/telco-si/specs/004-build-phase3/`
**Spec**: `specs/004-build-phase3/spec.md`
**Plan**: `specs/004-build-phase3/plan.md`
**Research**: `specs/004-build-phase3/research.md`
**Data model**: `specs/004-build-phase3/data-model.md`
**Contracts**: `specs/004-build-phase3/contracts/`
**Quickstart**: `specs/004-build-phase3/quickstart.md`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Included. The feature specification's Test Mapping names a planned test for every requirement, FR-030 requires an OpenAPI-validated spec, and Constitution Article VII.1 requires every acceptance criterion to map to a verifiable test.

**Organization**: Tasks are grouped by phase to enable independent implementation and testing of each phase.

⚠️ Blocking gate: Constitution Article I.1 permits implementation only against an **approved** specification. T012, T013, and T014 complete that precondition and MUST complete before any other task in this list begins.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

This is a **monorepo** of project setup and governance artifacts. Paths below
follow `specs/004-build-phase3/`:

- `specs/004-build-phase3/` — this feature's artefacts
- `contracts/` — interface contracts and alignment documents
- `docs/` — governance and design prose

---

## Phase 1: Setup (Shared Infrastructure)

- [x] T038 Create project structure per implementation plan
- [x] T039 Initialize project with dependencies per plan.md
- [x] T040 .python-version pinning to 3.13
- [x] T041 [P] Configure linting and formatting tools (ruff, black)
- [x] T042 [P] Configure code quality tools (mypy, pylint)
T043]  T004 [P] Create `specs/004-build-phase3/pyproject.toml` and [COMPLETE T043] [COMPLETE 043]
T044]  T005 [P] Create `services/auth-service/pyproject.toml` [COMPLETE T044] [COMPLETE 044]
T045]  T006 [P] Create `services/crm-service/pyproject.toml` [COMPLETE T045] [COMPLETE 045]
T046]  T007 [P] Create `services/billing-service/pyproject.toml` [COMPLETE T046] [COMPLETE 046]
T047]  T008 [P] Create `services/inventory-service/pyproject.toml` [COMPLETE T047] [COMPLETE 047]
T048]  T009 Extend `.gitignore` with the Phase 0 exclusions (Python/DB/Docker) [COMPLETE T048] [COMPLETE 048]
T049]  T010 Create `Makefile` as a thin alias layer over nox [COMPLETE T049] [COMPLETE 049]
T050]  T011 Generate `uv.lock` with `uv lock` and verify `uv sync` works [COMPLETE T050] [COMPLETE 050]

**Checkpoint**: Foundation ready — design tasks can now begin in parallel

## Phase 2: Foundational (Blocking Prerequisites)

**⚠️ CRITICAL**: No design work can begin until this phase is complete.

- [x] T051 Constitution reconciliation between docs/ and .specify/
- [x] T052 Ratify constitution with date and signatures
- [x] T053 Set spec.md status to Approved
- [x] T054 Implement configuration loader in config.py (pydantic-settings)
- [x] T055 Create .env.example with placeholder values (AUTH_PREFIX, RATE_LIMIT)
- [x] T056 Implement session framework in noxfile.py (sdk-gen, validate, migrate, test)
- [x] T057 Create ci/run-checks.sh as single entry point (lint, validate, test, sdk-gen)
- [x] T058 Create tests/conftest.py with marker registration (us1, us2, us3, us4)
- [x] T059 Create minimal test suite that passes on empty impl (TM031–TM035)

**Checkpoint**: Foundation ready — design tasks can now begin in parallel

## Phase 3: Design & Contracts (API Contract Layer)

**This phase implements User Story 1: API Contract Layer**

- [x] T061 [P] [US1] Design OpenAPI 3.1 specification for person-management API
- [x] T062 [P] [US1] Create test for fresh clone setup verification
- [x] T063 [P] [US1] Create test for language baseline unchanged
- [x] T064 [P] [US1] Create test for setup prerequisites
- [x] T065 [P] [US1] Design and generate Python SDK from OpenAPI spec
- [x] T066 [P] [US1] Design and generate TypeScript SDK from OpenAPI spec
- [x] T067 [P] [US1] Implement request validation middleware using Pydantic
- [x] T068 [P] [US1] Implement response transformation to canonical format
- [x] T069 [P] [US1] Configure API gateway (Traefik) rate limiting per endpoint
- [x] T070 [P] [US1] Implement OAuth2.1 authentication middleware
- [x] T071 [P] [US1] Integrate all middleware into auth-service pipeline
- [x] T072 [P] [US1] Test fresh clone setup end-to-end (30 min verification)
- [x] T073 [P] [US1] Run complete required check set and confirm PASS
- [x] T074 [P] [Shared] Reconcile constitution documents (docs/ vs .specify/)
- [x] T075 [P] [Shared] Record ADR-0001 final decision status
- [x] T076 [P] [Shared] Update traceability matrix with TM031–TM053
- [x] T077 [P] [Shared] Update requirements.md to implemented state
- [x] T078 [P] [Shared] Fresh clone verification (30 min)
- [x] T079 [P] [Shared] Set spec.md status to Implemented after acceptance evidence

**Checkpoint**: US1 complete — API contract layer operational, SDKs generated, middleware active

## Phase 4: US2 — SDK Generation & Advanced Features

- [x] T080 [P] [US2] Generate Python SDK v2 with advanced models
- [x] T081 [P] [US2] Generate TypeScript SDK v2 with axios interceptors
- [x] T082 [P] [US2] Add integration tests for SDK methods
- [x] T083 [P] [US2] Implement webhook validation and processing
- [x] T084 [P] [US2] Add API key management UI (CRUD)
- [x] T085 [P] [US2] Implement request/response logging middleware
- [x] T086 [P] [US3] Add distributed tracing (OpenTelemetry)
- [x] T087 [P] [US3] Configure centralized error tracking
- [x] T088 [P] [US3] Implement health check endpoints
- [x] T089 [P] [US4] Add comprehensive documentation
- [x] T090 [P] [US4] Update traceability matrix for all stories
- [x] T091 [P] [Shared] Final fresh clone verification (45 min)
- [x] T092 [Shared] Set all spec.md statuses to Implemented after acceptance evidence

**Checkpoint**: US2–US4 complete — advanced features implemented, documentation complete

## Phase 7: Polish & Cross-Cutting Concerns

- [x] T093 [P] [Shared] Set spec.md status to Implemented
- [x] T094 [Shared] Run complete required check set and confirm PASS
- [x] T095 [P] [Shared] Reconcile constitution documents
- [x] T096 [P] [Shared] Record ADR-0001 final decision status
- [x] T097 [P] [Shared] Update traceability matrix
- [x] T098 [P] [Shared] Update requirements.md to implemented state
- [x] T099 [P] [Shared] Fresh clone verification (30 min)
- [x] T100 [Shared] Set spec.md status to Implemented after acceptance evidence

## Dependencies & Execution Order

- Phase 1 (T038–T050): Foundation — can run immediately
- Phase 2 (T051–T059): Blocking prerequisites — must complete before Phase 3
- Phase 3 (T061–T039): US1 — API Contract Layer — depends on Phase 2 complete
- Phase 4 (T080–T052): US2–US4 — depends on US1 complete
- Phase 7 (T093–T102): Polish — depends on all prior phases complete

## Parallel Execution Examples

### Parallel: SDK Generation (P tasks)
- T025: Generate Python SDK (different file from T026)
- T026: Generate TypeScript SDK (different file, no Python dependency)
- Both can run concurrently on separate workers

### Parallel: Middleware Implementation (P tasks)
- T027: Request validation middleware (Pydantic-based)
- T028: Response transformation (canonical format)
- T029: API gateway rate limiting (Traefik config)
- T030: OAuth2.1 auth middleware (different concern)
- All four can run in parallel, each modifying different files

### Parallel: Checklist Updates (P tasks)
- T034–T039: Constitution reconciliation, ADR recording, traceability, requirements update
- All can run once US1 acceptance evidence is collected
