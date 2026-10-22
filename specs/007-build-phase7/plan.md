# Implementation Plan: build-phase7

**Branch**: `main` | **Date**: 2026-10-21 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/007-build-phase7/spec.md`

## Summary

Close out the build programme: finalize the specification statuses across every
phase once the acceptance evidence exists, reconcile the two constitution
documents, record the final ADR-0001 decision status, complete the central
traceability matrix, run a fresh-clone verification of the complete
environment, and produce the hand-off documentation in `docs/HANDOFF.md`.

This phase delivers no runtime behaviour. Its outputs are governance and
documentation records, and each one is verifiable by reading the artifact it
names.

## Technical Context

**Language/Version**: Python 3.13 (pinned by `.python-version`)

**Primary Dependencies**: The existing toolchain — `uv`, `nox`, `ruff`,
`mypy`, `pytest` — plus `pip-audit` for the dependency audit in the fresh
clone verification

**Storage**: None. The entities in `data-model.md` are records in the
governance documents, not tables

**Testing**: `pytest` through the nox `fast_checks` session; the fresh clone
verification runs the same lane from a clean checkout

**Target Platform**: Linux server and developer workstations

**Project Type**: Governance and hand-off

**Performance Goals**: Fresh clone verification completes in 30 to 45 minutes
(SC-04, FR-063); every requirement from build-phase1 to build-phase6 appears
in the central traceability matrix

**Constraints**:
- A specification moves to **Implemented** only after its acceptance evidence
  exists (Art. I.1)
- No new feature development, infrastructure changes, database schema
  modifications or business logic implementation (Boundaries)
- The two constitution copies stay aligned under Art. XI.4 precedence

**Scale/Scope**: Requirements FR-060 to FR-065 across user stories US1 to US6,
reserving test mappings TM221–TM238 across tasks T224–T229

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Art. I — Specification First
- **Pass**: `spec.md` defines FR-060 to FR-064, NFR-040 to NFR-043, SC-01 to
  SC-05, five acceptance criteria and five assumptions. This phase *is* the
  work that closes out Art. I.1 for the other phases

### Art. III — Security and Privacy by Design
- **Pass**: The hand-off documentation covers secret handling and the
  remediation path for a committed credential, without reproducing any
  credential material

### Art. VII — Testing and Verifiability
- **Pass**: SC-01 to SC-05 are measurable; the fresh clone verification is the
  test that proves the environment is reproducible

### Art. X — Maintainability and Delivery
- **Pass**: The phase delivers the hand-off record the programme ends with

### Art. XI — Architecture Decisions and Exceptions
- **Pass**: The constitution reconciliation and the ADR-0001 decision status
  are recorded under this article

**Constitution Check: ALL GATES PASS**

## Project Structure

### Documentation (this feature)

```text
specs/007-build-phase7/
├── plan.md              # This file
├── spec.md              # Feature specification
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
└── tasks.md             # Phase 2 output
```

### Source Code (repository root)

The phase changes no application source. It updates these records:

```text
docs/
├── constitution.md          # Ratified constitution with the approval block
├── adr/
│   └── ADR-0001-centralized-postgresql.md   # Final decision status
├── build-plan.md            # Phase-to-specification index and exit gates
└── traceability-matrix.md   # Central TM001–TM333 index
specs/
└── <phase>/spec.md          # Status field, once the evidence exists
```

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | — | The phase adds no service, no runtime network endpoint and no database object, so every constitution gate passes without a justified exception |
