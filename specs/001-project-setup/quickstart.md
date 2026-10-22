# Quickstart — SPEC-001 Project Setup and Governance

## six-step setup path

| Step | Command | Expected Outcome |
|------|---------|-----------------|
| 1 | `git clone <repository>` | Repository cloned successfully |
| 2 | `cd telco-platform && make setup` | Project structure initialized; `.gitignore`, `pyproject.toml`, `.python-version`, `Makefile`, `uv.lock` created |
| 3 | `make test` | Fast-checks suite runs; all checks report **PASS** or **COULD NOT RUN** |
| 4 | `docker compose -f deploy/compose/compose.yaml up -d` | PostgreSQL starts; health check passes within 30 seconds |
| 5 | `make test` | All required checks (format, lint, lockfile, typecheck, test, secret-scan, dependency-audit) run; exit code 0 if all PASS |
| 6 | Verify `.env` exists and contains placeholder values only | `.env` contains `DB_PASSWORD=PLACEHOLDER_NO_REAL_CREDENTIAL` and no real credentials |

## Prerequisites
- Python 3.13+ installed
- `uv` 0.12.15+ installed
- `docker` available (for PostgreSQL)
- `make` installed

## Expected Outcomes
- Full required-check set ≤ 5 minutes on CI (SC-005)
- Fast lane ≤ 2 minutes (SC-005)
- Fresh clone to verified state ≤ 30 minutes (SC-001)
- Local check run ≤ 3 minutes excluding cold dependency resolution (SC-004)

## Notes
- BR-011: No runtime network endpoint and no database object introduced
- BR-012: Implementation-language baseline unchanged (Python 3.13)
- All decisions, with alternatives considered and rejected, are recorded in `research.md`
- The traceability matrix (`docs/quality/traceability-matrix.md`) maps all 34 test mapping rows to requirements
EOF
echo "quickstart.md created"
