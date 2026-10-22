# Implementation Plan: build-phase9

**Branch**: `main` | **Date**: 2026-10-21 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/009-build-phase9/spec.md`

## Summary

Extend the build pipeline beyond the phase 7 horizon with five capabilities:
additional pipeline stages, enhanced phase gate validation, a phase
documentation framework, integration with external build systems, and
compliance and regulatory reporting for build processes, plus build version
and metadata tracking.

The technical approach is recorded in [research.md](research.md) and the
conceptual entities in [data-model.md](data-model.md). The build version and
metadata tracking requirement (FR-095) is the anchor the other four stories
depend on, because the compliance report and the traceability check both
resolve against a released version's metadata.

## Technical Context

**Language/Version**: Python 3.13 (pinned by `.python-version`)

**Primary Dependencies**: The existing build lane — `uv`, `nox`, `ruff`,
`mypy`, `pytest` — plus `pip-audit` for the compliance view of the locked
dependency graph. External build systems are reached over their documented
APIs (NFR-062).

**Storage**: Version metadata and compliance records require durable storage.
The existing centralized PostgreSQL instance (ADR-0001) is used with a schema
dedicated to the build domain, so service ownership is not violated (Art. II).
Schema ownership is assigned to the build domain before implementation.

**Testing**: `pytest` through the nox `fast_checks` session, with contract
tests for each new pipeline stage and integration tests for the external
system adapters

**Target Platform**: Linux server and developer workstations

**Project Type**: Build tooling and reporting pipeline

**Performance Goals**: Phase gate validation completes in under 30 seconds
(NFR-061); pipeline stages execute idempotently (NFR-060)

**Constraints**:
- Compliance reports must be generated on demand (NFR-063)
- Released version metadata is immutable (NFR-064)
- External build system integrations use standardized protocols (NFR-062)
- A pipeline stage that is skipped must not fail the build (Edge Cases)

**Scale/Scope**: Six functional requirements (FR-090 to FR-095) across five
user stories, reserving test mappings TM280–TM297 across tasks T256–T261

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Art. I — Specification First
- **Pass**: `spec.md` defines FR-090 to FR-095, NFR-060 to NFR-064, SC-01 to
  SC-05, five assumptions and five edge cases. The phase remains **Proposed**
  until its acceptance criteria pass

### Art. II — Domain Ownership and Service Boundaries
- **Pass**: The phase adds build-domain pipeline stages and reporting. It
  introduces no new business service and does not take ownership of any
  existing domain's data. Version metadata and compliance records live in a
  build-domain schema

### Art. III — Security and Privacy by Design
- **Pass**: External build system integration uses OAuth2.0 or the equivalent
  standardized protocol (NFR-062); credentials are read from the environment
  and never committed; the secret scan gate covers the new artefacts

### Art. VI — API and Integration Contracts
- **Pass**: Each external build system adapter defines its request and
  response contract before implementation, and the phase gate validation
  criteria are published as a contract so a gate result is reproducible

### Art. VII — Testing and Verifiability
- **Pass**: SC-01 to SC-05 are measurable; each of the five edge cases has an
  identified test; TM280–TM297 reserve a test mapping per requirement

### Art. X — Maintainability and Delivery
- **Pass**: The pipeline stages are idempotent (NFR-060) and the phase gate
  validates in under 30 seconds (NFR-061), so the phase does not slow the
  delivery lane materially

**Constitution Check: ALL GATES PASS**

## Project Structure

### Documentation (this feature)

```text
specs/009-build-phase9/
├── plan.md              # This file
├── spec.md              # Feature specification
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
└── tasks.md             # Phase 2 output
```

### Source Code (repository root)

```text
build/
├── stages/              # Pipeline stage implementations (US1)
│   └── ...
├── gates/               # Phase gate validation (US2)
│   └── ...
├── documentation/       # Phase documentation framework (US3)
│   └── ...
├── integrations/        # External build system adapters (US4)
│   └── ...
├── compliance/          # Compliance and regulatory reporting (US5)
│   └── ...
└── versioning/          # Build version and metadata tracking (FR-095)
    └── ...
tests/
├── contract/            # Pipeline stage and gate contracts
├── integration/         # External system adapter flows
└── unit/                # Isolated units
```

The `build/` package is new to this phase; it is the first top-level package
outside `src/` and `services/`. Placing it there keeps the build domain
separable from the runtime services (Art. II).

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| New top-level `build/` package | The build domain owns pipeline stages, gates, documentation, integrations, compliance and version metadata; the runtime services must not depend on it | Folding the stages into `src/` would make the runtime application depend on build tooling and would couple the two delivery lanes |
