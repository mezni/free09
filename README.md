# Telco Platform — Project Setup and Governance

## Purpose
A monorepo of four independently-deployable FastAPI services plus a shared
technical library, governed by Spec Kit artefacts. No runtime network endpoint
and no application database object is introduced by the project-setup phase (BR-011).

## Repository Conventions
- **Path layout**: follows `specs/001-project-setup/contracts/repository-layout-contract.md`
- **Services**: `services/<name>/src/<package_name>/` — application source
- **Library**: `libs/telco-common/src/telco_common/` — shared utilities only
- **Tests**: `tests/contract/`, `tests/governance/` — cross-service and governance tests
- **CI**: `ci/` — machine-consumed verification configuration
- **Deploy**: `deploy/compose/` — local runtime topology
- **Docs**: `docs/` — governance and design prose
- **Specs**: `specs/<nnn>-<feature>/` — one directory per feature, each holding
  `spec.md`, `research.md`, `data-model.md`, `contracts/`, `quickstart.md`,
  `checklists/requirements.md`, and (where planned) `plan.md` and `tasks.md`

## Contributing
See [CONTRIBUTING.md](CONTRIBUTING.md) for development workflow, pull request process,
specification development, task development, documentation standards, code standards,
and issue reporting guidelines.

## Documentation Index

| Document | Purpose |
|---|---|
| [CONTRIBUTING.md](CONTRIBUTING.md) | Contribution rules and workflow gates |
| [docs/build-plan.md](docs/build-plan.md) | Phase-by-phase delivery plan and exit gates |
| [docs/constitution.md](docs/constitution.md) | Governing principles (clause-numbered source) |
| [.specify/memory/constitution.md](.specify/memory/constitution.md) | Governance record of the constitution |
| [docs/architecture/architecture-overview.md](docs/architecture/architecture-overview.md) | Service responsibilities and topology |
| [docs/domain-model/data-model-overview.md](docs/domain-model/data-model-overview.md) | Conceptual and logical data model |
| [docs/traceability-matrix.md](docs/traceability-matrix.md) | Requirement-to-test mapping (central matrix) |
| [docs/quality/test-strategy.md](docs/quality/test-strategy.md) | Test strategy and quality lanes |
| [docs/quality/definition-of-done.md](docs/quality/definition-of-done.md) | Completion criteria per work item |
| [docs/risks/open-questions.md](docs/risks/open-questions.md) | Open questions with owners and due phases |
| [docs/API_REFERENCE.md](docs/API_REFERENCE.md) | API contract layer reference |
| [docs/adr/](docs/adr/) | Architecture decision records |
| [specs/](specs/) | Per-feature specification artefacts |

## Documented Setup Path
1. Clone the repository
2. Ensure Python 3.13+ is installed (`pyenv global 3.13` or `.python-version`)
3. Run `make setup` to verify prerequisites and create `.env` from `.env.example`
   (an existing `.env` is preserved; `FORCE_ENV_RECREATE=1` overwrites it)
4. Run `make test` to execute the local verification lane
5. Run `docker compose -f deploy/compose/compose.yaml up -d` to start PostgreSQL

## Verification Command
```
make test
```
This runs the nox `fast_checks` lane, which includes format, lint, lockfile,
typecheck, test, secret-scan, and dependency-audit checks. Exit codes:
- **0** — PASS (all checks passed)
- **1** — FAIL (one or more checks failed)
- **2** — COULD NOT RUN (check could not execute)
- **3** — INTERNAL ERROR (unexpected failure)

The same lane can be invoked directly for CI callers:
```
ci/run-checks.sh fast_checks
```

## Quick Start
```bash
git clone <repository>
cd telco-si
make setup
make test
docker compose -f deploy/compose/compose.yaml up -d
```

## Philosophy
- BR-011: No runtime network endpoint and no database object introduced by Phase 0
- BR-012: Tooling does not change the Python FastAPI on PostgreSQL baseline
- Checks are reproducible locally with identical results
- Governance is enforced through constitution and traceability matrix

## Version
Currently tracking SPEC-001 build phases 1–11 (`specs/002-build-phase1` through
`specs/011-build-phase11`). Each build phase extends the telco platform with
incremental capabilities governed by approved specifications.

Per-phase traceability mappings are recorded in each phase's `spec.md`. The ranges
in use across the phase set are TM001–TM333; the central matrix at
`docs/traceability-matrix.md` indexes the build-phase5 through build-phase11
rows (TM104–TM124, TM125–TM142, TM221–TM235, TM260–TM277, TM280–TM297,
TM298–TM315, TM316–TM333) and states which are implemented.
