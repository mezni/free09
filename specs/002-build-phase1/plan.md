# Implementation Plan: build-phase1

**Branch**: `main` | **Date**: 2026-10-21 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/002-build-phase1/spec.md`

## Summary

Deliver the build phase 1 infrastructure: a repository skeleton, a pinned
Python toolchain, a reproducible dependency lockfile, a documented check lane
and the onboarding path a new engineer follows to reach a verified state.

The phase introduces no runtime network endpoint and no database object
(BR-011). The technical approach is recorded in
[research.md](research.md), the conceptual entities in
[data-model.md](data-model.md) and the onboarding contract in
[contracts/user-scenarios.md](contracts/user-scenarios.md).

## Technical Context

**Language/Version**: Python 3.13 (pinned by `.python-version`)

**Primary Dependencies**: `uv` for dependency resolution and lockfile
management; `nox` as the session runner; `ruff` for formatting and linting;
`mypy` for type checking; `pytest` for the test suite; `pip-audit` for the
dependency audit

**Storage**: None introduced by this phase. Configuration is held in `.env`,
derived from `.env.example`; no database object is created (BR-011)

**Testing**: `pytest` driven through the nox `fast_checks` session, with
governance tests under `tests/governance/`

**Target Platform**: Linux server, macOS and Windows developer workstations

**Project Type**: Monorepo of FastAPI services plus a shared library

**Performance Goals**: Fast lane ≤ 2 minutes; full required-check set ≤ 5
minutes on CI; fresh clone to verified state ≤ 30 minutes (SC-001, SC-005)

**Constraints**:
- BR-011: no runtime network endpoint and no database object introduced
- BR-012: the Python FastAPI on PostgreSQL baseline is unchanged
- Constitution Art. I.1 permits implementation only against an approved
  specification
- The required-check set reports PASS (0), FAIL (1), COULD NOT RUN (2) or
  INTERNAL ERROR (3); both 1 and 2 fail the gate (BR-003)

**Scale/Scope**: Repository skeleton, tooling, lockfile, documentation and
the check lane. No service implementation.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Art. I — Specification First
- **Pass**: `spec.md` defines FR-001 through FR-005 and SC-001 through SC-005;
  research, data model, contracts and quickstart are present

### Art. II — Domain Ownership and Service Boundaries
- **Pass**: The phase creates the directory skeleton only. No service takes
  ownership of a domain and no schema is created

### Art. III — Security and Privacy by Design
- **Pass**: `.env.example` holds placeholders only; `ci/secret_scan.py` fails
  the gate when a credential is committed

### Art. V — Data Modeling and Database Evolution
- **Pass**: No migration is introduced by this phase (BR-011)

### Art. VI — API and Integration Contracts
- **Pass**: No API is introduced by this phase (BR-011)

### Art. VII — Testing and Verifiability
- **Pass**: SC-001 through SC-005 are measurable and each has a check in the
  required-check set

### Art. X — Maintainability and Delivery
- **Pass**: The check lane is reproducible locally and in CI, and the
  exit-code contract is documented in `noxfile.py` and `ci/run-checks.sh`

**Constitution Check: ALL GATES PASS**

## Project Structure

### Documentation (this feature)

```text
specs/002-build-phase1/
├── plan.md              # This file
├── spec.md              # Feature specification
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/
│   ├── constitution-alignment.md
│   ├── success-criteria.md
│   └── user-scenarios.md
└── tasks.md             # Phase 2 output
```

### Source Code (repository root)

```text
pyproject.toml               # Project metadata, dependencies, tool configuration
uv.lock                      # Pinned dependency graph
.python-version              # Interpreter pin (3.13)
Makefile                     # Thin alias layer over nox and docker compose
noxfile.py                   # Session framework and result reporter
ci/
├── setup.sh                 # Idempotent environment bootstrap
├── check_prerequisites.py   # Toolchain verification
├── run-checks.sh            # Single entry point for the check lane
├── secret_scan.py           # Committed-credential detection
├── dependency_audit.py      # Locked-dependency vulnerability audit
└── health_check.py          # Runtime health probe
.env.example                # Documented configuration contract
docs/                        # Governance and design prose
tests/
├── contract/                # Cross-service API contracts
├── governance/              # Constitution and workflow governance tests
├── integration/             # Cross-component flows
└── unit/                    # Isolated units
services/<name>/             # Application source, one directory per service
libs/telco-common/           # Shared technical library
deploy/compose/              # Local runtime topology
```

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | — | The phase introduces no new service, no runtime network endpoint and no database object, so every constitution gate passes without a justified exception |
