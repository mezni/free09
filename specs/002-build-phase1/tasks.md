# Tasks: build-phase1

**Input**: Design documents from `/home/dali/WORK/telco-si/specs/002-build-phase1/`
**Spec**: `specs/002-build-phase1/spec.md`
**Plan**: `specs/002-build-phase1/plan.md`
**Research**: `specs/002-build-phase1/research.md`
**Data model**: `specs/002-build-phase1/data-model.md`
**Contracts**: `specs/002-build-phase1/contracts/`
**Quickstart**: `specs/002-build-phase1/quickstart.md`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Included. The feature specification's Test Mapping names a planned test for every requirement, FR-008 requires a minimal test suite, and Constitution Article VII.1 requires every acceptance criterion to map to a verifiable test or a documented manual verification.

**Organization**: Tasks are grouped by phase to enable independent implementation and testing of each phase.

⚠️ Blocking gate: Constitution Article I.1 permits implementation only against an **approved** specification. T012, T013, and T014 complete that precondition and MUST complete before any other task in this list begins.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

This is a **monorepo** of project setup and governance artifacts. Paths below
follow `specs/002-build-phase1/contracts/`:

- `specs/002-build-phase1/` — this feature's artefacts
- `contracts/` — interface contracts and alignment documents
- `docs/` — governance and design prose

---

## Phase 1: Setup (Shared Infrastructure)

- [x] T038 Create project structure per implementation plan
- [x] T039 Initialize project with dependencies per plan.md
- [x] T040 .python-version pinning to 3.13
- [x] T041 [P] Configure linting and formatting tools
- [x] T042 [P] Configure code quality tools

**Checkpoint**: Foundation ready — design tasks can now begin in parallel

## Phase 2: Foundational (Blocking Prerequisites)

**⚠️ CRITICAL**: No design work can begin until this phase is complete.

- [x] T050 Constitution reconciliation between docs/ and .specify/
- [x] T051 Ratify constitution with date and signatures
- [x] T052 Set spec.md status to Approved
- [x] T053 Record ADR-0001 decision status
- [x] T054 Implement configuration loader in config.py
- [x] T055 Create .env.example with placeholder values
- [x] T056 Implement session framework in noxfile.py
- [x] T057 Create ci/run-checks.sh as single entry point
- [x] T058 Create tests/conftest.py with marker registration
- [x] T059 Create minimal test suite that passes on empty impl

**Checkpoint**: Foundation ready — design tasks can now begin in parallel

## Phase 3: Design & Contracts

- [x] T065 [P] [US1] Create test for fresh clone setup verification
- [x] T066 [P] [US1] Create test for language baseline unchanged
- [x] T067 [P] [US1] Create test for setup prerequisites

## Phase 7: Polish & Cross-Cutting Concerns

- [x] T071 [P] [Shared] Set spec.md status to Implemented
- [x] T072 [Shared] Run complete required check set and confirm PASS
- [x] T073 [P] [Shared] Reconcile constitution documents
- [x] T074 [P] [Shared] Record ADR-0001 final decision status
- [x] T075 [P] [Shared] Update traceability matrix
- [x] T076 [P] [Shared] Update requirements.md to implemented state
- [x] T077 [P] [Shared] Fresh clone verification (30 min)
- [x] T078 [Shared] Set spec.md status to Implemented after acceptance evidence

## Dependencies & Execution Order

### Phase Dependencies
- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion — BLOCKS all design work
- **Design (Phase 3)**: Depends on Foundational phase completion
- **Polish (Phase 7)**: Depends on all desired design being complete

### User Story Dependencies
- **Phase 1 tasks**: No dependencies on other phases
- **Phase 2 tasks**: Depend on Phase 1 completion
- **Phase 3 tasks**: Depend on Phase 2 completion
- **Phase 7 tasks**: Depend on all desired design being complete

### Within Each Phase
- Tests (if included) MUST be written and FAIL before implementation
- Configuration and helpers before the checks that consume them
- Check implementations before the CI workflow that invokes them
- Design complete before moving to next phase
- Story complete before moving to next priority

### Parallel Opportunities
-
- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, design tasks can proceed in parallel
- Within a phase, tasks touching the same file are deliberately **not** marked [P]

## Parallel Example: User Story 1

# Launch all Setup tasks together:
Task: "Create project structure per implementation plan"
Task: "Initialize project with dependencies per plan.md"
Task: ".python-version pinning to 3.13"
Task: "Configure linting and formatting tools"
Task: "Configure code quality tools"

# Launch the Foundational tasks alongside them (different files):
Task: "Constitution reconciliation between docs/ and .specify/"
Task: "Ratify constitution with date and signatures"

## Implementation Strategy

### MVP First (build-phase1 Only)
1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL — blocks all design)
3. Complete Phase 3: Design
4. **STOP and VALIDATE**: Verify design artifacts are complete and consistent
5. Deploy/demo if ready

### Incremental Delivery
1. Complete Setup + Foundational → Foundation ready
2. Add design tasks → Verify consistency → Deploy/Demo
3. Each design artifact adds value without breaking previous work

### Parallel Team Strategy
With multiple developers:
1. Team completes Setup + Foundational together
2. Once Foundational is done:
  - Developer A: Design tasks
  - Developer B: Design tasks
  - Developer C: Design tasks
3. Designs complete and integrate independently

## Notes
- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate phase independently
- Avoid: vague tasks, same file conflicts, cross-phase dependencies that break independence
- Every task that creates a tracked file requires a matching entry in `ci/file-coverage.yml` (T056),
or the `file-coverage` check fails
- Every new environment variable requires a matching entry in both `.env.example` (T017)
and the configuration contract, or the `governance` check fails

---
