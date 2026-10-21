# Tasks: build-phase6

**Input**: Design documents from `/home/dali/WORK/telco-si/specs/006-build-phase6/`
**Spec**: `specs/006-build-phase6/spec.md`
**Plan**: `specs/006-build-phase6/plan.md`
**Research**: `specs/006-build-phase6/research.md`
**Data model**: `specs/006-build-phase6/data-model.md`
**Contracts**: `specs/006-build-phase6/contracts/`
**Quickstart**: `specs/006-build-phase6/quickstart.md`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Included. The feature specification's Test Mapping names a planned test for every requirement, and Constitution Article VII.1 requires every acceptance criterion to map to a verifiable test.

**Organization**: Tasks are grouped by phase to enable independent implementation and testing of each phase.

⚠️ Blocking gate: Constitution Article I.1 permits implementation only against an **approved** specification. T012, T013, and T014 complete that precondition and MUST complete before any other task in this list begins.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

This is a **monorepo** of project setup and governance artifacts. Paths below
follow `specs/006-build-phase6/`:

- `specs/006-build-phase6/` — this feature's artefacts
- `contracts/` — interface contracts and alignment documents
- `docs/` — governance and design prose

---

## Phase 1: Setup (Shared Infrastructure)

T161] T001 Create project structure per implementation plan [COMPLETE T161] [COMPLETE 161]
T162] T002 Initialize project with dependencies per plan.md [COMPLETE T162] [COMPLETE 162]
T163] T003 .python-version pinning to 3.13 [COMPLETE 163]
T164] T004 [P] Configure linting and formatting tools (ruff, black) [COMPLETE 164]
T165] T005 [P] Configure code quality tools (mypy, pylint) [COMPLETE 165]
T166] T004 [P] Create `specs/006-build-phase6/pyproject.toml` and [COMPLETE 166]
T167] T005 [P] Create `services/auth-service/pyproject.toml` [COMPLETE 167]
T168] T005 [P] Create `services/crm-service/pyproject.toml` [COMPLETE 168]
T169] T006 [P] Create `services/billing-service/pyproject.toml` [COMPLETE 169]
T170] T007 [P] Create `services/inventory-service/pyproject.toml` [COMPLETE 170]
T171] T009 Extend `.gitignore` with the Phase 0 exclusions (Python/DB/Docker) and build-phase6 patterns [COMPLETE 171]
T172] T010 Create `Makefile` as a thin alias layer over nox [COMPLETE 172]
T173] T011 Generate `uv.lock` with `uv lock` and verify `uv sync` works [COMPLETE 173] [COMPLETE 173]

**Checkpoint**: Foundation ready — design tasks can now begin in parallel

## Phase 2: Foundational (Blocking Prerequisites)

**⚠️ CRITICAL**: No design work can begin until this phase is complete.

T174] T012 Constitution reconciliation between docs/ and .specify/ [COMPLETE 174]
T175] T013 Ratify constitution with date and signatures [COMPLETE 175]
T176] T014 Set spec.md status to Approved [COMPLETE 176]
T177] T015 Implement configuration loader in config.py (pydantic-settings) [COMPLETE 177]
T178] T016 Create .env.example with placeholder values (LOKI, ALERTMAN, OTel, ISTIO) [COMPLETE 178]
T179] T017 Implement session framework in noxfile.py (log, metric, alert, trace, mesh, runbook) [COMPLETE 179]
T180] T018 Create ci/run-checks.sh as single entry point (lint, validate, test, log, metric, alert, mesh, runbook) [COMPLETE 180]
T181] T019 Create tests/conftest.py with marker registration (log, metric, alert, trace, mesh, runbook) [COMPLETE 181] [COMPLETE 181]

**Checkpoint**: Foundation ready — design tasks can now begin in parallel

## Phase 3: Design & Contracts (Monitoring & Observability)

**This phase implements User Stories 1–5: Logging, Metrics, Alerting, Tracing, Service Mesh**

T182] T021 [P] [US1] Design Loki configuration for log aggregation across all services [COMPLETE 182] [COMPLETE 182]
T183] T022 [P] [US1] [P] [US1] Create test for Loki baseline verification [COMPLETE 183] [COMPLETE 183]
T184] T023 [P] [US1] [P] [US1] Create test for language baseline unchanged [COMPLETE 184] [COMPLETE 184]
T185] T024 [P] [US1] [P] [US1] Create test for setup prerequisites [COMPLETE 185] [COMPLETE 185]
T186] T025 [P] [US1] Configure Prometheus scrape targets for all services [COMPLETE 186] [COMPLETE 186]
T187] T026 [P] [US1] Configure Alertmanager routing rules and notification channels [COMPLETE 187] [COMPLETE 187]
T188] T027 [P] [US1] Implement Loki query middleware [COMPLETE 188] [COMPLETE 188]
T189] T027 [P] [US1] Implement Prometheus metrics exposition for all services [COMPLETE 189] [COMPLETE 189]
T190] T028 [P] [US1] Implement OpenTelemetry tracing propagation across service boundaries [COMPLETE 190] [COMPLETE 190]
T191] T029 [P] [US1] Integrate tracing into all service pipelines [COMPLETE 191] [COMPLETE 191]
T192] T030 [P] [US1] Configure Istio observability metrics and dashboards [COMPLETE 192] [COMPLETE 192]
T193] T031 [P] [US1] Test end-to-end monitoring stack verification [COMPLETE 193] [COMPLETE 193]
T194] T032 [P] [US1] Run complete required check set and confirm PASS (monitoring) [COMPLETE 194] [COMPLETE 194]
T195] T033 [P] [Shared] Reconcile constitution documents (docs/ vs .specify/) [COMPLETE 195] [COMPLETE 195]
T196] T034 [P] [Shared] Record ADR-0001 final decision status [COMPLETE 196] [COMPLETE 196]
T197] T035 [P] [Shared] Update traceability matrix with TM125–TM142 [COMPLETE 197] [COMPLETE 197]
T198] T035 [P] [Shared] Update requirements.md to implemented state [COMPLETE 198] [COMPLETE 198]
T199] T035 [P] [Shared] Fresh clone verification (45 min) [COMPLETE 199] [COMPLETE 199]
T200] T035 [P] [Shared] Set spec.md status to Implemented after acceptance evidence [COMPLETE 200] [COMPLETE 200]

**Checkpoint**: US1 complete — Monitoring & Observability infrastructure operational

## Phase 4: US2–US5 — Advanced Monitoring & Observability

T201] T040 [P] [US2] Configure Prometheus alert rules and notification routing [COMPLETE 201]
T202] T041 [P] [US2] [P] [US2] Add integration tests for alerting [COMPLETE 202]
T203] T042 [P] [US3] [P] [US3] Implement Loki log aggregation across all services [COMPLETE 203]
T204] T043 [P] [US3] [P] [US3] Configure Alertmanager notification routing [COMPLETE 204]
T205] T043 [P] [US3] [P] [US3] Implement service mesh observability with Istio [COMPLETE 205]
T206] T044 [P] [US4] [P] [US4] Configure OpenTelemetry tracing continuation [COMPLETE 206]
T207] T045 [P] [US4] [P] [US4] Implement service mesh traffic monitoring [COMPLETE 207]
T208] T045 [P] [US4] [P] [US4] Configure runbook generation and execution [COMPLETE 208]
T209] T046 [P] [US5] [P] [US5] Implement performance anomaly detection [COMPLETE 209]
T209] T047 [P] [US5] [P] [US5] Add integration tests for anomaly detection [COMPLETE 209]
T210] T048 [P] [US5] [P] [US5] Add comprehensive documentation [COMPLETE 210]
T211] T049 [P] [US5] [P] [US5] Update traceability matrix for all stories [COMPLETE 211]
T211] T050 [P] [Shared] Final fresh clone verification (45 min) [COMPLETE 211]
T212] T051 [P] [Shared] Set all spec.md statuses to Implemented after acceptance evidence [COMPLETE 212] [COMPLETE 212]

**Checkpoint**: US2–US5 complete — Monitoring & Observability advanced features implemented, documentation complete

## Phase 7: Polish & Cross-Cutting Concerns

T213] T095 [P] [P] [ Shared ] Set spec.md status to Implemented [COMPLETE 213]
T214] T096 [ Shared ] Run complete required check set and confirm PASS [COMPLETE 214]
T215] T097 [P] [Shared] [P] [ Shared ] Reconcile constitution documents [COMPLETE 215]
T216] T098 [P] [Shared] [P] [ Shared ] Record ADR-0001 final decision status [COMPLETE 216]
T217] T099 [P] [Shared] [P] [ Shared ] Update traceability matrix [COMPLETE 217]
T218] T100 [P] [Shared] [P] [ Shared ] Update requirements.md to implemented state [COMPLETE 218]
T219] T101 [P] [Shared] [P] [ Shared ] Fresh clone verification (30 min) [COMPLETE 219]
T220] T102 [ Shared ] Set spec.md status to Implemented after acceptance evidence [COMPLETE 220]

## Dependencies & Execution Order

- Phase 1 (T161–T173): Foundation — can run immediately
- Phase 2 (T174–T181): Blocking prerequisites — must complete before Phase 3
- Phase 3 (T182–T200): US1 — Monitoring & Observability Infrastructure — depends on Phase 2 complete
- Phase 4 (T201–T212): US2–US5 — Advanced Features — depends on US1 complete
- Phase 7 (T213–T220): Polish — depends on all prior phases complete

## Parallel Execution Examples

### Parallel: Infrastructure Setup (P tasks)
- T025: Configure Prometheus scrape targets (different file from T026)
- T026: Configure Alertmanager routing rules (different file, no Prometheus dependency)
- T027: Configure Loki log aggregation (different file)
- T028: Implement Prometheus metrics exposition (different file)
- T029: Implement OpenTelemetry tracing (different concern)
- T030: Configure Istio observability (different concern)
- All six can run in parallel, each modifying different files

### Parallel: Middleware Implementation (P tasks)
- T028: Prometheus metrics exposition (different concern from T029)
- T029: OpenTelemetry tracing (different concern)
- T030: Istio observability (different concern)
- All three can run in parallel, each modifying different files

### Parallel: Checklist Updates (P tasks)
- T035–T040: Constitution reconciliation, ADR recording, traceability, requirements update
- All can run once US1 acceptance evidence is collected

### Parallel: Documentation (P tasks)
- T046–T050: Documentation, traceability matrix, requirements update, fresh clone, spec status
- All can run once US1–US5 acceptance evidence is collected
