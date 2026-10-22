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

⚠️ Blocking gate: Constitution Article I.1 permits implementation only against an **approved** specification. T15, T16, and T17 complete that precondition and MUST complete before any other task in this list begins.

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


**Status**: Implemented — all six tasks complete.

> Completion markers reflect the state of the repository as of 2026-10-22.
> Completed phases are finalized to **Implemented**, the traceability matrix is
> closed for the allocated TM001–TM238 range, and the hand-off report is in
> `docs/HANDOFF.md`. Phases 8–11 remain **Proposed** because their acceptance
> evidence does not exist yet.

---

## Phase 1: Finalization (T224–T228)

**This phase finalizes the SPEC-001 completion across all build phases.**

- [x] T224 [P] [US1] Finalize all spec.md statuses to Implemented after acceptance evidence
- [x] T225 [P] [US2] Reconcile constitution documents (docs/ vs .specify/) across all phases
- [x] T226 [P] [US3] Record final ADR-0001 decision status and update governance artifacts
- [x] T227 [P] [US4] Update traceability matrix with all test mappings (TM001–TM238)
- [x] T228 [P] [US5] Fresh clone verification (full environment, 30-45 minutes)
- [x] T229 [P] [US6] Publish hand-off documentation and knowledge transfer record

**Checkpoint**: US1 complete — SPEC-001 finalization complete

## Dependencies & Execution Order

- Phase 1 (T224–T228): Finalization — depends on all prior phases (build-phase1 through build-phase6) being complete with all tasks [COMPLETE]
- No subsequent phases (this is the final phase)

## Parallel Execution Examples

### Parallel: Finalization Tasks (P tasks)
- T224: Finalize spec.md statuses (different files across build-phases)
- T225: Reconcile constitution documents (different files)
- T226: Record ADR-0001 final decision (different files)
- T227: Update traceability matrix (different files)
- All five can run in parallel, each modifying different files

### Parallel: Hand-off Documentation (P tasks)
- Once US1–US5 acceptance evidence is collected, all finalization tasks can run in parallel
