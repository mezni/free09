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

T038] T001 Create project structure per implementation plan [COMPLETE T038] [COMPLETE 038]
T039] T002 Initialize project with dependencies per plan.md [COMPLETE T039] [COMPLETE 039]
T040] T003 .python-version pinning to 3.13 [COMPLETE T040] [COMPLETE 040]
T041] T004 [P] Configure linting and formatting tools (ruff, black) [COMPLETE T041] [COMPLETE 041]
T042] T005 [P] Configure code quality tools (mypy, pylint) [COMPLETE T042] [COMPLETE 042]
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

T051] T012 Constitution reconciliation between docs/ and .specify/ [COMPLETE T012] [COMPLETE 051]
T052] T013 Ratify constitution with date and signatures [COMPLETE 052]
T053] T014 Set spec.md status to Approved [COMPLETE 053]
T054] T015 Implement configuration loader in config.py (pydantic-settings) [COMPLETE 054]
T055] T016 Create .env.example with placeholder values (AUTH_PREFIX, RATE_LIMIT) [COMPLETE 055]
T056] T017 Implement session framework in noxfile.py (sdk-gen, validate, migrate, test) [COMPLETE 056]
T057] T018 Create ci/run-checks.sh as single entry point (lint, validate, test, sdk-gen) [COMPLETE 057]
T058] T019 Create tests/conftest.py with marker registration (us1, us2, us3, us4) [COMPLETE 058]
T059] T020 Create minimal test suite that passes on empty impl (TM031–TM035) [COMPLETE 059]

**Checkpoint**: Foundation ready — design tasks can now begin in parallel

## Phase 3: Design & Contracts (API Contract Layer)

**This phase implements User Story 1: API Contract Layer**

T061] T021 [P] [US1] Design OpenAPI 3.1 specification for person-management API [COMPLETE T061]
T062] T022 [P] [US1] [P] [US1] Create test for fresh clone setup verification [COMPLETE T062]
T063] T023 [P] [US1] [P] [US1] Create test for language baseline unchanged [COMPLETE T063]
T064] T024 [P] [US1] [P] [US1] Create test for setup prerequisites [COMPLETE T064]
T065] T025 [P] [US1] Design and generate Python SDK from OpenAPI spec [COMPLETE T065]
T066] T026 [P] [US1] Design and generate TypeScript SDK from OpenAPI spec [COMPLETE T066]
T067] T027 [P] [US1] Implement request validation middleware using Pydantic [COMPLETE T067]
T068] T028 [P] [US1] Implement response transformation to canonical format [COMPLETE T068]
T069] T029 [P] [US1] Configure API gateway (Traefik) rate limiting per endpoint [COMPLETE T069]
T070] T030 [P] [US1] Implement OAuth2.1 authentication middleware [COMPLETE T070]
T071] T031 [P] [US1] Integrate all middleware into auth-service pipeline [COMPLETE T071]
T072] T032 [P] [US1] Test fresh clone setup end-to-end (30 min verification) [COMPLETE T072]
T073] T033 [P] [US1] Run complete required check set and confirm PASS [COMPLETE T073]
T074] T034 [P] [Shared] Reconcile constitution documents (docs/ vs .specify/) [COMPLETE T074]
T075] T035 [P] [Shared] Record ADR-0001 final decision status [COMPLETE T075]
T076] T036 [P] [Shared] Update traceability matrix with TM031–TM053 [COMPLETE T076]
T077] T037 [P] [Shared] Update requirements.md to implemented state [COMPLETE T077]
T078] T038 [P] [Shared] Fresh clone verification (30 min) [COMPLETE T078]
T079] T039 [P] [Shared] Set spec.md status to Implemented after acceptance evidence [COMPLETE T079]

**Checkpoint**: US1 complete — API contract layer operational, SDKs generated, middleware active

## Phase 4: US2 — SDK Generation & Advanced Features

T080] T040 [P] [US2] Generate Python SDK v2 with advanced models [COMPLETE T080]
T081] T041 [P] [US2] Generate TypeScript SDK v2 with axios interceptors [COMPLETE T081] [COMPLETE T081]
T082] T042 [P] [US2] Add integration tests for SDK methods [COMPLETE T082] [COMPLETE T082]
T083] T043 [P] [US2] Implement webhook validation and processing [COMPLETE T083] [COMPLETE T083]
T084] T044 [P] [US2] Add API key management UI (CRUD) [COMPLETE T084] [COMPLETE T084]
T085] T045 [P] [US2] Implement request/response logging middleware [COMPLETE T085] [COMPLETE T085]
T086] T046 [P] [US3] [P] [US3] Add distributed tracing (OpenTelemetry) [COMPLETE T086] [COMPLETE T086]
T087] T047 [P] [US3] [P] [US3] Configure centralized error tracking [COMPLETE T087] [COMPLETE T087]
T088] T048 [P] [US3] [P] [US3] Implement health check endpoints [COMPLETE T088] [COMPLETE T088]
T089] T049 [P] [US4] [P] [US4] Add comprehensive documentation [COMPLETE T089] [COMPLETE T089]
T090] T050 [P] [US4] [P] [US4] Update traceability matrix for all stories [COMPLETE T090]
T091] T051 [P] [Shared] Final fresh clone verification (45 min) [COMPLETE T091] [COMPLETE T091]
T092] T052 [Shared] Set all spec.md statuses to Implemented after acceptance evidence [COMPLETE T092]

**Checkpoint**: US2–US4 complete — advanced features implemented, documentation complete

## Phase 7: Polish & Cross-Cutting Concerns

T093] T095 [P] [P] [ Shared ] Set spec.md status to Implemented [COMPLETE T093]
T094] T096 [ Shared ] Run complete required check set and confirm PASS [COMPLETE T094]
T095] T097 [P] [Shared] [P] [ Shared ] Reconcile constitution documents [COMPLETE T095]
T096] T098 [P] [Shared] [P] [ Shared ] Record ADR-0001 final decision status [COMPLETE T096]
T097] T099 [P] [Shared] [P] [ Shared ] Update traceability matrix [COMPLETE T097]
T098] T100 [P] [Shared] [P] [ Shared ] Update requirements.md to implemented state [COMPLETE T098]
T099] T101 [P] [Shared] [P] [ Shared ] Fresh clone verification (30 min) [COMPLETE T099]
T100] T102 [ Shared ] Set spec.md status to Implemented after acceptance evidence [COMPLETE T100]

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
