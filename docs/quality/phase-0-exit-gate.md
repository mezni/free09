# Phase 0 Exit Gate — Evidence

**Feature**: SPEC-001 — Project Setup and Governance
**Gate defined by**: `docs/build-plan.md`, "Phase 0 — Project setup and governance"
**Status**: Closed with recorded evidence
**Recorded**: 2026-10-21

The build plan states three Phase 0 exit-gate conditions. Each is recorded
below with the evidence that satisfies it and the check that keeps it true.

## Gate Conditions and Evidence

| # | Condition (from `docs/build-plan.md`) | Evidence | Verified by |
|---|---|---|---|
| 1 | Clean environment setup is reproducible | `ci/setup.sh` is idempotent: it creates `.env` from `.env.example` only when `.env` is absent, and preserves locally supplied values. `ci/check_prerequisites.py` names each missing prerequisite and the documented baseline (`Python 3.13+`, `uv`, `Docker`, `git`, `make`). Two independent setup paths are asserted to reach an equivalent state by `tests/governance/test_setup_determinism.py`. | `tests/governance/test_setup_determinism.py`, `tests/governance/test_setup_prerequisites.py`, `tests/governance/test_fresh_clone_setup.py` |
| 2 | Formatting, linting, and a minimal test run succeed in CI | `.github/workflows/ci.yml` runs the nine required checks as two lanes — `fast-checks` and `slow-checks` — feeding the `required-checks` gate, which runs under `if: always()` and fails unless both lanes report exactly `success`. The local equivalent run of the same nox sessions on commit `da0c66b` reported PASS for all nine checks: format, lint, lockfile, governance, file-coverage, typecheck, test, secret-scan, dependency-audit. | `.github/workflows/ci.yml`, `noxfile.py`, `docs/quality/traceability-matrix.md` |
| 3 | No secrets are committed | `ci/secret_scan.py` scans every tracked file and every commit in the version-controlled history. On commit `da0c66b` it reported no finding, and it never prints a detected value — the `secret` and `match` fields of every finding are redacted before output. The repository's `.env` is untracked and excluded by `.gitignore`. | `ci/secret_scan.py`, `tests/governance/test_secret_scan_history.py`, `tests/governance/test_no_real_secret_in_tracked_files.py` |

## Constitution Compliance Review

The constitution requires a compliance review at each phase exit gate
(`docs/constitution.md`, Art. XI, "Compliance Review"):

- **No obligation without a specification.** Phase 0 introduces governance and
  verification machinery only. It adds no runtime behaviour, no domain rule,
  and no API surface. Every obligation it introduces is stated in
  `specs/001-project-setup/spec.md` and in the contracts under
  `specs/001-project-setup/contracts/`.
- **Acceptance criteria map to the articles the specification cites.** Each row
  of `docs/quality/traceability-matrix.md` names the test that proves the
  requirement, and each test maps to the article the requirement cites.
- **Quality gates.** The required-check set is defined once, in `noxfile.py`,
  and is invoked identically by the local command and by CI (Art. X.6).
- **Baseline unchanged.** The implementation-language baseline is unchanged
  (BR-012): the platform remains Python 3.13 on FastAPI with SQLAlchemy and
  PostgreSQL. The strict type-checking configuration in `mypy.ini` is
  configuration, not a baseline change.
- **No runtime surface.** Phase 0 introduces no runtime network endpoint and
  no application database object (BR-011).

## Artefact Coverage

Every artefact this phase introduces is covered by a required check or carries
a recorded exemption. The coverage map is `ci/file-coverage.yml`, and the
`file-coverage` required check fails when a tracked file is neither covered
nor exempted, when an exemption has expired, or when a declared check is
missing from the merge gate.

## Residual Items

- The automated run of `.github/workflows/ci.yml` on `main` is recorded by the
  workflow run itself; the local equivalent run cited above is the evidence
  available before that run.
- `docs/architecture/architecture-overview.md` remains Proposed pending
  review. It is a Phase 1 artefact, not a Phase 0 gate condition.
