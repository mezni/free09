# Implementation Plan: build-phase11

**Branch**: `main` | **Date**: 2026-10-21 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/011-build-phase11/spec.md`

## Summary

Extend the build pipeline beyond the phase 10 horizon into reporting and
analysis: additional build pipeline reporting stages, enhanced phase gate
statistical analysis, a phase dashboard and visualization framework,
integration with external monitoring systems, and compliance and statistical
process control reporting, plus build trend analysis and forecasting.

The technical approach is recorded in [research.md](research.md) and the
conceptual entities in [data-model.md](data-model.md). The phase builds
directly on the build-domain structure delivered by build-phase9 and extended
by build-phase10, so the layout is extended rather than re-invented.

## Technical Context

**Language/Version**: Python 3.13 (pinned by `.python-version`)

**Primary Dependencies**: The existing build lane — `uv`, `nox`, `ruff`,
`mypy`, `pytest` — plus a charting and statistical analysis library for the
dashboard and statistical process control reporting (FR-112, FR-114).
External monitoring systems are reached over their documented APIs
(NFR-082).

**Storage**: Report records, statistical samples and trend series require
durable storage. The existing centralized PostgreSQL instance (ADR-0001) is
used with the build-domain schema established by build-phase9, so service
ownership is not violated (Art. II).

**Testing**: `pytest` through the nox `fast_checks` session, with contract
tests for each reporting stage and integration tests for the external
monitoring system adapters

**Target Platform**: Linux server and developer workstations

**Project Type**: Build tooling, reporting and analysis pipeline

**Performance Goals**: Phase gate statistical analysis completes in under 15
seconds (NFR-081); trend analysis adds less than 3% build-time overhead
(NFR-084); reporting stages execute idempotently (NFR-080)

**Constraints**:
- Compliance and statistical process control reports are generated on demand
  with statistical charts (NFR-083)
- External monitoring system integrations use standardized protocols
  (NFR-082)
- A reporting stage that is skipped must not fail the build (Edge Cases)

**Scale/Scope**: Six functional requirements (FR-110 to FR-115) across five
user stories, reserving test mappings TM316–TM333 across tasks T268–T273

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Art. I — Specification First
- **Pass**: `spec.md` defines FR-110 to FR-115, NFR-080 to NFR-084, SC-01 to
  SC-05, five assumptions and five edge cases. The phase remains **Proposed**
  until its acceptance criteria pass

### Art. II — Domain Ownership and Service Boundaries
- **Pass**: The phase extends the build domain introduced by build-phase9. It
  introduces no new business service and takes ownership of no existing
  domain's data

### Art. III — Security and Privacy by Design
- **Pass**: External monitoring system integration uses OAuth2.0 or the
  equivalent standardized protocol (NFR-082); statistical reports carry no
  credentials or personal data; the secret scan gate covers the new artefacts

### Art. VI — API and Integration Contracts
- **Pass**: Each external monitoring system adapter defines its request and
  response contract before implementation, and the compliance report contract
  fixes the generated fields and the chart payload shape

### Art. VII — Testing and Verifiability
- **Pass**: SC-01 to SC-05 are measurable; each of the five edge cases has an
  identified test; TM316–TM333 reserve a test mapping per requirement

### Art. X — Maintainability and Delivery
- **Pass**: The reporting stages are idempotent (NFR-080), statistical
  analysis completes in under 15 seconds (NFR-081), and the trend analysis
  overhead stays below 3% (NFR-084)

**Constitution Check: ALL GATES PASS**

## Project Structure

### Documentation (this feature)

```text
specs/011-build-phase11/
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
build/                       # Build domain, introduced by build-phase9
├── reporting/               # Reporting stages (US1)
├── gates/                   # Statistical analysis for phase gates (US2)
├── dashboards/              # Dashboard and visualization framework (US3)
├── integrations/            # External monitoring system adapters (US4)
├── compliance/              # Compliance and statistical process control (US5)
└── trends/                  # Build trend analysis and forecasting (FR-115)
tests/
├── contract/                # Reporting stage and chart contracts
├── integration/             # External monitoring adapter flows
└── unit/                    # Isolated units
```

Every path extends the build-phase9 layout; the phase adds `build/reporting/`,
`build/dashboards/` and `build/trends/` and extends the rest.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | — | The phase extends the build domain already justified by build-phase9 and introduces no new service, runtime network endpoint or database object, so every constitution gate passes without a further justified exception |
