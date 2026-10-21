# Implementation Plan: Project Setup and Governance

**Branch**: `001-project-setup` | **Date**: 2026-10-21 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/001-project-setup/spec.md`

**Prerequisites**: `python3 --version` (3.13+), `uv` 0.12.15+, `docker` 29.7.2+, `git` 2.51+, network access to PyPI and GitHub for the first sync.

## Summary

Phase 0 turns this repository from a documentation-only scaffold into a
verifiably-governed engineering repository, without introducing a single runtime
endpoint or database object (BR-011). It delivers a documented top-level
layout, an entry-point README and a contributor guide, a deterministic setup
path, an automated required-check suite (format, lint, type check, tests,
secret scan, dependency audit, governance checks), a GitHub Actions pipeline
whose gate fails closed on any inconclusive check, an example configuration
containing placeholders only, and the governance artifacts that make those
checks auditable — the file-coverage manifest, the traceability matrix, the
exit-gate evidence record, and the ADRs for the material tooling decisions
taken here.

The technical approach follows the constitution's technology baseline (Python
FastAPI services on PostgreSQL) and constrains itself to tooling that does not
change that baseline (BR-012). Dependency and environment management is uv in
workspace mode; task orchestration is nox with a uv backend so that CI and a
developer's machine invoke the identical session definitions; quality is
enforced by ruff, mypy in strict mode with the pydantic plugin, and pytest;
secrets are detected with gitleaks in redacting mode against full history;
dependency vulnerabilities are checked offline against a vendored advisory
snapshot so the required check is deterministic and needs no network. All
decisions, with the alternatives considered and rejected, are recorded in
[research.md](./research.md).

## Technical Context

**Language/Version**: Python 3.13 (floor `>=3.13,<4`); CI matrix 3.13 and 3.14; `.python-version` pins `3.13`

**Primary Dependencies**: uv 0.12.15 (workspace, single `uv.lock`); ruff 0.17.1 (lint + format); mypy 2.4.0 (`--strict`, `pydantic.mypy` plugin); pytest 9.1.1; pytest-asyncio 1.4.0 (`asyncio_mode = "auto"`); pytest-cov 7.1.0; coverage.py 7.16.2; diff-cover 10.6.0; httpx 0.28.1; nox 2026.10.20; pre-commit 4.7.0; gitleaks v8.30.1 (binary, not a Python package); PostgreSQL 16.15 (`postgres:16.15-alpine`)

**Storage**: PostgreSQL 16.15 for local development and CI only. **No application database object is created by this phase** (BR-011); no schema, no migration, no table. Phase 0's persisted artifacts are repository files only.

**Testing**: pytest 9.1.1 with pytest-asyncio 1.4.0 and pytest-cov 7.1.0; markers `unit`, `integration`, `contract`, `governance`, `slow`; coverage measured and published, not yet gated numerically

**Target Platform**: Linux (CI runner, containers); Linux and macOS (developer workstations); Python 3.13+

**Project Type**: Monorepo of four independently-deployable FastAPI web services (`auth-service`, `crm-service`, `billing-service`, `inventory-service`) plus one shared technical library, governed by Spec Kit artifacts

**Performance Goals**: Full required-check set ≤ 5 minutes on CI (SC-005); fast lane ≤ 2 minutes; fresh clone to verified state ≤ 30 minutes (SC-001); local check run ≤ 3 minutes excluding cold dependency resolution

**Constraints**: Required checks run with no network access to external services and no interactive input (FR-011); no secret material in any tracked file or in history (BR-001, BR-007); no production credentials, production data, or live external system required (BR-008); checks are reproducible locally with identical results (BR-004); no runtime network endpoint and no database object (BR-011); the implementation-language baseline is unchanged (BR-012); third-party actions are SHA-pinned and the workflow token is read-only

**Scale/Scope**: 4 services, 1 shared library, ~10 required checks, ~16 declared environment variables, ~12 minimal tests, 32 functional requirements, 12 business rules, 25 acceptance criteria, 11 success criteria

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Initial gate (before research): PASS** — all eleven principles were consulted
before any research was commissioned; the research questions were derived from
the principles and from the specification's open questions, not the reverse.
No principle was found to conflict with the specification.

**Post-design re-check (after Phase 1) is recorded in
[Constitution Re-check (Post-Design)](#constitution-re-check-post-design).**

**Citation convention.** Clause references such as `Art. VII.1` use the
numbered-clause form of `docs/constitution.md`. The binding governance record
at `.specify/memory/constitution.md` states the same eleven articles in
expanded prose but does not reproduce the clause numbers, and the two copies
have not yet been reconciled — that divergence is tracked as **Q-018** in
`docs/risks/open-questions.md` and is a Phase 0 exit-gate condition. Any
conflict between the two copies resolves under the constitution's own
precedence rule (Art. XI.4) in favour of the approved copy, and neither copy
is approved yet.

### Article-by-article verification

| Article | Principle | Plan response | Status |
|---|---|---|---|
| I | Specification First | The specification exists at `spec.md` with 32 FRs, 12 BRs, 25 ACs, 11 SCs and zero `[NEEDS CLARIFICATION]`. The plan introduces no behaviour the specification does not describe; every tooling choice is a means of satisfying a stated FR. | **CONDITIONAL** — Art. I.1 requires an *approved* specification before implementation. The spec is complete but not yet approved. Approval is the Phase 0 exit gate; see the note below. |
| II | Domain Ownership and Service Boundaries | Layout gives each of the four constitution-named services its own `services/<name>/` package with its own tests, satisfying Art. II.2. `libs/telco-common/` holds technical utilities only, satisfying Art. II.7. Cross-service imports are prohibited by a ruff `flake8-tidy-imports` `banned-api` rule, making Art. II.4 mechanically enforced rather than documentary. | PASS |
| III | Security and Privacy by Design | Gitleaks v8.30.1 with `--redact` over full history (FR-017, FR-018, BR-001); least-privilege handling (Art. III.5); no secret leakage in logs or verification output (Art. III.6); SHA-pinned actions and a read-only workflow token as operational policy; no production credentials required (BR-008); `.env` excluded, `.env.example` placeholders only (FR-013, FR-014, BR-007); documented rotate-first remediation runbook (FR-019). | PASS |
| IV | Financial Integrity | No financial artefact exists in this phase, so the monetary-precision and idempotency rules are not yet engaged. The plan takes the one preventive step that is available now: mypy `--strict` forbids `Any` propagation, and ruff's `DTZ` and `S` rule families are selected, so a `Decimal`-typed money path cannot silently widen to `Any` or accept an unsanitised timestamp when the billing service is built in Phase 2. | PASS (not yet applicable; prophylactic only) |
| V | Data Modeling and Database Evolution | BR-011 forbids any database object in this phase, and the plan creates none — the only storage is PostgreSQL 16.15 running empty for future phases. The plan additionally commits to Alembic 1.20.0 as the sole migration tool with reviewed migrations from Phase 2, pre-empting the Art. V.3 requirement rather than deciding it here. | PASS |
| VI | API and Integration Contracts | No runtime endpoint is introduced, so no network contract exists. The developer-facing contracts this phase does introduce — configuration, verification, and repository layout — are specified in `contracts/` with the same requirement for explicit schemas and error models that Art. VI demands of runtime APIs. | PASS |
| VII | Testing and Verifiability | A minimal suite that passes against an empty implementation (BR-005), the eight test layers from `docs/quality/test-strategy.md`, marker-based selection, and a traceability matrix linking every requirement to a test or an approved manual procedure (Art. VII.1, FR-029). Authorization tests are specified as positive *and* negative pairs from the start (Art. VII.2). | PASS |
| VIII | Observability and Operability | No runtime service exists, so health endpoints and metrics are not applicable. The observable surface this phase produces is the verification report itself: a failed check must be distinguishable from a check that could not run, and both distinguishable from success (spec's error model) — implemented as distinct exit codes and distinct report sections. | PASS (not applicable to runtime) |
| IX | Synthetic Data | The synthetic-data generator is Phase 7 and out of scope here. The one obligation this phase does engage is the environment data policy: the setup path requires no production data and the seed tooling's production refusal cannot be built before the generator exists. This is recorded as a deferred item, not a compliance. | PASS (deferred to Phase 7) |
| X | Maintainability and Delivery | Typed, formatted, linted, and tested code with an explicit rule selection; externalised configuration with a documented variable contract; a single setup path and a single required-check command; pinned and SHA-locked dependencies; documentation updated in the same change set (Art. X.6); CI as the sole merge gate (Art. X.3). | PASS |
| XI | Architecture Decisions and Exceptions | Four material decisions taken in this phase — uv workspace, ruff-plus-mypy toolchain, gitleaks with rotate-first remediation, and the httpx pin — are recorded as ADRs with context, options, consequences, and revisit conditions, satisfying Art. XI.1. Precedence order (constitution → ADR → spec → tasks → code) is stated in the contributor guide and the contracts (FR-028, BR-009). No exception is requested. | PASS |

### Operational policies

| Policy | Plan response | Status |
|---|---|---|
| Technology baseline (Python FastAPI + PostgreSQL) | Honoured; the plan selects tooling that operates on that baseline and changes nothing about it (BR-012). | PASS |
| Deployment topology (one PostgreSQL, four schemas, per-service least-privilege credentials) | Honoured in the test topology: one database, one schema per service, one database per parallel worker (research R-07). Phase 0 creates no schema. | PASS |
| Out-of-scope integrations (no payment gateway, no live network) | Honoured; the required check set contacts no external service (FR-011). | PASS |
| Environment data policy (synthetic data only; seed tooling refuses production targets) | Not applicable in this phase; deferred with the generator (Phase 7). | DEFERRED |
| Standards compliance (no implied TM Forum/3GPP) | Honoured; no standards claim is made anywhere in this phase's artifacts. | PASS |
| Required engineering gate | The Phase 0 exit gate in `docs/build-plan.md` is the gate this phase must satisfy, and its evidence record is a required artefact (FR-031, BR-010). | PASS |

### Gate on specification approval

Article I.2 permits implementation only against an **approved** specification,
and Article I.5 requires the specification's status to be updated when approval
occurs. The specification at `spec.md` is complete and its quality checklist is
16/16, but it carries status *Draft*. Accordingly:

- The plan, research, data model, contracts, and quickstart may be produced now,
  because they are specification artifacts and not implementation.
- **Implementation work (the `/speckit.tasks` task set and any code change)
  MUST NOT begin until the specification status is set to *Approved* and the
  constitution's ratification record is completed.**

This is recorded as a Phase 0 exit-gate condition rather than treated as a
violation, because the constitution's own workflow places specification review
before task derivation.

## Project Structure

### Documentation (this feature)

```text
specs/001-project-setup/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output — 17 resolved decisions with rationale
├── data-model.md        # Phase 1 output — repository artefacts and their lifecycle
├── quickstart.md        # Phase 1 output — runnable verification path
├── contracts/           # Phase 1 output — developer-facing contracts
│   ├── configuration-contract.md
│   ├── verification-contract.md
│   └── repository-layout-contract.md
├── spec.md              # The approved-in-progress specification
├── checklists/
│   └── requirements.md  # Specification quality checklist (16/16)
└── tasks.md             # Phase 2 output (/speckit.tasks command — NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
telco-si/
├── README.md                          # FR-002 entry point: what this is, how to start
├── CONTRIBUTING.md                    # FR-003/FR-004 contributor guide and rules
├── pyproject.toml                     # uv workspace root + ruff/mypy/pytest config
├── uv.lock                            # single shared lockfile (tracked)
├── .python-version                    # "3.13" — pins local interpreter
├── .env.example                       # FR-013/FR-014 placeholders only
├── .gitleaks.toml                     # secret-scanner configuration
├── .pre-commit-config.yaml            # local fast-feedback hooks
├── noxfile.py                         # the single local + CI check entry point
├── Makefile                           # thin alias layer over nox; no logic
├── .gitignore                         # FR-016 excludes overrides and artefacts
│
├── .github/
│   ├── workflows/
│   │   └── ci.yml                     # fast-checks → slow-checks → required-checks gate
│   ├── dependabot.yml                 # uv + github-actions ecosystems
│   └── rulesets/
│       └── main-required-checks.json  # makes the gate a merge requirement
│
├── ci/
│   ├── file-coverage.yml              # SC-010 coverage manifest (required check → path glob)
│   ├── check_file_coverage.py         # manifest enforcement, 5 conditions
│   ├── check_dependencies.py          # offline advisory check against vendored snapshot
│   ├── check_spec_artifacts.py        # template placeholders, feature layout, numbering
│   ├── run-checks.sh                  # entry point invoked by nox sessions
│   └── advisories/
│       └── python-advisories.json     # vendored snapshot, refreshed by scheduled workflow
│
├── deploy/
│   └── compose/
│       └── compose.yaml               # local PostgreSQL 16.15 only
│
├── docs/                              # existing governance documents (unchanged ownership)
│   ├── adr/                           # README's ADR pointer corrected here
│   ├── architecture/
│   ├── build-plan.md
│   ├── constitution.md
│   ├── domain-model/
│   ├── quality/
│   └── risks/
│
├── specs/                             # existing SDD feature artefacts
│   └── 001-project-setup/
│
├── templates/                         # existing reusable document templates
│   ├── adr-template.md
│   ├── decision-log-template.md
│   ├── feature-spec-template.md
│   └── implementation-plan-template.md
│
├── libs/
│   └── telco-common/                  # technical utilities ONLY (Art. II.7)
│       ├── pyproject.toml
│       ├── src/telco_common/
│       └── tests/
│
├── services/
│   ├── auth-service/
│   │   ├── pyproject.toml
│   │   ├── src/auth_service/
│   │   └── tests/
│   ├── crm-service/
│   │   ├── pyproject.toml
│   │   ├── src/crm_service/
│   │   └── tests/
│   ├── billing-service/
│   │   ├── pyproject.toml
│   │   ├── src/billing_service/
│   │   └── tests/
│   └── inventory-service/
│       ├── pyproject.toml
│       ├── src/inventory_service/
│       └── tests/
│
└── tests/                             # cross-service + repository-governance tests ONLY
    ├── contract/
    └── governance/
```

**Structure Decision**: The four services are top-level siblings under
`services/` because each is independently deployable and must own its
dependencies and its tests (Art. II.2, II.4). The shared library lives under
`libs/` rather than `packages/` so that the directory name itself records the
constitution's constraint that it contains technical utilities only and no
domain logic (Art. II.7). Tests are split by ownership rather than by type:
a service's own tests live with that service, and the root `tests/` directory
holds only cross-service contract tests and repository-governance tests — the
root cannot own service tests without violating Art. II.2. `ci/` and `deploy/`
are separated because one is machine-consumed configuration and the other is
runtime topology; both sit outside the governance prose in `docs/` so that
neither can drift into narrative documents.

## Constitution Re-check (Post-Design)

Performed after the Phase 1 artefacts (`data-model.md`, `contracts/`,
`quickstart.md`) were written.

| Re-check item | Finding | Status |
|---|---|---|
| Does any Phase 1 artefact introduce a runtime network endpoint or database object? | No. `data-model.md` documents repository artefacts only and states the BR-011 prohibition explicitly; `contracts/` documents developer-facing interfaces; `quickstart.md` describes local commands. | PASS |
| Do the contracts in `contracts/` meet the Art. VI bar (explicit schemas, error model, no implicit behaviour)? | Yes. Each contract states its identifiers, required/optional semantics, and its failure modes, and separates "failed" from "could not run". | PASS |
| Does the data model respect Art. V (no implicit objects, migration discipline)? | Yes. The only persistence is version-controlled files; the artefact-lifecycle table states the unit of consistency as the single commit, matching the specification. | PASS |
| Does `quickstart.md` introduce production credentials or live external systems (BR-008)? | No. It uses local PostgreSQL in a container, placeholder configuration, and no outbound service call. | PASS |
| Does any Phase 1 artefact supersede an approved decision? | No. The Phase 1 artefacts elaborate Phase 0 decisions; they change none. | PASS |
| Are the four Phase 0 decisions that need ADRs covered? | Yes — ADR-0002 (uv workspace), ADR-0003 (gitleaks and the rotate-first remediation path), ADR-0004 (httpx pin with the `httpx2` revisit trigger), and ADR-0005 (ruff + mypy toolchain, with the pyright alternative recorded). These are required by the task set, not by this plan. | PASS (ADR files not yet created — tracked as a Phase 0 task) |
| Does anything in Phase 1 require a constitution amendment or an exception? | No. | PASS |

**Post-design result: PASS.** No amendment and no exception are requested. The
only outstanding governance items are the specification approval and the
constitution ratification, both of which are Phase 0 exit-gate conditions
recorded in the build plan and the open-question register.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No constitution violation was found, so no exception is requested. The following
complexities are recorded for transparency: each was weighed against a
simpler alternative and none of them deviates from the constitution — they
exist because a stated requirement (FR, BR, AC, or SC) cannot be met by the
simpler form.

| Complexity | Why Needed | Simpler Alternative Rejected Because |
|---|---|---|
| A separate `required-checks` gate job that fans in from two lanes, rather than one flat list of jobs | BR-003 requires that a check which *cannot run* be treated as a failure. GitHub reports a skipped job as Success, so a flat job list would let an inconclusive check pass silently. | A flat job list — the platform's skip-as-success semantics make it incapable of distinguishing "passed" from "never ran". |
| A vendored advisory snapshot plus a scheduled refresh workflow | FR-011 requires the required checks to run without network access to external services, and a networked audit would make the same commit pass or fail depending on when it ran. | Networked `uv audit` as the required check — violates FR-011 and makes CI non-deterministic. GitHub dependency review alone — is advisory, available only after the pull request is opened, and cannot be reproduced locally (BR-004). |
| Two orchestration layers (nox, plus a Makefile alias) | SC-001 and SC-007 require a non-technical contributor to reach a verified state quickly; `make verify` is the most discoverable entry point, while nox provides cross-platform session isolation that raw Make cannot. | Makefile alone — tab sensitivity and a GNU Make dependency on Windows. nox alone — discoverable only to contributors who already know nox. The Makefile contains no logic, so there is still only one source of truth. |
| An explicit file-coverage manifest with a machine-enforced checker, rather than a documented convention | FR-032 and SC-010 require every artefact introduced by this phase to be covered by a check or an explicit recorded exemption. A convention cannot be enforced; a manifest can. | `CODEOWNERS` — expresses review ownership, not check coverage. Path filters in the workflow — break BR-003, and the checks are cheap enough to always run. |
| Savepoint-based per-test isolation with one database per parallel worker, rather than a shared container and truncate-based cleanup | BR-005 requires a failing check to always indicate a real defect; truncate-based cleanup leaks state between tests under parallelism and cannot express per-service least-privilege grants, which the constitution's deployment topology requires. | Truncate after every test — O(n) per table per test and uncoordinated across workers. A fresh database per test — CREATE/DROP dominates the five-minute budget. |
| mypy `--strict` in addition to ruff, rather than ruff alone | Art. IV's monetary-precision and immutability rules, and Art. VI's explicit-schema rule, are properties a linter cannot check. The pydantic plugin additionally enforces immutability on `frozen=True` models, which is the mechanism that makes a posted ledger entry tamper-evident. | ruff only — cannot verify types, cannot enforce `Any` propagation, and would leave Art. IV unenforced until the billing service exists. |
