# Implementation Plan: build-phase2

**Branch**: `main` | **Date**: 2026-10-21 | **Updated**: 2026-10-22 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/003-build-phase2/spec.md`

## Summary

Establish the phase-2 foundation of the build programme: the data model and
database foundation the later phases depend on. The specification, its quality
checklist, this plan, the task list, the research record, the conceptual and
logical data model, and the non-specialist description of that model exist;
the database foundation under the model has not started.

The specification is deliberately written against the platform baseline, not
against a database engine. Selecting the engine and the schema layout is the
decision ADR-0001 records, and it is already `Accepted`.

## Technical Context

**Language/Version**: Python 3.13 (pinned by `.python-version`)

**Primary Dependencies**: The existing toolchain — `uv`, `nox`, `ruff`,
`mypy`, `pytest` — plus SQLAlchemy and Alembic, both already declared in the
root `pyproject.toml`

**Storage**: PostgreSQL, one deployment with one schema per domain
(ADR-0001). The schema and role layout is in `deploy/compose/compose.yaml`.

**Testing**: `pytest` through the nox `test` session; the local and CI runs
use the same session (BR-004)

**Target Platform**: Linux server and developer workstations

**Project Type**: Data model and database foundation

**Performance Goals**: The initial migration set creates a clean database and
the migration tests pass — the phase-2 exit-gate condition in
`docs/build-plan.md`

## Constitution Check

| Article | Obligation | How this phase satisfies it |
|---|---|---|
| Art. I.1 | Implementation only against an approved specification | The phase-2 specification is `Approved` (2026-10-22); its three open questions are answered in `research.md` and the assumptions those answers rest on are recorded (Art. I.5). |
| Art. II.2 | Each domain is owned by exactly one service | The schema and role layout gives each of the four domains its own schema and its own least-privilege role. |
| Art. V | Data changes are modelled before they are written | The phase-2 artefacts are the conceptual and logical data model, the data dictionary, and the migration set. |
| Art. VII.1 | Every acceptance criterion maps to a test | The specification's traceability table names the test identifier for every requirement; the tests themselves are written with the implementation. |
| Art. X.3 | Quality gates are mandatory | The migration and schema checks are part of the required-check set before the phase can close. |
| BR-011 | No runtime network endpoint or database object introduced by the setup phase | Phase 0 and phase 2 introduce no runtime endpoint; the schema objects belong to this phase and are introduced by its migrations. |
| BR-012 | The implementation-language baseline is unchanged | The platform remains Python 3.13 on FastAPI with SQLAlchemy and PostgreSQL. |

## Project Layout

```text
specs/003-build-phase2/
├── spec.md                  # the approved specification
├── plan.md                  # this plan
├── research.md              # the decisions behind the plan
├── data-model.md            # the conceptual model and the data dictionary
├── tasks.md                 # the task set
├── checklists/
│   └── requirements.md      # the specification quality checklist
└── completion-report.md     # the completion record and the review outcome
```

Artefacts the phase still owes, and the task that produces each:

| Artefact | Produced by |
|---|---|
| `specs/003-build-phase2/data-model.md` — the conceptual and logical data model | T006 |
| `specs/003-build-phase2/research.md` — the decisions behind the plan | T006 |
| `docs/domain-model/data-model-overview.md` — the non-specialist overview | T007 |
| `specs/003-build-phase2/quickstart.md` — the runnable guide | T010 |

## Impact

- **Affected code**: the migration set under `migrations/`, the model layer
  under `src/models/`, and the schema configuration in
  `deploy/compose/compose.yaml`.
- **Affected documentation**: the domain-model prose under `docs/domain-model/`.
- **Affected checks**: the migration and schema tests become part of the
  required-check set before this phase closes.

## Risks and Mitigations

| Risk | Mitigation |
|---|---|
| A shared database becomes a shared failure domain | Revisit when deployment independence requires separate instances — the trigger is recorded in ADR-0001. |
| A migration is written against a schema that the domain model does not describe | The data dictionary is reviewed before the initial migration set is written. |
| The phase drifts into implementing later phases' behaviour | Each task names the file it touches; the task list is the only authorised scope. |

## Open Questions

The three questions the specification raised are answered. The answers are
recorded as decisions D-01, D-02, and D-03 in `research.md`, together with
their rationale and the alternatives that were rejected.

- **Q-DM-001** — which domains the platform owns at this phase.
- **Q-DM-002** — which service owns the shared reference data.
- **Q-DM-003** — how far effective dating extends.

One conflict between two repository documents remains open and is owned
elsewhere: Q-024 in `docs/risks/open-questions.md`. The layout contract names
the catalogue under `crm-service`, and the architecture overview assigns it to
`inventory-service`; the model follows the architecture overview, and the
contract text is to be corrected.
