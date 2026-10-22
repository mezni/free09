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

⚠️ Blocking gate: Constitution Article I.1 permits implementation only against an **approved** specification. T13, T14, and T15 complete that precondition and MUST complete before any other task in this list begins.

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


**Status**: Implemented — all 62 tasks complete.

> Completion markers reflect the state of the repository as of 2026-10-22 and
> were verified against the artifacts each task names. The monitoring stack
> (Loki, Prometheus, Alertmanager, Grafana, Istio), middleware, API surface,
> nox sessions and pytest markers are present and covered by the phase-6
> contract tests. The phase status in `spec.md` is **Implemented**.

---

## Phase 1: Setup (Shared Infrastructure)

- [x] T162 Create project structure per implementation plan
- [x] T163 Initialize project with dependencies per plan.md
- [x] T164 .python-version pinning to 3.13
- [x] T165 [P] Configure linting and formatting tools (ruff, black)
- [x] T166 [P] Configure code quality tools (mypy, pylint)
- [x] T167 [P] Create `specs/006-build-phase6/pyproject.toml` and
- [x] T168 [P] Create `services/auth-service/pyproject.toml`
- [x] T169 [P] Create `services/crm-service/pyproject.toml`
- [x] T170 [P] Create `services/billing-service/pyproject.toml`
- [x] T171 [P] Create `services/inventory-service/pyproject.toml`
- [x] T172 Extend `.gitignore` with the Phase 0 exclusions (Python/DB/Docker) and build-phase6 patterns
- [x] T173 Create `Makefile` as a thin alias layer over nox
- [x] T174 Generate `uv.lock` with `uv lock` and verify `uv sync` works

**Checkpoint**: Foundation ready — design tasks can now begin in parallel

## Phase 2: Foundational (Blocking Prerequisites)

**⚠️ CRITICAL**: No design work can begin until this phase is complete.

- [x] T175 Constitution reconciliation between docs/ and .specify/
- [x] T176 Ratify constitution with date and signatures
- [x] T177 Set spec.md status to Approved
- [x] T178 Implement configuration loader in config.py (pydantic-settings)
- [x] T179 Create .env.example with placeholder values (LOKI, ALERTMAN, OTel, ISTIO)
- [x] T180 Implement session framework in noxfile.py (log, metric, alert, trace, mesh, runbook)
- [x] T181 Create ci/run-checks.sh as single entry point (lint, validate, test, log, metric, alert, mesh, runbook)
- [x] T182 Create tests/conftest.py with marker registration (log, metric, alert, trace, mesh, runbook)

**Checkpoint**: Foundation ready — design tasks can now begin in parallel

## Phase 3: Design & Contracts (Monitoring & Observability)

**This phase implements User Stories 1–5: Logging, Metrics, Alerting, Tracing, Service Mesh**

- [x] T183 [P] [US1] Design Loki configuration for log aggregation across all services
- [x] T184 [P] [US1] Create test for Loki baseline verification
- [x] T185 [P] [US1] Create test for language baseline unchanged
- [x] T186 [P] [US1] Create test for setup prerequisites
- [x] T187 [P] [US1] Configure Prometheus scrape targets for all services
- [x] T188 [P] [US1] Configure Alertmanager routing rules and notification channels
- [x] T189 [P] [US1] Implement Loki query middleware
- [x] T190 [P] [US1] Implement Prometheus metrics exposition for all services
- [x] T191 [P] [US1] Implement OpenTelemetry tracing propagation across service boundaries
- [x] T192 [P] [US1] Integrate tracing into all service pipelines
- [x] T193 [P] [US1] Configure Istio observability metrics and dashboards
- [x] T194 [P] [US1] Test end-to-end monitoring stack verification
- [x] T195 [P] [US1] Run complete required check set and confirm PASS (monitoring)
- [x] T196 [P] [Shared] Reconcile constitution documents (docs/ vs .specify/)
- [x] T197 [P] [Shared] Record ADR-0001 final decision status
- [x] T198 [P] [Shared] Update traceability matrix with TM125–TM142
- [x] T199 [P] [Shared] Update requirements.md to implemented state
- [x] T200 [P] [Shared] Fresh clone verification (45 min)
- [x] T201 [P] [Shared] Set spec.md status to Implemented after acceptance evidence

**Checkpoint**: US1 complete — Monitoring & Observability infrastructure operational

## Phase 4: US2–US5 — Advanced Monitoring & Observability

- [x] T202 [P] [US2] Configure Prometheus alert rules and notification routing
- [x] T203 [P] [US2] Add integration tests for alerting
- [x] T204 [P] [US3] Implement Loki log aggregation across all services
- [x] T205 [P] [US3] Configure Alertmanager notification routing
- [x] T206 [P] [US3] Implement service mesh observability with Istio
- [x] T207 [P] [US4] Configure OpenTelemetry tracing continuation
- [x] T208 [P] [US4] Implement service mesh traffic monitoring
- [x] T209 [P] [US4] Configure runbook generation and execution
- [x] T210 [P] [US5] Implement performance anomaly detection
- [x] T211 [P] [US5] Add integration tests for anomaly detection
- [x] T212 [P] [US5] Add comprehensive documentation
- [x] T213 [P] [US5] Update traceability matrix for all stories
- [x] T214 [P] [Shared] Final fresh clone verification (45 min)
- [x] T215 [P] [Shared] Set all spec.md statuses to Implemented after acceptance evidence

**Checkpoint**: US2–US5 complete — Monitoring & Observability advanced features implemented, documentation complete

## Phase 7: Polish & Cross-Cutting Concerns

- [x] T216 [P] [Shared] Set spec.md status to Implemented
- [x] T217 [Shared] Run complete required check set and confirm PASS
- [x] T218 [P] [Shared] Reconcile constitution documents
- [x] T219 [P] [Shared] Record ADR-0001 final decision status
- [x] T220 [P] [Shared] Update traceability matrix
- [x] T221 [P] [Shared] Update requirements.md to implemented state
- [x] T222 [P] [Shared] Fresh clone verification (30 min)
- [x] T223 [Shared] Set spec.md status to Implemented after acceptance evidence

## Dependencies & Execution Order

- Phase 1 (T162–T174): Foundation — can run immediately
- Phase 2 (T175–T182): Blocking prerequisites — must complete before Phase 3
- Phase 3 (T183–T201): US1 — Monitoring & Observability Infrastructure — depends on Phase 2 complete
- Phase 4 (T202–T215): US2–US5 — Advanced Features — depends on US1 complete
- Phase 7 (T216–T223): Polish — depends on all prior phases complete

## Parallel Execution Examples

### Parallel: Infrastructure Setup (P tasks)
- T187: Configure Prometheus scrape targets (different file from T188)
- T188: Configure Alertmanager routing rules (different file, no Prometheus dependency)
- T189: Implement Loki query middleware (different file)
- T190: Implement Prometheus metrics exposition (different file)
- T191: Implement OpenTelemetry tracing propagation across service boundaries (different concern)
- T193: Configure Istio observability metrics and dashboards (different concern)
- All six can run in parallel, each modifying different files

### Parallel: Middleware Implementation (P tasks)
- T190: Prometheus metrics exposition (different concern from T191)
- T191: OpenTelemetry tracing (different concern)
- T193: Istio observability (different concern)
- All three can run in parallel, each modifying different files

### Parallel: Checklist Updates (P tasks)
- T196–T199: Constitution reconciliation, ADR recording, traceability, requirements update
- All can run once US1 acceptance evidence is collected

### Parallel: Documentation (P tasks)
- T212–T215: Documentation, traceability matrix, requirements update, fresh clone, spec status
- All can run once US1–US5 acceptance evidence is collected
