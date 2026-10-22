# ADR-0004: Pin httpx to 0.28.1 and defer httpx2

- Status: Accepted
- Date: 2026-10-21
- Decision owners: Technical lead

## Context

Starlette's test client has begun deprecating the `httpx` 1.x line in favour
of a successor package (`httpx2`). With `httpx` 0.28.1 installed, importing
`starlette.testclient` emits:

```
StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is
deprecated; install `httpx2` instead.
```

The repository's test suite exercises the API surface through that client. The
question is whether to adopt the successor package now or to pin the current
one and defer.

The constraint is the local/CI parity requirement (Constitution Article X.6):
a dependency must not be adopted in a way that makes the local result differ
from the automated result.

## Decision drivers

- A warning in the test output is a warning that will be ignored, and then
  hidden.
- A dependency change must not alter what the checks verify.
- The successor package is new; its ecosystem coverage is incomplete.
- The deprecation must not become a runtime break.

## Options considered

1. **Pin `httpx` 0.28.1 and defer `httpx2` (selected)** — benefits: the
   installed version is the one the current Starlette release is tested
   against, the warning is known and bounded, and no API change is adopted
   under test pressure. Costs: a deprecation warning remains in the test
   output. Risks: a future Starlette release may remove the `httpx`
   compatibility path entirely, breaking the test client.
2. **Adopt `httpx2` now** — benefits: the deprecation warning disappears.
   Costs: the successor package is young; its coverage of the client API that
   Starlette's test client relies on is incomplete, so parts of the test suite
   would have to be rewritten or temporarily skipped — which would weaken
   FR-008 and BR-005, the minimal-suite guarantees. Risks: an immature
   dependency in the verification path can change results between two clones
   of the same commit.
3. **Remove the dependency on Starlette's test client** — benefits: no
   deprecation at all, and the tests would exercise the ASGI application
   directly. Costs: a rewrite of every API-level test, for a warning.

## Decision

The repository **pins `httpx` to 0.28.1** and defers the successor package.

- The pin is recorded in the root `pyproject.toml` and in `uv.lock`.
- The deprecation warning is acknowledged and tracked; it is not hidden, and
  it is not filtered out of the test output.
- The warning is not treated as a failure: it is a third-party deprecation,
  not a defect in this repository.

## Consequences

- Positive: the test suite runs against the combination Starlette's current
  release is tested with; no test was weakened to accommodate a migration.
- Negative: a known deprecation warning is present in the test output.
- Risks and mitigations: a future Starlette release could remove the `httpx`
  path. Mitigation — the `test` required check fails on any import error, so
  the break is detected at the gate rather than at release.

## Follow-up actions

- [ ] Re-evaluate the successor package when the `httpx2` release used by
  Starlette covers the test-client API surface the suite depends on.

## Revisit triggers

- Starlette removes `httpx` support from its test client.
- The successor package reaches a stable release whose API covers every
  client call the test suite makes.
