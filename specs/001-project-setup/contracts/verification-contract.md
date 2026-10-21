# Contract: Required Verification Checks

**Feature**: `SPEC-001` — Project Setup and Governance
**Status**: Active | **Date**: 2026-10-21
**Governed by**: `specs/001-project-setup/spec.md` (FR-007 … FR-012, FR-017, FR-029, FR-032, BR-003, BR-004, BR-005), Constitution Articles VII and X

---

## Purpose

This contract defines the **required checks** of the repository: what each one
verifies, how it is invoked locally, how it runs in continuous verification, and
precisely what its outcome means. It is the interface between a contributor's
machine, a reviewer's screen, and the merge gate.

A required check is one whose failure blocks a merge. The set below is
exhaustive: a check not listed here is **advisory**, reports without blocking,
and MUST NOT be added to the gate job's `needs:` list without amending this
contract.

## Outcome Vocabulary

Three outcomes are distinguishable, and the specification's error model
requires that a failed check, a check that could not run, and success are
three different things.

| Outcome | Exit code | Meaning |
|---|---|---|
| **Pass** | `0` | The check ran to completion and every condition it verifies was met. |
| **Fail** | `1` | The check ran and found a violation. The output names the violation and its location. |
| **Could not run** | `2` | The check could not establish its precondition — a missing tool, a missing file, an unset required variable, a database that did not become healthy. |
| **Internal error** | `3` | The check itself is defective. |

**Both `1` and `2` are failures at the gate.** This is the whole point of the
contract: GitHub reports a skipped job as Success, so a check that silently did
not run would otherwise pass. The gate job therefore fails unless every
upstream lane reports exactly `success`, and `failure`, `cancelled`,
`skipped`, `timed_out`, and `startup_failure` all count as failure (BR-003).

Every check MUST distinguish `1` from `2` in its output. A contributor must be
able to tell "your code is wrong" from "your environment is not ready".

## The Checks

| ID | Verifies | Local invocation | CI job | Lane | Timeout |
|---|---|---|---|---|---|
| `format` | Every tracked source file matches the formatter's output | `uv run nox -s format` | `fast-checks` | fast | 2 min |
| `lint` | No lint rule is violated under the pinned `select` list | `uv run nox -s lint` | `fast-checks` | fast | 3 min |
| `lockfile` | `uv.lock` is consistent with every `pyproject.toml` in the workspace | `uv run nox -s lockfile` | `fast-checks` | fast | 1 min |
| `governance` | Templates carry unfilled placeholders only; exactly one constitution exists; feature directories and numbering are valid; the configuration contract and `.env.example` agree | `uv run nox -s governance` | `fast-checks` | fast | 2 min |
| `file-coverage` | Every tracked file is covered by a required check or by a justified, unexpired exclusion; every declared check exists as a CI job and is in the gate's `needs:` list | `uv run nox -s file-coverage` | `fast-checks` | fast | 2 min |
| `typecheck` | The code passes mypy in strict mode with the pydantic plugin | `uv run nox -s typecheck` | `slow-checks` | slow | 8 min |
| `test` | The test suite passes on an otherwise empty implementation | `uv run nox -s test` | `slow-checks` | slow | 10 min |
| `secret-scan` | No secret material exists in the working tree or anywhere in the version-controlled history; no detected value is printed | `uv run nox -s secret-scan` | `slow-checks` | slow | 5 min |
| `dependency-audit` | No locked dependency matches a known advisory in the vendored snapshot; the lockfile resolves offline | `uv run nox -s dependency-audit` | `slow-checks` | slow | 3 min |

Nine required checks. The two lanes exist so that a contributor's feedback
loop stays under two minutes for the checks that catch most mistakes, while
the expensive checks run in parallel.

## Local and CI Equivalence

BR-004 requires that every required check be reproducible locally with the
same result as the automated run. This is achieved by a single definition
site: the nox session in `noxfile.py` *is* the check, and the CI workflow
calls the same sessions. There is no second copy of any check's logic.

```text
noxfile.py                    .github/workflows/ci.yml
┌──────────────────────┐     ┌────────────────────────────┐
│ session format       │◄────│ uv run nox -s format       │
│ session lint         │◄────│ uv run nox -s lint         │
│ session lockfile     │◄────│ uv run nox -s lockfile     │
│ session governance   │◄────│ uv run nox -s governance   │
│ session file-coverage│◄────│ uv run nox -s file-coverage│
│ session typecheck    │◄────│ uv run nox -s typecheck    │
│ session test         │◄────│ uv run nox -s test         │
│ session secret-scan  │◄────│ uv run nox -s secret-scan  │
│ session dependency-… │◄────│ uv run nox -s dependency-audit
└──────────────────────┘     └────────────────────────────┘
```

The only permitted difference is the environment: CI adds a PostgreSQL
service container and sets `TELECO_ENV=ci`. The check logic is identical.

## Invocations

| Invocation | Effect |
|---|---|
| `uv run nox` | Runs every required check. The documented single command. |
| `uv run nox -s <id>` | Runs one check by its ID from the table above. |
| `make verify` | Alias for `uv run nox`. Convenience only; contains no logic. |
| `uv run nox -s test -k <pattern>` | Runs a subset of the test suite. Advisory, never a gate. |
| `uv run pre-commit run --all-files` | The full pre-commit hook set. Advisory; the hook set is a strict subset of the required checks. |

## Output Contract

Each check MUST report, in this order:

1. **Result** — `PASS`, `FAIL`, or `COULD NOT RUN`, as a single word.
2. **Check ID** — the ID from the table above.
3. **Actionable message** — what is wrong, and where. A message that does not
   let the contributor locate the problem is a defect in the check.
4. **Diagnostics** — the tool's own output, verbatim, for the failing
   locations.

A failing check MUST NOT print a detected secret value. The `secret-scan`
check MUST redact both the `Secret` and the `Match` field of every finding,
in stdout and in JSON output alike (FR-018).

## Pipeline Contract

```yaml
on:
  pull_request:              # branches: [main]
  push:                      # branches: [main]
  merge_group:
```

| Property | Value | Reason |
|---|---|---|
| Workflow file | `.github/workflows/ci.yml` | One file means one required status context |
| Jobs | `fast-checks`, `slow-checks`, `required-checks` | Two parallel lanes feeding one gate |
| `required-checks` condition | `if: always()` and every upstream result is exactly `success` | A skipped lane must not read as a pass |
| `continue-on-error` | Forbidden in the gate's `needs:` chain | It would make a failing lane non-blocking |
| Path filters | Forbidden anywhere in the workflow | A path-filtered job reports as skipped, and skipped reads as success |
| Concurrency | Grouped by pull-request number; `cancel-in-progress` enabled **only** for `pull_request` | Superseded commits should be cancelled; a merge-queue run must never be cancelled, or the required check never reports and the queue stalls |
| `permissions` | `contents: read` at workflow level; nothing more is granted | Least privilege (Art. III.5) |
| Action pinning | Every `uses:` is a full 40-character commit SHA with the version in a trailing comment | A tag can be moved or deleted |
| `persist-credentials` | `false` on every checkout | The token has no use in this repository and must not remain in the workspace's git configuration |
| `pull_request_target` | Forbidden | It runs with write access against untrusted code |
| Secrets | No job may reference a repository or organisation secret | The required checks need no production credentials (BR-008) |

## Adding or Changing a Check

1. Add or amend the session in `noxfile.py`.
2. Add or amend the entry in `ci/file-coverage.yml`, including the path glob
   the check now covers.
3. Add or amend the row in the table above.
4. If the check is required, add it to the appropriate lane **and** to the
   gate job's `needs:` list. A required check that is not in `needs:` is a
   silent non-required check and a BR-003 violation; `file-coverage` rejects
   this case.
5. Update `docs/quality/traceability-matrix.md` if the check proves a
   requirement that was previously proven manually.

Removing a required check, or downgrading one to advisory, is a governance
change: it requires an ADR and an amendment to the constitution's quality-gate
list, not a pull request.

## Failure Recovery

| Symptom | Meaning | Action |
|---|---|---|
| `COULD NOT RUN` with exit `2` and a missing-tool message | The environment is not ready | Install the pinned tool; re-run locally before pushing |
| `COULD NOT RUN` with a database-health message | The PostgreSQL service container did not become ready | Re-run the job; if it persists, the health check in `ci/run-checks.sh` is wrong |
| `FAIL` in `secret-scan` | Secret material is present | Follow the rotate-first runbook in the contributor guide; do **not** merely delete the file |
| `FAIL` in `dependency-audit` | A locked dependency matches a known advisory | Update the dependency, or accept the advisory with an owner, a mitigation, and a review date |
| `FAIL` in `file-coverage` | A tracked file is uncovered, an exclusion is stale, or a check is missing from the gate | Add the covering check or justify the exclusion with a reason, an owner, and a review date |
