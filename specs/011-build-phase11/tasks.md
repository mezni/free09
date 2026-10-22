# build-phase11: Tasks

**Total tasks**: 6
**Complete**: 0
**Outstanding**: 6
**User stories**: 5 (US1–US5)
**Phases**: 1 (Setup) + 2 (Foundational) + 3–7 (User Stories) + N (Polish)

> **Status**: Not started. No task in this list is complete; the build domain
> that this phase extends is introduced by build-phase9 and does not exist in
> the repository yet. The task identifiers are the global build-plan
> identifiers T268–T273, matching the traceability table in `spec.md`, and the
> test-mapping ranges are TM316–TM333. The phase status stays **Proposed**
> until every acceptance criterion passes.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Extend the build domain introduced by build-phase9

- [ ] T001 Add the `build/reporting/`, `build/dashboards/` and `build/trends/` sub-packages and confirm the build-phase9 and build-phase10 sub-packages are present (per plan.md Project Structure)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T002 [P] Define the statistical sample and control limit model used by the gate analysis and the statistical process control report, including the 15-second analysis timeout (NFR-081)
- [ ] T003 [P] Define the chart payload shape shared by the dashboard and the compliance report (NFR-083)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Pipeline reporting stages (Priority: P1) 🎯 MVP

**Goal**: Additional pipeline reporting stages (FR-110)
**Independent Test**: A reporting stage runs twice over the same input and produces the same report and the same artifacts (NFR-080, SC-01)
**Test Mappings**: TM316–TM318

- [ ] T268 [P] [US1] Implement the pipeline reporting stages in `build/reporting/` with idempotent execution, report handoff between stages, and graceful handling of a skipped stage that leaves an absent report (FR-110, NFR-080)

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Phase gate statistical analysis (Priority: P1)

**Goal**: Enhanced phase gate statistical analysis (FR-111)
**Independent Test**: A phase gate computes its statistics over a sample and reports pass, fail or timeout within 15 seconds (NFR-081, SC-02)
**Test Mappings**: TM319–TM321

- [ ] T269 [P] [US2] Implement phase gate statistical analysis in `build/gates/` over the statistical sample model, with a 15-second timeout that auto-fails and flags for manual review, and a recorded analysis result (FR-111, NFR-081)

**Checkpoint**: At this point, User Story 2 should be fully functional and testable independently

---

## Phase 5: User Story 3 - Dashboard and visualization framework (Priority: P2)

**Goal**: Improved phase dashboard and visualization framework (FR-112)
**Independent Test**: A dashboard renders for a phase and every rendered element traces back to a requirement (SC-03)
**Test Mappings**: TM322–TM324

- [ ] T270 [P] [US3] Implement the phase dashboard and visualization framework in `build/dashboards/` that renders the phase metrics as charts built from the shared chart payload shape (FR-112)

**Checkpoint**: At this point, User Story 3 should be fully functional and testable independently

---

## Phase 6: User Story 4 - External monitoring system integration (Priority: P2)

**Goal**: External monitoring system integration framework (FR-113)
**Independent Test**: An external monitoring system is reached over its standardized protocol and an unreachable system falls back to local execution with a warning (NFR-082, SC-04)
**Test Mappings**: TM325–TM327

- [ ] T271 [P] [US4] Implement the external monitoring system integration framework in `build/integrations/` using a standardized protocol with OAuth2.0 credentials read from the environment, and a mock/local fallback that surfaces a warning when the remote system is unreachable (FR-113, NFR-082)

**Checkpoint**: At this point, User Story 4 should be fully functional and testable independently

---

## Phase 7: User Story 5 - Compliance reporting and trend analysis (Priority: P3)

**Goal**: Compliance and statistical process control reporting features (FR-114) and build trend analysis and forecasting (FR-115)
**Independent Test**: A compliance report is generated on demand with statistical charts, and trend analysis adds less than 3% build-time overhead (NFR-083, NFR-084, SC-05)
**Test Mappings**: TM328–TM333

- [ ] T272 [P] [US5] Implement compliance and statistical process control report generation in `build/compliance/`, generated on demand with statistical charts built from the shared chart payload shape (FR-114, NFR-083)
- [ ] T273 [P] [US5] Implement build trend analysis and forecasting in `build/trends/`, analysing the historical series with less than 3% build-time overhead (FR-115, NFR-084)

**Checkpoint**: At this point, User Story 5 should be fully functional and testable independently

---

## Phase N: Polish & Cross-Cutting Concerns

**Purpose**: Final integration and hardening

- [ ] T007 [P] Run the full check lane and record the result in the phase status block (make test)
- [ ] T008 Verify the constitution gate for the phase and mark the acceptance criteria in `spec.md` as they pass

---

## Dependencies & Execution Order

### Phase Dependencies

- build-phase9 must complete before this phase, because the sub-packages this phase extends are introduced there
- Phase 2 (Foundational) must complete before any user story
- T272 (compliance reporting) must complete before T270 (dashboard), because the dashboard renders the compliance report's charts
- T273 (trend analysis) must complete before T272, because the statistical process control report quotes the forecast

### User Story Dependencies

- US5 (T272, T273) depends on the statistical and chart models from Phase 2
- US3 (T270) depends on the chart payload shape from Phase 2 and on T272
- US1, US2 and US4 are independent of each other

### Within Each User Story

- Each user story is one task, so there is no intra-story ordering
- The test mappings for a story are covered by the contract and integration tests written alongside it

### Parallel Opportunities

- T268, T269, T271 and T273 can proceed in parallel once Phase 2 is complete
- T270 and T272 can proceed in parallel with each other after T272's dependency on T273 is met

## Parallel Example: User Story 1

```bash
# Terminal 1
Task: T268 [US1] Implement the pipeline reporting stages

# Terminal 2
Task: T269 [US2] Implement phase gate statistical analysis
```

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 (T001) and Phase 2 (T002, T003)
2. Complete T268 (US1, reporting stages)
3. Verify the reporting stage idempotency test passes
4. Stop here and ship the MVP; remaining stories are independent

### Incremental Delivery

1. T268 (US1) - reporting stages
2. T269 (US2) - statistical analysis
3. T271 (US4) - external monitoring system integration
4. T273 (US5) - trend analysis and forecasting
5. T272 + T270 (US5, US3) - compliance reporting, then the dashboard that renders it

### Parallel Team Strategy

Four engineers can work in parallel after Phase 2 completes:
- Engineer A: T268 (US1)
- Engineer B: T269 (US2)
- Engineer C: T271 (US4), then T273 (US5)
- Engineer D: T272 (US5), then T270 (US3)

## Notes

**Task ID convention**: The identifiers T268–T273 are the global build-plan
identifiers from the traceability table in `spec.md`. Earlier phase task lists
use local identifiers; this phase follows the global convention so that the
traceability table, the central matrix and this list agree.

**Scope discipline**: Code compilation, test execution, deployment pipeline
overhaul, business logic redesign and infrastructure migration are out of
scope for this phase.

**Verification**: Every task is verified by `make test`, which runs the
`fast_checks` lane: format check, lint, lockfile check, type check, the test
suite, the secret scan and the dependency audit.
