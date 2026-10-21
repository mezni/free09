# Contract: Repository Layout

**Feature**: `SPEC-001` — Project Setup and Governance
**Status**: Active | **Date**: 2026-10-21
**Governed by**: `specs/001-project-setup/spec.md` (FR-001, FR-020, FR-021, FR-022, FR-025, FR-026), Constitution Articles II and X

---

## Purpose

This contract fixes **where things live** and **who owns them**. Every
artefact introduced by Phase 0 belongs to exactly one location, and the
`governance` check verifies that the tree matches this contract, so the
documented layout and the actual layout cannot drift apart (FR-001, AC-017).

## Top-Level Ownership

| Path | Owns | Never contains |
|---|---|---|
| `README.md` | The entry point: what this repository is, what state it is in, how to reach a verified state | Detailed contribution rules, design rationale |
| `CONTRIBUTING.md` | The contributor guide: prerequisites, setup path, required checks, review expectations, remediation runbook | Service-level design documents |
| `docs/` | Governance and design prose: constitution, build plan, quality, architecture, domain model, risks, ADRs | Machine-consumed configuration |
| `specs/` | One directory per feature, holding that feature's specification and its derived artefacts | Source code |
| `templates/` | Reusable, unfilled document formats | Approved content (BR-006) |
| `ci/` | Machine-consumed verification configuration and scripts | Narrative documentation |
| `deploy/` | Runtime topology for local development | Application source |
| `libs/` | The shared technical library | Domain logic (Art. II.7) |
| `services/` | The four independently-deployable services | Shared utilities |
| `tests/` | Cross-service contract tests and repository-governance tests only | A service's own unit tests (Art. II.2) |
| `.github/` | Continuous verification configuration | Application source |

## Governance Artefact Placement

| Artefact | Location | Requirement |
|---|---|---|
| The binding constitution | `.specify/memory/constitution.md` | — |
| The published constitution copy | `docs/constitution.md` | FR-020 — exactly one constitution document exists in the tracked tree; the two copies MUST NOT diverge |
| The build plan | `docs/build-plan.md` | FR-021 |
| Architecture decisions | `docs/adr/ADR-NNNN-<slug>.md` | FR-024 — at least one completed ADR; numbering unique and sequential |
| Architecture overview | `docs/architecture/architecture-overview.md` | FR-024 |
| Quality gates | `docs/quality/definition-of-done.md` | Art. X.3 |
| Test strategy | `docs/quality/test-strategy.md` | Art. VII |
| Traceability matrix | `docs/quality/traceability-matrix.md` | Art. VII.1, FR-029 |
| Exit-gate evidence | `docs/quality/` | FR-031, BR-010 |
| Open questions and risks | `docs/risks/open-questions.md` | FR-027 |
| Domain model | `docs/domain-model/` | Art. V |
| Feature artefacts | `specs/<NNN>-<slug>/` | FR-025, FR-026 |
| Feature quality checklist | `specs/<NNN>-<slug>/checklists/requirements.md` | FR-030 |
| Decision log template | `templates/decision-log-template.md` | FR-022 |

> **Correction applied by this phase.** The README's original layout diagram
> placed the ADR directory at the repository root, but the ADR actually lives
> at `docs/adr/`. Rather than introduce a second ADR location, the README is
> corrected to point at `docs/adr/`, which is also what FR-001 and AC-017
> require — the documented layout and the tracked structure must agree.

## Service Layout

Each of the four constitution-named services occupies a top-level sibling under
`services/`:

```text
services/<service-name>/
├── pyproject.toml            # the service's own dependency declaration
├── src/<package_name>/
│   ├── __init__.py
│   └── ...                   # application code
└── tests/                    # this service's own tests (Art. II.2)
```

| Service | Package | Owns |
|---|---|---|
| `auth-service` | `auth_service` | Identity, authentication, authorisation, credential and token lifecycle, subscriber identity linkage |
| `crm-service` | `crm_service` | Customer and subscriber records, account lifecycle, product catalogue |
| `billing-service` | `billing_service` | Invoicing, payments, immutable ledger, refunds, dunning |
| `inventory-service` | `inventory_service` | SIM and device stock, reservations, fulfilment, provisioning status |

Rules, each of which the `governance` or `lint` check enforces where
mechanically possible:

1. A service MUST NOT import from another service's package. Enforced by a
   ruff `flake8-tidy-imports` `banned-api` rule over the service package
   names. Cross-service communication happens through a contract, never through
   a source import (Art. II.4).
2. A service's dependencies are declared in its own `pyproject.toml`. The
   shared `uv.lock` resolves them together, but a service's closure remains
   extractable with `uv export --package <service>`.
3. A service owns its tests. The root `tests/` directory MUST NOT contain a
   service's unit or integration tests (Art. II.2).
4. A service MUST use only its own database URL and MUST NOT be able to reach
   another service's schema (Art. II.2 least-privilege requirement).

## Shared Library Layout

```text
libs/telco-common/
├── pyproject.toml
├── src/telco_common/        # technical utilities ONLY
└── tests/
```

`telco-common` holds **technical** utilities only: configuration loading,
logging setup, correlation-identifier propagation, database session helpers,
error and problem-detail types, and shared test fixtures. It MUST NOT contain
domain logic, and it MUST NOT contain a domain type that belongs to exactly
one service (Art. II.7).

The reason the directory is named `libs/` rather than `packages/` is that the
name itself records the constraint. `packages/` would suggest a peer of
`services/`, implying deployable units; `libs/` says shared and non-deployable.

## Root Test Layout

```text
tests/
├── contract/                # cross-service contract tests
└── governance/              # repository-governance tests
```

`tests/governance/` holds the tests that prove the repository's own rules —
for example `test_no_network_endpoint_or_database_object_introduced`
(BR-011) and `test_exit_gate_evidence_recorded_for_every_condition`
(BR-010). These are the tests that make the governance claims checkable rather
than asserted.

## Feature Directory Layout

```text
specs/<NNN>-<slug>/
├── spec.md                  # the specification; status lives here
├── plan.md                  # the implementation plan
├── research.md              # Phase 0 decisions with rationale
├── data-model.md            # Phase 1 data model
├── quickstart.md            # Phase 1 runnable guide
├── contracts/               # Phase 1 contracts
├── checklists/
│   └── requirements.md      # specification quality checklist
└── tasks.md                 # Phase 2 task set
```

Numbering is **sequential** — the next number is one greater than the highest
existing — and the identifier is unique within the repository (FR-026). The
`governance` check rejects a duplicate number, a gap in the sequence, and a
directory whose name does not match its number.

## Naming Rules

| Kind | Pattern | Example |
|---|---|---|
| Feature directory | `<NNN>-<kebab-case-slug>` | `001-project-setup` |
| Decision record | `ADR-<NNNN>-<kebab-case-slug>.md` | `ADR-0002-uv-workspace.md` |
| Python package | `snake_case`, matching the service | `billing_service` |
| Test file | `test_<unit-under-test>.py` | `test_ledger_entry_immutability.py` |
| Test function | `test_<behaviour_in_english>` | `test_crm_role_cannot_write_billing_schema` |
| Nox session | the check ID | `secret-scan` |

Test names MUST state the behaviour being verified, not the function being
called. A test name that reads as `test_calls_calculate_tax` documents the
implementation and fails to document the requirement.

## Verification

| Rule | Enforced by |
|---|---|
| The tracked tree matches this contract | `governance` check |
| Every tracked file is covered by a required check or a justified exclusion | `file-coverage` check |
| Templates contain unfilled placeholders only | `governance` check |
| No service imports another service | `lint` check (ruff `banned-api`) |
| A service's own tests live with the service | `governance` check |
| Feature numbering is unique and sequential | `governance` check |

## Change Procedure

A change to this contract changes where files live, so it is reviewed as a
structural change:

1. Propose the change with the artefact being moved or added, and its new
   owner.
2. Move the artefact and update every reference to it in the same change set.
3. Update `ci/file-coverage.yml` if the artefact's path glob changes.
4. Update `README.md` and `CONTRIBUTING.md` if the documented layout changes.
5. Run `uv run nox` — the `governance` and `file-coverage` checks will fail
   until every reference is updated.

Moves are not silently performed by tooling. A file move is a deletion plus an
addition in Git's model, and the reviewer sees both.
