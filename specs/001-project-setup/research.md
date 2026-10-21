# Phase 0 Research: Project Setup and Governance

**Feature**: `SPEC-001` — Project Setup and Governance
**Spec**: `specs/001-project-setup/spec.md`
**Date**: 2026-10-21
**Status**: Complete — all unknowns resolved

This document resolves every unknown carried in the feature specification's
Open Questions table and every technology choice required by the Technical
Context. Each entry follows the required format: Decision, Rationale,
Alternatives considered.

All version numbers were verified against PyPI and the GitHub API on
2026-10-21. The local environment was probed directly: Python 3.13.7, uv
0.12.15, Docker 29.7.2, git 2.51.0, PostgreSQL 16.15 container already running
on `127.0.0.1:5432`.

---

## R-01 — Continuous verification platform

**Decision**: GitHub Actions, a single workflow file `.github/workflows/ci.yml`,
with three jobs — `fast-checks`, `slow-checks`, and a `required-checks` gate job
that fans in from the first two.

**Rationale**: The repository remote is `git@github.com:mezni/telco-si.git`, so
GitHub Actions is the platform of record with no further decision required. One
workflow file means exactly one required status-check context, which is what
makes FR-010 and BR-003 auditable in one place. The gate job runs with
`if: always()` and fails unless every upstream lane's result is exactly
`success`; `failure`, `cancelled`, `skipped`, `timed_out`, and
`startup_failure` all count as failure. This is the mechanism that satisfies
BR-003 ("a check that cannot run is treated as a failure"), because GitHub
reports a *skipped* job as Success and would otherwise let an inconclusive
check pass silently. No `paths` or `paths-ignore` filters are used anywhere,
because a path-filtered job reports as skipped and therefore as success.

**Alternatives considered**: One workflow per check (lint.yml, test.yml,
security.yml) — rejected, each becomes a separate required context, tripling
the chance that one is skipped or never reported, and tripling the YAML. Path
filters for a fast docs-only lane — rejected, directly violates BR-003. A
self-hosted runner — rejected as unnecessary operational surface for a
single-developer repository.

## R-02 — Runtime and operating system baselines

**Decision**: Python **3.13** is the declared floor (`requires-python =
">=3.13,<4"`); CI runs a matrix of **3.13 and 3.14**. A `.python-version` file
containing `3.13` pins local interpreters. Developer workstations are Linux or
macOS; CI runs on Linux; PostgreSQL runs in a container on both.

**Rationale**: Python 3.13 and 3.12 are both already in security-only support
as of 2026-10, so the meaningful difference is end-of-life runway: 3.13 has
security support to 2029-10 against 3.12's 2028-10, at the same support class.
3.13 also matches the local interpreter (`/usr/bin/python3.13` is 3.13.7), so
uv resolves it with no download — this directly serves SC-001, which allows 30
minutes for a fresh clone to reach a verified state. 3.15 was rejected as
twelve days old with a freshly-settled wheel ecosystem; 3.14 belongs in the
matrix as the current-bugfix leg, not as the floor. The `.python-version` file
is required because uv's own default interpreter changes between minor
releases; without it, local and CI interpreters can drift.

**Alternatives considered**: Python 3.12 floor — same support class, one year
less runway, and it does not match the machine default. Python 3.14 floor —
needlessly excludes the local interpreter. Python 3.15 — twelve days old.
Python 3.11 or 3.10 — 3.10 reached end of life on 2026-10-01.

## R-03 — Dependency and environment management

**Decision**: **uv**, in workspace mode. One root `pyproject.toml` with
`[tool.uv.workspace]` covering `services/*` and `libs/*`, one `uv.lock` at the
repository root, and one `pyproject.toml` per service and per library.

**Rationale**: uv 0.12.15 is already installed, and it is fast enough that the
30-minute setup budget is never at risk. Per-package selection is first class
(`uv sync --package auth-service`, `uv export --package auth-service`), so each
service's dependency closure is extractable for independent deployment even
though the lockfile is shared. A single resolved graph across all four
services matters concretely here: they share one PostgreSQL instance, so
divergent versions of FastAPI, Pydantic, or SQLAlchemy across services would
produce failures that appear in one service and not another. The lockfile also
gives a single artifact to audit for vulnerabilities.

**Alternatives considered**: pip-tools — no first-class monorepo concept and
slower resolution; retained as a fallback since `uv pip compile` is
API-compatible. Poetry and PDM — slower resolvers with weaker workspace
support, and no reason to adopt a second tool when uv is already present. Plain
pip plus requirements files — no meaningful lockfile semantics. The lockfile
format is not a lock-in: `uv export --format pylock.toml` emits the
standardised PEP 751 format, which any PEP 751-aware installer can consume.

## R-04 — Repository layout

**Decision**:

```text
telco-si/
├── README.md                     # entry point
├── CONTRIBUTING.md               # contributor guide and contribution rules
├── pyproject.toml                # uv workspace root, tool configuration
├── uv.lock                       # single shared lockfile (tracked)
├── .python-version               # "3.13"
├── .env.example                  # every variable, placeholder values only
├── .gitignore
├── .gitleaks.toml                # secret-scanner configuration
├── .pre-commit-config.yaml
├── noxfile.py                    # the single local + CI check entry point
├── Makefile                      # thin alias layer over nox, no logic
├── .github/
│   ├── workflows/ci.yml
│   ├── dependabot.yml
│   └── rulesets/main-required-checks.json
├── ci/
│   ├── file-coverage.yml         # SC-010 coverage manifest
│   ├── check_file_coverage.py
│   ├── check_dependencies.py
│   ├── check_spec_artifacts.py
│   ├── run-checks.sh
│   └── advisories/python-advisories.json
├── docs/                         # existing governance documents
├── specs/                        # existing SDD feature artifacts
├── templates/                    # existing reusable document templates
├── libs/
│   └── telco-common/             # technical utilities ONLY (constitution Art. II.7)
├── services/
│   ├── auth-service/
│   ├── crm-service/
│   ├── billing-service/
│   └── inventory-service/
└── tests/                        # cross-service and repository-governance tests ONLY
```

Each service directory holds its own `pyproject.toml`, `src/<package>/`, and
its own `tests/`, because Constitution Article II.2 requires each service to
own its tests. The root `tests/` directory holds only cross-service contract
tests and repository-governance tests.

**Rationale**: The research surfaced a genuine conflict between two existing
conventions in the repository. The README lists `adr/` at the root, but the
actual ADR lives at `docs/adr/`. Rather than create a second ADR directory,
the README is corrected to point at `docs/adr/`, which also satisfies FR-001
and AC-017 ("the documented layout matches the actual tracked structure"). The
second conflict was the location of tests: a root-only `tests/` directory
cannot satisfy Article II.2 for four services, so service tests live with their
service and the root directory is reserved for cross-service and governance
tests. This split is recorded in the layout contract rather than left
implicit.

**Alternatives considered**: `packages/` for everything — conflates deployable
services with libraries and loses the independent-deployability signal.
`apps/` instead of `services/` — purely stylistic, but `services/` matches the
constitution's own vocabulary. A single `src/` with services as subpackages —
makes per-service dependency isolation and per-service images impossible.

## R-05 — Linting, formatting, and type checking

**Decision**: `ruff` **0.17.1** for both linting (`ruff check`) and formatting
(`ruff format`), with an explicitly pinned `select` list. `mypy` **2.4.0** in
`--strict` mode with the `pydantic.mypy` plugin, configured in `mypy.ini`.

**Rationale**: ruff reimplements Black's formatting and flake8's plugin
ecosystem — including flake8-bugbear — in one binary, so one tool replaces
three with no loss of coverage. Ruff 0.16.0 expanded its default rule set from
59 to 413 rules, so leaving `select` unset would silently enable opinionated
rules; the plan pins an explicit list. mypy is chosen over pyright and
basedpyright for one decisive reason: the pydantic plugin. In a FastAPI
codebase the pydantic models *are* the API contract, and the plugin
synthesises a typed `__init__`, flags untyped fields, and enforces immutability
on `frozen=True` models — directly relevant to the constitution's immutability
requirement for posted ledger entries. Pyright has no plugin system and could
only approximate this. On a 48k-line corpus, mypy found four real errors while
pyright's strict mode produced 1208 diagnostics on the same clean code, the
large majority from duplicated lint concerns that ruff already owns. mypy
`--strict` also disallows `Any` generics and warns on `Any` returns, which is
the guardrail that matters when `Decimal` could otherwise silently become
`Any` in a money path.

**Alternatives considered**: Black plus flake8 — two tools and two configs for
a result ruff gives from one. pyright 1.1.414 — the stronger typing-spec
conformance is real, but the loss of the pydantic plugin and the need for three
overrides to stop duplicating ruff make it the runner-up rather than the
choice; revisit if the team standardises on VS Code and Pylance.
basedpyright — strictly more opinionated, producing 2400 warnings on the same
corpus, a heavy tax for a greenfield project. `ty` and `pyrefly` — both
promising and both too new to be the authoritative gate for a billing domain.

**Two verified traps carried into the configuration**: `TC` (flake8-type-checking)
rules must **not** be selected, because moving imports into `TYPE_CHECKING`
blocks breaks FastAPI's runtime annotation resolution and produces a
request-time `PydanticUserError` that no type checker catches. And
`sqlalchemy.ext.mypy.plugin` was removed in SQLAlchemy 2.1, so it must not be
listed; the native `Mapped[...]` typing is used instead.

## R-06 — Test framework, HTTP client, and async mode

**Decision**: `pytest` **9.1.1** with `pytest-asyncio` **1.4.0** in
`asyncio_mode = "auto"` and `asyncio_default_fixture_loop_scope = "function"`.
`httpx` **0.28.1** with `AsyncClient` + `ASGITransport` for async API tests and
`starlette.testclient.TestClient` as a context manager where the ASGI lifespan
must run.

**Rationale**: pytest-asyncio's `auto` mode is its own documented
recommendation when asyncio is the only async library in play, which is the
case here. The fixture loop scope must be set explicitly or pytest-asyncio
raises a deprecation warning. `ASGITransport` does **not** trigger the
application lifespan — FastAPI's own documentation is explicit about this — so
tests needing startup and shutdown use `TestClient` as a context manager or
`asgi-lifespan`. `httpx` is pinned rather than `httpx2` because `httpx2` was
published on the day of research and neither `respx` nor `pytest-httpx` yet
support it; adopting a zero-ecosystem HTTP client in Phase 0 would put the
"minimal test suite must pass" guarantee (BR-005) at risk. The cost of the
choice is one deprecation warning on the `fastapi.testclient` import, which is
filterable. All outbound HTTP is routed through a single module so the future
migration is a one-file change.

**Alternatives considered**: `httpx2` now — rejected for Phase 0 only, with
an explicit revisit trigger: migrate when the mocking ecosystem ships
`httpx2` support or when Starlette drops plain-`httpx` support. This is
recorded as an ADR so it is not re-litigated in Phase 1. The anyio pytest
plugin — conflicts with pytest-asyncio in auto mode and adds a trio backend
the project will never run. `unittest` — no fixtures, no markers for the eight
test layers defined in the test strategy, no parametrisation.

## R-07 — Database test isolation

**Decision**: One PostgreSQL **16.15** container per CI job and per local test
session, containing one database with four schemas (`auth`, `crm`, `billing`,
`inventory`), one schema per service. Per-test isolation by **savepoint
rollback** via SQLAlchemy 2.x `join_transaction_mode="create_savepoint"`,
injected into FastAPI through `app.dependency_overrides`. Per-parallel-worker
isolation by **one database per worker**.

**Rationale**: PostgreSQL grants and `search_path` are database-scoped, so the
only layout in which a `crm` role's inability to write `billing` can be
asserted is one database holding all four schemas. The savepoint pattern is
the load-bearing detail: without it, an explicit `session.commit()` inside a
request handler commits for real and the test leaves committed state behind.
With it, a commit releases a savepoint, the data is visible inside the test,
and the outer transaction still owns it, so teardown erases everything.
`dependency_overrides` is the FastAPI-native mechanism, which means the
production commit/rollback logic is exercised unmodified and cannot drift from
test behaviour. A separate database per parallel worker keeps grants,
`search_path`, and `CREATE SCHEMA` from bleeding across workers.

**Alternatives considered**: Truncating after every test — O(n) per table per
test, and uncoordinated across parallel workers. A fresh database per test —
CREATE/DROP per test is slow and fails if connections linger. Real
`SERIALIZABLE` isolation — changes the semantics under test and would surface
as flaky failures. `pytest-postgresql` — requires locally installed PostgreSQL
*server* binaries, which makes the verification environment non-hermetic;
this machine has only the client. Compose-managed test databases — rejected
for tests because CI and local would then use different provisioning code,
which contradicts BR-004, though compose is retained for local development.

**Five traps recorded for the contributor guide**: background tasks must
receive the request's session through dependency injection rather than opening
their own, or they write outside the test transaction; request handlers must
not open transactions explicitly, only `flush()`; `expire_on_commit=False` is
required or attributes expire and raise `DetachedInstanceError`; test reads
must use the same session and connection or they cannot see uncommitted data;
and code paths that genuinely need a real commit require a separate fixture
with truncate-based teardown, marked so they run outside the parallel pass.

## R-08 — Coverage policy

**Decision**: `coverage.py` **7.16.2** via `pytest-cov` **7.1.0**. Phase 0
**measures and publishes** coverage with no numeric threshold. From Phase 1 the
gate becomes three mechanisms: a ratcheting total per service, `diff-cover`
**10.6.0** at 90% on changed lines for every pull request, and a separate
strict pass requiring 100% branch coverage on designated critical modules
(billing money arithmetic, authorisation decisions, idempotency handling).

**Rationale**: The project's own test strategy states that "coverage
percentage alone is not proof of correctness; critical acceptance criteria and
financial invariants require explicit tests." A single global threshold
contradicts that directly, because a team can reach a threshold with trivial
tests in easy files while leaving the money logic untested. `diff-cover`
measures the lines actually changed, so it cannot be gamed by unrelated growth
and does not punish a young codebase. The critical-module pass is the only
numeric bar that corresponds to "coverage is proof" for the parts that matter.
Phase 0 has no implementation, so any threshold would either fail trivially or
be vacuous.

## R-09 — Secret scanning and remediation

**Decision**: `gitleaks` **v8.30.1** as the single secret scanner, run in `git`
mode with `--redact` against the full history, configured by a repository-owned
`.gitleaks.toml`. Remediation uses `git-filter-repo` **2.47.0**.

**Rationale**: gitleaks is MIT-licensed, offline by default, scans full history
including all branches in its default invocation, and is the only candidate
with a redaction flag honoured identically in stdout and JSON output —
`Secret` and `Match` both become `REDACTED`, which is what FR-018 requires.
TruffleHog is disqualified on licence grounds for a permissive-stack project
(AGPL-3.0) and because its credential-verification feature calls out to
providers, which breaks the no-external-service constraint. detect-secrets is
Apache-2.0 and legitimate but has had no release in roughly two and a half
years and has no first-class redaction; its baseline file also becomes a
de facto allowlist for real secrets. GitHub's own secret scanning is enabled as
a free second layer because the repository is public, but it cannot be
reproduced locally and cannot run offline, so it is defence in depth rather
than the gate.

**The remediation runbook is rotate-first, not rewrite-first.** The governing
guidance is explicit that revoking or rotating the credential is the first and
usually sufficient step, and that rewriting history "may not be warranted",
because rewriting permanently changes commit SHAs, breaks pull-request diffs,
loses commit signatures, and carries a high recontamination risk from stale
clones. The runbook therefore records: rotate the credential at the issuing
provider; if a rewrite is warranted, use `git-filter-repo
--sensitive-data-removal --replace-text`, count the collateral damage to
pull-request refs, force-push all refs, contact GitHub Support with the
affected pull-request count and the first changed commit; collaborators rebase
rather than merge, because a single merge commit reintroduces the entire
tainted history. A history audit of this repository found no live credentials,
only four weak placeholder literals, so no rewrite is warranted now; a custom
gitleaks rule prevents those from reappearing.

**Alternatives considered**: TruffleHog — AGPL-3.0 and outbound verification
calls. detect-secrets — stale, no redaction. GitHub secret scanning alone —
cannot run offline or be reproduced locally. `gitleaks protect --staged` as the
only control — covers staged content but not history, so it cannot satisfy
BR-001.

## R-10 — Dependency vulnerability scanning

**Decision**: The **required** dependency check is offline, running against a
vendored advisory snapshot at `ci/advisories/python-advisories.json`. A
separate **scheduled, non-required** workflow refreshes the snapshot using
`uv audit` and opens a pull request. Dependabot is configured for the `uv` and
`github-actions` ecosystems.

**Rationale**: FR-011 requires the checks to complete with no network access
to external services. A scanner that queries `api.osv.dev` on every run is a
live external dependency and makes the check non-deterministic — the same
commit can pass today and fail tomorrow when an advisory is published, which
is not reproducible CI. `uv export --frozen --no-hashes` was verified to work
fully offline against a warm cache because it only reads `uv.lock`, and
`uv lock --check` provides the same guarantee for the lockfile itself.
Vendoring the advisory set makes the check deterministic, offline, and fast.

**This is the one design decision in the plan that carries an explicit
trade-off, and it is flagged for the project owner**: a vendored snapshot is
only as good as its freshness, and the refresh workflow needs a pull request to
be landed. The alternative — making networked `uv audit` the required check —
satisfies the dependency-scanning requirement more directly but violates the
literal reading of FR-011 and introduces non-determinism. The plan implements
the offline snapshot **and** enables GitHub dependency review and Dependabot,
so the two readings are covered simultaneously. Switching the required check to
networked `uv audit` is a one-line change if the owner decides FR-011 admits
advisory lookups as a "controlled substitute".

## R-11 — Pre-commit hooks

**Decision**: `pre-commit` **4.7.0** with a committed
`.pre-commit-config.yaml` containing: ruff check with `--fix`, ruff format,
`uv-lock` from `astral-sh/uv-pre-commit` pinned to **0.12.15** to match the
local uv, gitleaks in staged mode with `--redact`, and the standard
pre-commit-hooks (trailing whitespace, end-of-file fixer, YAML and JSON
validation, large-file limit). CI additionally runs
`uvx pre-commit run --all-files` for parity.

**Rationale**: Hooks are a developer convenience; **CI is the gate**. The
rationale for keeping mypy out of the hooks is that a type check over a
48k-line codebase takes 35 seconds to two minutes, which is punitive per commit
and encourages `--no-verify`, and that pre-commit runs hooks in isolated
environments where a type checker cannot see the project's dependencies
without duplicating them, guaranteeing version drift between hook and CI.
ruff alone runs in roughly three seconds. Pinning `uv-pre-commit` to the same
version as the local uv is what keeps hook-generated lockfiles byte-identical
to developer-generated ones.

**Alternatives considered**: `prek` (a Rust reimplementation reading the same
configuration) — faster, and adopted by CPython, FastAPI, and ruff itself;
rejected only because the committed artifact is the standard YAML either way
and `pre-commit` is the more widely documented and audited option.
pre-commit as the primary gate — rejected, since `--no-verify` bypasses it
entirely and it cannot enforce that a check actually ran.

## R-12 — Local orchestration and CI parity

**Decision**: `nox` **2026.10.20** with the uv virtualenv backend is the single
task runner. `uv run nox` runs the full required check set; `uv run nox -s
<session>` runs one. The CI workflow is a thin caller of the same nox
sessions. A `Makefile` provides a thin alias layer (`make verify` →
`uv run nox`) and nothing else.

**Rationale**: nox lives in the development dependency group, so `uv run nox`
bootstraps it with zero extra installation and works identically on a
developer's machine and a CI runner. Sessions give per-session virtual
environments, which is what a four-service repository needs. Making CI a thin
caller of the same nox sessions is the discipline that prevents "works locally,
fails in CI" drift and satisfies BR-004. The Makefile exists purely for
discoverability by contributors who do not know nox; it contains no logic, so
there is no second source of truth.

**Alternatives considered**: tox — INI-flavoured and oriented at packaging
matrices rather than tasks. just — excellent ergonomics but adds an install
step for every developer and every CI runner. A Makefile as the primary runner
— tab sensitivity and a GNU Make dependency on Windows. Raw shell scripts —
loses cross-platform parity and per-session environment isolation.

## R-13 — Database test topology and PostgreSQL version

**Decision**: PostgreSQL **16.15**, pinned as `postgres:16.15-alpine`, in both
the local compose file and the CI service container. Local development uses
`deploy/compose/compose.yaml`; CI uses a GitHub Actions service container with
a `pg_isready` health check, followed by a separate explicit credential
connection step, followed by migrations as their own step.

**Rationale**: 16.15 is the version already running on the local machine and
the tag was verified to exist on Docker Hub, so local and CI use an identical
engine. A floating `16` or `latest` tag would turn a routine refresh into an
unplanned major upgrade. The three-layer CI database startup exists because
`pg_isready` proves the server accepts connections but does **not**
authenticate: a role can be reported ready and still fail authentication
later. Separating the credential check and the migration step gives each layer
its own log section and its own exit status. The compose file lives under
`deploy/` rather than the repository root so that the root stays an SDD
governance surface, with the Makefile preserving a one-command developer
experience.

**Alternatives considered**: `postgres:18.6-alpine` — current stable, but the
local machine runs 16.15 and matching versions removes a whole class of
"works locally, fails in CI" divergence. Testcontainers — container startup
dominates the five-minute budget; retained as an escape hatch behind a marker
for tests needing a non-default PostgreSQL configuration. `pytest-docker` —
needs local PostgreSQL binaries. A job-level `container:` in CI — changes
database addressing and requires the job image to carry the full toolchain.

## R-14 — CI security hardening

**Decision**: Workflow-level `permissions: contents: read`. Every action
pinned to a full 40-character commit SHA with the version in a trailing
comment. `persist-credentials: false` on every checkout. No
`pull_request_target`. `continue-on-error` is banned from the gate's `needs`
chain. Concurrency keyed on the pull-request number with
`cancel-in-progress` enabled only for `pull_request` events.

**Rationale**: GitHub's secure-use guidance is to default the workflow token
to read access and to pin actions to a commit SHA, because a tag can be moved
or deleted. SHA pinning is also machine-enforced by the `zizmor` audit, which
exits non-zero on unpinned `uses:` references. `persist-credentials: false`
removes the token from the workspace's git configuration, where nothing in
this repository needs it. `continue-on-error` in the gate chain would directly
violate BR-003. The concurrency expression is chosen so that a superseded pull
request commit is cancelled, while the post-merge verification run on `main`
and any merge-queue run are never cancelled — cancelling a merge-queue run
breaks the queue and causes the required check never to report.

**Alternatives considered**: Tag pinning — tags are mutable. Workflow
dependency lockfiles — the strongest available mechanism, but public preview;
adopt when it stabilises, ship SHA pinning now. Per-job permission
elevation — no job in Phase 0 needs more than read access.

## R-15 — SC-010 file-coverage enforcement

**Decision**: A manifest at `ci/file-coverage.yml` declares which required
check covers which path glob, plus explicit exclusions that must each carry a
non-empty reason, an owner, and a review date. A checker,
`ci/check_file_coverage.py`, enforces five conditions: every tracked file is
covered by at least one check or matched by exactly one exclusion; every
exclusion has a reason, owner, and review date; every exclusion glob matches
at least one tracked file, so stale exclusions fail; every declared check
corresponds to a real job in the workflow and every workflow job appears in the
manifest; and every declared check appears in the `needs:` list of the gate
job.

**Rationale**: SC-010 asks a question about coverage of *checks*, not of
tests — for every tracked file, which required check would notice if it broke.
Files that no check inspects are silent failure surface. The fifth condition
is the important one: it makes it impossible to add a job that the gate
ignores, which would otherwise be a silent non-required check and a direct
BR-003 violation. The manifest lives under `ci/` rather than `docs/quality/`
because it is machine-consumed configuration and must not drift into the prose
tree; the enforcement reasons are left to be authored and reviewed by the
project owner rather than pre-filled by the planner.

**Alternatives considered**: A `.gitignore`-style exclusion list alone — can
express "not covered" but cannot prove the covered set is complete. Enforcing
via `CODEOWNERS` — expresses review ownership, not check coverage. Per-job
`paths:` filters — break BR-003, and the checks are cheap enough to always
run.

## R-16 — Constitution ratification ownership

**Decision**: Ratification is a **Phase 0 exit-gate condition** owned by the
project owner, with the technical reviewer as the second signatory. Until
signed, the constitution's ratification field records its state as pending and
the governance record is explicitly marked "not yet binding".

**Rationale**: The build plan's Phase 0 outcome list includes "Approve the
constitution and initial assumptions", so ratification is inside this phase's
scope, and the constitution's own ratification record requires two
signatories. Leaving it unbound would mean the repository ships a constitution
that its own governance says is not in force.

**Alternatives considered**: Treating ratification as an automatic consequence
of adopting the constitution — rejected, because the constitution requires
explicit approval and states that exceptions and changes require explicit
approval. Leaving it to a later phase — rejected, because the build plan
places it in Phase 0.

## R-17 — Reserved environment variable names

**Decision**: A naming convention of `<SERVICE>_<DOMAIN>_<NAME>`, with the
service prefix drawn from the constitution's four service names:
`AUTH_*`, `CRM_*`, `BILLING_*`, `INVENTORY_*`. Cross-cutting settings use the
prefix `TELECO_*` or `COMMON_*`. Phase 0 declares only the cross-cutting and
tooling variables plus the four per-service database URLs and their shared
credential variables, and reserves the naming space for the rest.

**Rationale**: Declaring the full variable set before the services exist
invents requirements that no specification has approved, which the
constitution's Article I.3 forbids. Declaring only the tooling variables
leaves the per-service database credentials undeclared, which Phase 0's
FR-015 and the ADR-0001 topology require. Reserving the naming space now
means later services add variables without renaming or colliding, and the
example configuration's contents stay traceable to real requirements.

**Alternatives considered**: Fully enumerating every anticipated variable —
rejected as speculative requirement creation. A flat unprefixed namespace —
rejected, because four services sharing one configuration space cannot be
distinguished.

---

## Resolved Open Questions from the Specification

| Open question | Resolution | Reference |
|---|---|---|
| Which continuous verification platform and runner are used? | GitHub Actions, single workflow, gate job | R-01, R-14 |
| Which runtime and operating system baselines are supported? | Python 3.13 floor, matrix 3.13/3.14, Linux CI, Linux/macOS workstations | R-02 |
| Who ratifies the constitution, and on what date? | Project owner plus technical reviewer, as a Phase 0 exit-gate condition | R-16 |
| Which environment variable names are reserved for unimplemented services? | `<SERVICE>_<DOMAIN>_<NAME>` convention; only tooling and database variables declared now | R-17 |
| What is the remediation path when secret material has already been committed? | Rotate-first runbook, `git-filter-repo` rewrite only if warranted | R-09 |

## Unresolved and Deliberately Deferred

| Item | Why deferred | Revisit trigger |
|---|---|---|
| `httpx2` adoption | Mocking ecosystem has no support yet | When `respx` ships `httpx2` support, or Starlette drops plain-`httpx` |
| `ty` / `pyrefly` as a second type checker | Both pre-1.0 or newly 1.0 | Phase 1 re-evaluation; `pyrefly` is the strongest candidate |
| Networked dependency auditing as the required check | Conflicts with FR-011 | Project owner decision; one-line change to `uv audit --locked` |
| Workflow dependency lockfiles | Public preview | When the feature stabilises |
| Per-service CI cache keys | Requires stable per-package export hashing | Phase 1, when service dependencies diverge |
| Cross-schema foreign keys, audit store location, broker | Undecided architecture questions Q-011, Q-008 | Phase 1, per ADR-0001's revisit conditions |
