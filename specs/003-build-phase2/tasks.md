# Tasks: build-phase2

**Input**: Design documents from `specs/003-build-phase2/`
**Spec**: `specs/003-build-phase2/spec.md`
**Plan**: `specs/003-build-phase2/plan.md`

Artefacts this phase still owes, and the task that produces each:

| Artefact | Produced by |
|---|---|
| `specs/003-build-phase2/research.md` — the decisions behind the plan | T006 |
| `specs/003-build-phase2/data-model.md` — the conceptual and logical data model | T006 |
| `docs/domain-model/data-model-overview.md` — the non-specialist description | T007 |
| `specs/003-build-phase2/quickstart.md` — the runnable guide | T010 |

**Prerequisites**: spec.md, plan.md, research.md, and data-model.md (all exist),
quickstart.md (produced by T010)

**Tests**: Included. The specification's traceability table names a test identifier for every requirement, and Constitution Article VII.1 requires every acceptance criterion to map to a verifiable test. The test bodies are written with the implementation they verify.

**Organization**: Tasks are grouped by phase to enable independent implementation and testing of each phase.

✅ Gate cleared: Constitution Article I.1 permits implementation against an **approved** specification. The phase-2 specification is **Approved** (2026-10-22); its three open questions are answered in `specs/003-build-phase2/research.md`.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase Status

This phase is **complete**. The specification, its quality
checklist, this plan, this task list, the research record, the conceptual and
logical data model, the non-specialist description of that model, and the
completion report exist. The data model and database foundation are delivered and reviewed.

---

## Phase 1: Specification

**Purpose**: State what the data model and database foundation must deliver.

- [X] T001 Write `specs/003-build-phase2/spec.md` describing the phase-2 outcomes, the constraints it inherits, and its success criteria
- [X] T002 [P] Write `specs/003-build-phase2/checklists/requirements.md` validating the specification's completeness and quality
- [X] T003 [P] Record the specification completion state in `specs/003-build-phase2/completion-report.md`
- [X] T004 [P] Write `specs/003-build-phase2/plan.md` stating the technical context, the constitution check, and the impact of the phase
- [X] T005 [P] Write `specs/003-build-phase2/tasks.md` recording the authorised scope

**Checkpoint**: The specification is complete and its quality checklist passes.

**Open before approval**: the three open questions in the specification's Open
Questions section — Q-DM-001 (which domains the phase models), Q-DM-002 (which
service owns the shared reference data), and Q-DM-003 (how far effective dating
extends) — must be answered and the specification re-reviewed before it can be
approved.

**Closed**: all three questions are answered by D-01, D-02, and D-03 in
`specs/003-build-phase2/research.md`, the specification is re-reviewed against
its checklist, and it carries the status `Approved` (2026-10-22).

---

## Phase 2: Data Model

**Purpose**: Write the conceptual and logical data model the migrations implement.

- [X] T006 [P] Write `specs/003-build-phase2/data-model.md` with the conceptual ER model, the logical data dictionary, and the key and constraint rules for each domain, and record the decisions behind the plan in `specs/003-build-phase2/research.md`
- [X] T007 [P] Write `docs/domain-model/data-model-overview.md` to describe the model at the level a non-specialist reader needs
- [X] T008 Review the data dictionary against the conceptual ER model and record the review outcome in `specs/003-build-phase2/completion-report.md`

**Checkpoint**: The data model is reviewed.

---

## Phase 3: Database Foundation

**Purpose**: Create the schemas, the roles, and the initial migrations.

- [X] T009 [P] Add the phase-2 schemas and their least-privilege roles to `deploy/compose/compose.yaml` and `deploy/compose/initdb/001_schemas_and_roles.sql`
- [X] T010 Write the initial migration set under `migrations/versions/` that creates a clean database
- [X] T011 [P] Add the migration and schema tests to `tests/` and wire them into the required-check set
- [X] T012 Record the evidence that the initial migrations create a clean database and pass the migration tests in `specs/003-build-phase2/completion-report.md`

**Checkpoint**: The phase-2 exit-gate conditions in `docs/build-plan.md` are met.

This phase is **complete**: all tasks T001–T012 are done. Migration set creates a clean database (verified against PostgreSQL), schema matches the model, reversibility holds, no cross-schema FKs, and role grants are enforced. Tests and preflight are wired into the required checks.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Specification**: No dependencies
- **Data Model**: Depends on the specification
- **Database Foundation**: Depends on the reviewed data model

### Within Each Phase

- Tests MUST be written and FAIL before implementation
- The data dictionary is written before the migrations
- The migrations are written before the migration tests are written

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate a phase independently
