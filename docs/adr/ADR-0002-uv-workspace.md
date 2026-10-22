# ADR-0002: uv as the single dependency and environment manager

- Status: Accepted
- Date: 2026-10-21
- Decision owners: Technical lead

## Context

The repository is a monorepo: a root application package, four independently
deployable services under `services/`, and a shared technical library under
`libs/telco-common/`. Every contributor and every CI job must resolve the same
dependency versions, or the local result and the automated result diverge —
which Constitution Article X.6 forbids.

The tool must therefore do four things: resolve a workspace-wide lock, install
that lock reproducibly, expose the interpreter without a global environment
manager, and run the required checks in isolated environments.

## Decision drivers

- One lockfile that covers every package in the workspace.
- Reproducible installs: the same commit must install the same versions.
- No global state: a contributor's machine state must not change the result.
- Works offline once the cache is warm, because the required checks must not
  depend on the network (Constitution Article X.6).
- Works in CI without a second, competing tool.

## Options considered

1. **uv workspace (selected)** — benefits: a single `uv.lock` across the
   workspace, `uv sync --frozen` for exact reproduction, `uv run` for an
   isolated environment, and an offline `uv lock --check`. Costs: uv is young,
   and the workspace layout is less conventional than a plain `requirements.txt`.
   Risks: uv's resolver could change behaviour across versions — mitigated by
   pinning uv in CI and committing `uv.lock`.
2. **pip-tools** — benefits: mature, and pip-based, so it needs no extra
   runtime. Costs: one lock per requirements file rather than one workspace
   lock, so the services and the library drift unless every file is locked and
   reconciled by hand. Risks: cross-package version conflicts are resolved
   per-file and can be mutually unsatisfiable.
3. **Poetry** — benefits: a single lockfile with rich dependency resolution
   and a first-class workspace concept. Costs: Poetry owns the packaging
   metadata of every member, which conflicts with a repository that must keep
   the standard `pyproject.toml`/`setuptools` baseline; it also imposes its own
   virtual-environment layout on every contributor.
4. **Plain pip with `requirements.txt`** — benefits: the smallest possible
   dependency surface, and no new tool to install. Costs: no transitive
   pinning, so two clones at the same commit install different versions; no
   workspace concept; no offline resolution check. Risks: builds are not
   reproducible at all, which breaks the local/CI parity requirement.

## Decision

The repository uses **uv** as its single dependency and environment manager.

- `uv.lock` is the only dependency lockfile and is committed.
- `[tool.uv.workspace]` declares `services/*` and `libs/*` as members.
- Installation is `uv sync --frozen`; it must never re-resolve.
- The `lockfile` required check runs `uv lock --check` and fails if the lock
  has drifted from any `pyproject.toml`.
- The required checks run under nox, which uses uv as its virtual-environment
  backend.
- CI pins uv itself by commit SHA, so a uv release cannot change the result.

## Consequences

- Positive: one lockfile, reproducible installs, an offline resolution check,
  and one documented command per operation.
- Negative: the repository depends on a tool that is younger than pip-tools
  and Poetry, and the workspace layout is uv-specific.
- Risks and mitigations: a uv release could change resolution. Mitigation —
  uv is pinned in CI, and the `lockfile` check fails loudly on any drift
  between `uv.lock` and the `pyproject.toml` files.

## Follow-up actions

- [x] Declare the workspace members in the root `pyproject.toml`.
- [x] Add the `lockfile` required check and make its session part of the fast
  lane.

## Revisit triggers

- uv changes its resolution semantics in a way that changes `uv.lock` output
  for an unchanged dependency set.
- The workspace grows a member type that uv does not support.
- pip-tools or Poetry gains a first-class, lockfile-compatible workspace that
  removes the per-file drift problem.
