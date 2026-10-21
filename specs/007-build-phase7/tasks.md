# Tasks: build-phase7

**Input**: Design documents from `/home/dali/WORK/telco-si/specs/007-build-phase7/`
**Spec**: `specs/007-build-phase7/spec.md`
**Plan**: `specs/007-build-phase7/plan.md`
**Research**: `specs/007-build-phase7/research.md`
**Data model**: `specs/007-build-phase7/data-model.md`
**Contracts**: `specs/007-build-phase7/contracts/`
**Quickstart**: `specs/007-build-phase7/quickstart.md`

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
follow `specs/007-build-phase7/`:

- `specs/007-build-phase7/` — this feature's artefacts
- `contracts/` — interface contracts and alignment documents
- `docs/` — governance and design prose

---

## Phase 1: Finalization (T221–T225)

**This phase finalizes the SPEC-001 completion across all build phases.**

T221] T001 [P] [US1] Finalize all spec.md statuses to Implemented after acceptance evidence
T222] T002 [P] [US2] Reconcile constitution documents (docs/ vs .specify/) across all phases
T223] T003 [P] [US3] Record final ADR-0001 decision status and update governance artifacts
T224] T004 [P] [US4] Update traceability matrix with all test mappings (TM001–TM220)
T225] T005 [P] [US5] Fresh clone verification (full environment, 30-45 minutes) [COMPLETE T225]

**Checkpoint**: US1 complete — SPEC-001 finalization complete

## Dependencies & Execution Order

- Phase 1 (T221–T225): Finalization — depends on all prior phases (build-phase1 through build-phase6) being complete with all tasks [COMPLETE]
- No subsequent phases (this is the final phase)

## Parallel Execution Examples

### Parallel: Finalization Tasks (P tasks)
- T221: Finalize spec.md statuses (different files across build-phases)
- T222: Reconcile constitution documents (different files)
- T223: Record ADR-0001 final decision (different files)
- T224: Update traceability matrix (different files)
- All five can run in parallel, each modifying different files

### Parallel: Hand-off Documentation (P tasks)
- Once US1–US5 acceptance evidence is collected, all finalization tasks can run in parallel
