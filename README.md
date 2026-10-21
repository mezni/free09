# Telco Platform — Project Setup and Governance

## Purpose
A monorepo of four independently-deployable FastAPI services plus a shared
technical library, governed by Spec Kit artefacts. No runtime network endpoint
and no application database object is introduced by this phase (BR-011).

## Repository Conventions
- **Path layout**: follows `specs/001-project-setup/contracts/repository-layout-contract.md`
- **Services**: `services/<name>/src/<package_name>/` — application source
- **Library**: `libs/telco-common/src/telco_common/` — shared utilities only
- **Tests**: `tests/contract/`, `tests/governance/` — cross-service and governance tests
- **CI**: `ci/` — machine-consumed verification configuration
- **Deploy**: `deploy/compose/` — local runtime topology
- **Docs**: `docs/` — governance and design prose
- **Specs**: `specs/001-project-setup/` — this feature's artefacts

## Documented Setup Path
1. Clone the repository
2. Ensure Python 3.13+ is installed (`pyenv global 3.13` or `.python-version`)
3. Run `make setup` to initialize the project structure
4. Run `make test` to run the fast-checks suite
5. Run `docker compose -f deploy/compose/compose.yaml up -d` to start PostgreSQL
6. The make `setup` target will create `.env` idempotently from `.env.example`
7. Verify: `make local-verification-command-runs-all-required-checks`

## Verification Command
```
make local-verification-command-runs-all-required-checks
```
This runs the nox `fast-checks` lane, which includes format, lint, lockfile,
typecheck, test, secret-scan, and dependency-audit checks. Exit codes:
- **0** — PASS (all checks passed)
- **1** — FAIL (one or more checks failed)
- **2** — COULD NOT RUN (check could not execute)
- **3** — INTERNAL ERROR (unexpected failure)

## Quick Start
```bash
git clone <repository>
cd telco-platform
make setup
make test
docker compose -f deploy/compose/compose.yaml up -d
```

## Philosophy
- BR-011: No runtime network endpoint and no database object introduced by Phase 0
- BR-012: Tooling does not change the Python FastAPI on PostgreSQL baseline
- Checks are reproducible locally with identical results
- Governance is enforced through constitution and traceability matrix
