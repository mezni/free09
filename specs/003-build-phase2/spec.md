# build-phase2: Data Model and Database Foundation

**Feature**: Data model and database foundation for the telco platform  
**Priority**: P0 (must-have for every later phase)  
**Status**: Approved  
**Approved on**: 2026-10-22  
**Plan phase**: Phase 2 — Data model and database foundation (`docs/build-plan.md`)  
**Data model**: [data-model.md](data-model.md) | **Decisions**: [research.md](research.md)

## User Stories

- **US1**: As a data owner, I want the conceptual and logical data model of my domain documented, so that the tables I own are reviewable before any migration is written.
- **US2**: As a reviewer, I want every schema change to arrive as a reviewable migration with a stated rollback, so that no change is applied by hand to a live database.
- **US3**: As a developer, I want a local PostgreSQL environment that matches production in version and configuration, so that migrations are exercised against a real database before they are merged.

## Functional Requirements

- **FR-033**: The phase MUST deliver a conceptual ER model and a logical data model covering the domains the platform owns.
- **FR-034**: Each domain's data model MUST be assigned to exactly one owning service, in line with Constitution Art. V.1.
- **FR-035**: Each modelled table MUST declare its primary key, its foreign keys, its constraints and its lifecycle or status fields.
- **FR-036**: Each modelled table MUST declare the indexes required by its own access patterns.
- **FR-037**: Every schema change MUST be expressed as a reviewable Alembic migration; no change may be applied by hand to a live database (Constitution Art. V.2 and V.3).
- **FR-038**: A destructive migration MUST state its rollback, and a breaking change MUST be split into an expand step and a contract step (Constitution Art. V.3 and V.4).
- **FR-039**: The migration policy MUST define how migrations are reviewed, applied, and verified in a clean database.
- **FR-040**: The local database environment MUST run the same PostgreSQL major version as the deployment target and MUST be reproducible from the repository.
- **FR-041**: Every table MUST carry the audit fields the platform requires, and MUST state which of them are effective-dated.
- **FR-042**: The data model and the documentation that describes it MUST be updated in the same change set (Constitution Art. V.5).

## Non-Functional Requirements

- **NFR-030**: A migration applied to an empty database MUST produce a schema that matches the documented data model.
- **NFR-031**: The migration set MUST be forward-applicable from the initial revision to the head revision without manual intervention.
- **NFR-032**: No migration may depend on state that only exists in a developer's local database.
- **NFR-033**: The documented data model MUST be readable by a non-specialist, so that it can be reviewed without reading the migrations.

## Boundaries

- **In-scope**: conceptual and logical data model, schema ownership, keys, constraints, indexes, lifecycle and status fields, audit fields, effective dating, historical-data strategy, migration policy, local database environment.
- **Out-of-scope**: service implementation, API endpoints, authentication and authorization behaviour, synthetic data generation, production provisioning, and any change to the Python, FastAPI, or PostgreSQL baseline established in Phase 0.

## Acceptance Criteria

- [ ] The conceptual ER model and the logical data dictionary describe every domain the platform owns (FR-033).
- [ ] Every domain in the data model names exactly one owning service (FR-034, Constitution Art. V.1).
- [ ] Every table declares its primary key, foreign keys, constraints, and lifecycle or status fields (FR-035).
- [ ] Every table declares the indexes its access patterns require (FR-036).
- [ ] Every schema change is expressed as a reviewable Alembic migration, and no change is applied by hand (FR-037, Constitution Art. V.2 and V.3).
- [ ] Every destructive migration states its rollback, and every breaking change is split into expand and contract steps (FR-038, Constitution Art. V.4).
- [ ] The migration policy states how a migration is reviewed, applied, and verified against a clean database (FR-039).
- [ ] The local database environment runs the deployment PostgreSQL major version and starts from the repository without manual steps (FR-040).
- [ ] Every table carries the required audit fields and states which fields are effective-dated (FR-041).
- [ ] The data model and its documentation are updated in the same change set (FR-042, Constitution Art. V.5).
- [ ] A migration applied to an empty database yields a schema that matches the documented data model (NFR-030).
- [ ] The migration set applies from the initial revision to the head revision without manual intervention (NFR-031).
- [ ] No migration depends on state that exists only in a developer's local database (NFR-032).
- [ ] The data model is readable by a non-specialist reviewer (NFR-033).

## Edge Cases

- **A domain has no owning service**: the phase does not proceed past planning for that domain; the ownership question is recorded as an open question instead of a table
- **A table needs a key owned by another service**: the foreign key is not created across the ownership boundary; the reference is carried by a stable identifier instead, and the decision is recorded in the data dictionary
- **A breaking change is required by the phase**: the change is split into an expand step that is compatible with the currently deployed application version and a contract step that removes the old shape
- **A migration cannot be reversed**: it is marked destructive, states the manual restoration procedure, and is reviewed as such
- **The local database is not empty**: migrations are applied only to a clean database in the verification path; a developer's local state is never the source of truth
- **A migration depends on data seeded by another phase**: the dependency is ordered explicitly in the migration set, and the phase that seeds the data is named
- **The deployment PostgreSQL version differs from the local version**: the local environment is corrected to the deployment major version before the migration set is verified

## Assumptions

- PostgreSQL 16.15 is the deployment target major version, matching the local environment established in Phase 0.
- Alembic is the sole migration tool from Phase 2 onward, per Constitution Art. V.3.
- The service inventory and the domain boundaries are those recorded in `specs/002-build-phase1/`.
- The authentication and authorization model that Phase 3 builds on is described by its own specification, not by this phase.
- The catalogue is owned by `inventory-service` (D-02 in `research.md`). The repository-layout contract still names the "product catalogue" under `crm-service`; that conflict is recorded as Q-024 for the architecture owner and does not change the model.
- The business rules this phase stores but does not decide — subscriber semantics, billing cycles, tax scope, credit-memo thresholds — remain open with their owners, and are named against the model in `data-model.md` §6.

## Success Criteria

- **SC-030**: Every domain the platform owns appears in the data model with exactly one owning service.
- **SC-031**: The migration set applies to an empty database and reaches the head revision with no manual step.
- **SC-032**: The schema produced by the migration set matches the documented data model.
- **SC-033**: Every destructive migration states a rollback, and every breaking change is split into expand and contract steps.
- **SC-034**: The local database environment starts from the repository alone and runs the deployment PostgreSQL major version.
- **SC-035**: The data model and its documentation are updated in the same change set for every migration.

## Traceability

The test-mapping identifiers are in the global `TMxxx` space, in the range
TM146–TM155 that the central index records as unallocated until this phase
claims it (`docs/traceability-matrix.md`).

| Requirement | User Story | Implementing tasks | Test Mapping | Priority | State |
|---|---|---|---|---|---|
| FR-033 Conceptual and logical data model | US1 | T006, T007 | TM146 | P0 | Partial — the model is delivered in `data-model.md`; the test that verifies it is written with the migration set (T011) |
| FR-034 Single owning service per domain | US1 | T006, T008 | TM147 | P0 | Partial — ownership is assigned in `data-model.md` §1.1 and reviewed in T008; the schema-permission test is written with the migration set (T011) |
| FR-035 Keys, constraints, lifecycle fields | US1 | T006 | TM148 | P0 | Partial — the keys, constraints, and lifecycle fields are declared per table; the constraint test is written with the migration set (T011) |
| FR-036 Declared indexes | US1 | T006 | TM149 | P0 | Partial — the index plan is declared in `data-model.md` §5; the index test is written with the migration set (T011) |
| FR-037 Reviewable Alembic migrations | US2 | T010 | TM150 | P0 | Not started |
| FR-038 Rollback and expand/contract split | US2 | T010 | TM151 | P0 | Not started |
| FR-039 Migration policy | US2 | T012 | TM152 | P0 | Not started |
| FR-040 Local database environment | US3 | T009 | TM153 | P0 | Not started |
| FR-041 Audit fields and effective dating | US1 | T006 | TM154 | P0 | Partial — the audit fields and the three effective-dating forms are declared in `data-model.md` §2; the audit-field test is written with the migration set (T011) |
| FR-042 Data model and documentation together | US1 | T008 | TM155 | P0 | Partial — the model and `docs/domain-model/data-model-overview.md` are updated in the same change set; the check that keeps them together is written with the migration set (T011) |

## Open Questions

All three questions raised during specification were answered during the
research phase and are recorded here rather than left open. Each answer is
recorded as a decision in [`research.md`](research.md), with its rationale and
the alternatives that were rejected.

- **Q-DM-001 — Which domains does the platform own at this phase?** Answered
  by D-01: exactly four domains — `auth`, `crm`, `inventory`, and `billing` —
  one schema each, each owned by exactly one service (Art. II.1, Art. V.1).
- **Q-DM-002 — Which service owns the shared reference data?** Answered by
  D-02: the shared reference data is the commercial catalogue, owned by
  `inventory-service` in the `inventory` schema; every other domain reads it
  through that service's API, and no service keeps a copy.
- **Q-DM-003 — How far does effective dating extend?** Answered by D-03:
  history is kept in three forms, chosen by the kind of data — temporal rows
  (`valid_from`/`valid_to`) for master data, append-only rows for events, and
  immutable snapshots for priced documents. There is no generic history table.

Two further decisions were required before the data dictionary could be
written, and are recorded in the same file: D-04 prohibits a foreign key across
a schema boundary, which closes Q-011 in `docs/risks/open-questions.md`; and
D-02's conflict with the repository-layout contract is recorded as Q-024 for
the architecture owner.

## Constitution

The project is governed by the constitution at `docs/constitution.md` v1.0.0.
Clause references use the numbered form from `docs/constitution.md` (citation convention).
Per Art. XI.4, in the event of conflict between the numbered copy and the prose copy, the numbered copy prevails.

## Approval

- Status: Approved
- Approved on: 2026-10-22
- Feature directory: specs/003-build-phase2
- Short name: build-phase2
- Approval basis: the three open questions are answered in `research.md`, the
  specification quality checklist in `checklists/requirements.md` passes
  against the amended specification, and the assumptions the answers rest on
  are recorded in `research.md` and in `docs/risks/open-questions.md`
  (Art. I.5).
