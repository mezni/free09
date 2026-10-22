# Feature Specifications

Each specification directory holds the artifacts for one build phase. The
directory name carries the `NNN-build-phaseM` form; the number after the dash
is the build-plan phase the specification serves.

```text
specs/
├── README.md
├── 001-project-setup/           # Phase 0 — project setup and governance
│   ├── spec.md                  # Feature specification
│   ├── plan.md                  # Implementation plan
│   ├── research.md              # Phase 0 output
│   ├── data-model.md            # Phase 1 output
│   ├── quickstart.md            # Phase 1 output
│   ├── contracts/               # Phase 1 output
│   ├── checklists/              # Specification quality checklists
│   └── tasks.md                 # Phase 2 output
├── 002-build-phase1/            # Phase 1 — build path and tooling
├── 003-build-phase2/            # Phase 2 — data model and database foundation
├── 004-build-phase3/            # Phase 3 — authentication and authorization
├── 005-build-phase5/            # Phase 5 — advanced features and scale
├── 006-build-phase6/            # Phase 6 — monitoring and observability
├── 007-build-phase7/            # Phase 7 — polish and hand-off
├── 008-build-phase8/            # Phase 8 — cross-service integration
├── 009-build-phase9/            # Phase 9 — build plan extension
├── 010-build-phase10/           # Phase 10 — build plan extension
└── 011-build-phase11/           # Phase 11 — build plan extension
```

The build plan has twelve phases and the repository holds eleven
specification directories: phase 4 (the CRM vertical slice) has no
specification. The authoritative phase-to-specification mapping is the index in
[`docs/build-plan.md`](../docs/build-plan.md).

## Conventions

- **Specification status** is `Draft`, `Approved`, `Proposed` or
  `Implemented`. A phase stays `Proposed` until every acceptance criterion in
  its `spec.md` passes, whatever the state of its task list.
- **Task identifiers** are global for build-phase5, build-phase6,
  build-phase7 and build-phase9 to build-phase11, and phase-local for
  build-phase1, build-phase2, build-phase3 and build-phase8. The `Task` column of a
  traceability table names the identifier that appears in that phase's
  `tasks.md`.
- **Test-mapping identifiers** (`TMxxx`) are global throughout. The central
  index is [`docs/traceability-matrix.md`](../docs/traceability-matrix.md).
- **Requirement identifiers** (`FR-xxx`, `NFR-xxx`) are scoped to the phase
  that introduces them.

Do not mark a specification `Approved` until scope, business rules,
permissions, failure paths and acceptance criteria have been reviewed, and
keep the task plan derived from the approved specification.
