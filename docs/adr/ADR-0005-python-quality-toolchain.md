# ADR-0005: ruff and mypy strict as the Python quality toolchain

- Status: Accepted
- Date: 2026-10-21
- Decision owners: Technical lead

## Context

The repository is Python 3.13 on FastAPI with SQLAlchemy and Pydantic. The
required checks must verify formatting, lint quality, and type correctness, on
a contributor's machine and in CI, with the same result. The toolchain must
also be fast enough that the checks that catch most mistakes finish inside the
two-minute fast lane.

The repository currently carries `[tool.black]`, `[tool.isort]`, and
`[tool.flake8]` sections in `pyproject.toml` that no required check executes.

## Decision drivers

- One formatter, one linter, one type checker. Overlapping tools disagree.
- The checks must run offline and must not require a separate tool
  installation step that can fail.
- Strict type checking must not be a formality: the Pydantic models and the
  SQLAlchemy models are the boundaries where a silent wrong answer lives.
- The tools must support Python 3.13 syntax.

## Options considered

1. **ruff for formatting and linting, mypy strict for types (selected)** —
   benefits: ruff performs formatting and linting in one fast binary; mypy is
   the reference implementation for Python type checking and has a first-class
   Pydantic plugin; both are pure-Python or single-binary tools that install
   from the lockfile. Costs: ruff's formatter and mypy's type checker are
   different projects with independent release cycles. Risks: ruff's rule set
   changes between releases and can surface new findings — mitigated by
   pinning the version in `uv.lock`.
2. **black + isort + flake8 + mypy** — benefits: each tool is long-established
   and widely understood; black's formatting is famously stable. Costs: four
   tools for the same job, four independent upgrade cycles, four configuration
   files, and `isort` and `ruff`'s import handling overlap. Risks: the
   repository already carries these configuration sections but no required
   check runs them, so the declared standard and the enforced standard have
   already drifted apart — that drift is the real cost.
3. **pyright instead of mypy** — benefits: a type checker written in
   TypeScript that runs faster and reports some errors mypy misses.
   Costs: the Pydantic plugin story is weaker, so the Pydantic models — the
   ones that matter most for boundary correctness — would be checked with
   less precision; it also requires a Node.js runtime in the verification
   image, which adds a second toolchain to install and pin. Risks: an
   additional runtime in the check path is another thing that can fail before
   the check itself runs.
4. **pyright + ruff only** — benefits: two tools instead of three, and fast.
   Costs: drops static type checking entirely, which would leave the
   constitution's type-check requirement (FR-007, Article X.1) unimplemented.

## Decision

The repository uses **ruff** for formatting and linting and **mypy in strict
mode with the Pydantic plugin** for type checking.

- Formatting: `ruff format --check .`
- Linting: `ruff check .`
- Type checking: `mypy src libs/telco-common/src` under `mypy.ini` with
  `strict = True` and `plugins = pydantic.mypy`
- The rule selection is explicit in `[tool.ruff.lint]`: `E`, `F`, `I`, `B`,
  `A`, `PT`, `SIM`.
- The `black`, `isort`, and `flake8` sections in `pyproject.toml` are removed,
  because a declared tool that no check runs is a documentation defect.

## Consequences

- Positive: one formatter, one linter, one type checker; all three install
  from the lockfile; the type checker understands Pydantic and SQLAlchemy
  models.
- Negative: mypy strict surfaced real typing gaps in the existing code, which
  had to be fixed — the models were rewritten to SQLAlchemy 2.0's typed
  `Mapped[...]` declarations, and the endpoints and middleware were
  annotated.
- Risks and mitigations: mypy strict is slow on a large codebase.
  Mitigation — the type check is in the slow lane, the scope is the two
  application packages rather than the whole tree, and the cache is reused.

## Follow-up actions

- [x] Remove the unused `black`, `isort`, and `flake8` configuration sections.
- [x] Create `mypy.ini` with strict mode and the Pydantic plugin.
- [x] Fix the typing gaps the strict check surfaced.

## Revisit triggers

- ruff's formatter diverges from black's output for code the repository holds.
- mypy's Pydantic plugin stops tracking the Pydantic release in use.
- The type-checking scope grows past what fits in the slow lane's timeout.
