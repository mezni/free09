# Contributing to Telco Platform

## Prerequisites

| Tool | Version | Purpose |
|---|---|---|
| Python | 3.13+ | Runtime and test interpreter |
| [uv](https://docs.astral.sh/uv/) | latest | Dependency resolution, lockfile, environment management |
| make | any | Task runner entry point |
| Docker + Compose | any | Local PostgreSQL and the service stack |

`make setup` verifies that these are present and creates `.env` from
`.env.example`. An existing `.env` is preserved; run
`FORCE_ENV_RECREATE=1 make setup` to overwrite it.

## Development Workflow

1. **Create a feature branch** from `main`
2. **Follow the SPEC-001 workflow**:
   - `/speckit.specify` for feature specifications
   - `/speckit.plan` for implementation plans
   - `/speckit.tasks` for task decomposition
3. **Adhere to the project constitution** (`.specify/memory/constitution.md`, v1.0.0)
4. **Maintain traceability**: code changes must trace back to approved
   specifications via test mapping identifiers (TMxxx)
5. **Pass all quality gates**: format, lint, typecheck, test, secret-scan,
   dependency-audit
6. **No new network endpoints or database objects** (BR-011) — extend existing
   services only
7. **Tooling baseline** (BR-012) — Python FastAPI on PostgreSQL must remain
   unchanged

## Pull Request Process

1. All changes must be submitted via pull request with a completed review
   checklist
2. Quality gates (format, lint, lockfile, governance, file-coverage, typecheck,
   test, secret-scan, dependency-audit) must pass — the required-check set
   reports PASS (0), FAIL (1), COULD NOT RUN (2) or INTERNAL ERROR (3); both 1
   and 2 fail the gate (BR-003)
3. Changes must not introduce new runtime network endpoints or database objects
   (BR-011)
4. The implementation-language baseline must remain unchanged (BR-012)
5. Any GitHub Actions workflow added to the repository must pin third-party
   actions by SHA and use a read-only workflow token. The continuous
   verification workflow in `.github/workflows/ci.yml` is the reference for
   this rule
6. A change to approved behaviour must update the specification and the
   affected tests in the same change set

### Approval Expectations

- Every pull request needs one approving review from someone other than the
  author. The branch ruleset enforces this on `main`.
- A change to the constitution, to the required-check set, or to an accepted
  ADR needs the repository owner's approval in addition to the ordinary
  review.
- A change to an approved specification's approved behaviour needs the
  approval of the technical lead as well as one review.
- Reviews dismiss themselves when new commits are pushed, so an approval
  always refers to the code as it stands at the moment of the approval.

## Specification Development

- Use `/speckit.specify` to generate feature specifications
- Follow the template structure in `.specify/templates/spec-template.md`
- An approved specification must define purpose, scope, actors, preconditions,
  normal and failure flows, data changes, authorization, observability, and
  measurable acceptance criteria
- Implementation must not introduce requirements absent from the approved
  specification
- Specifications are the source of truth for intended behaviour

## Task Development

- Use `/speckit.tasks` to generate task lists
- Tasks follow the format `- [ ] T### [P] [USx] Description with file path`,
  where `[P]` marks tasks that can run in parallel and `[USx]` ties the task to
  a user story
- Tasks are organized by user story so each story can be implemented and
  tested independently
- Verify that the test fails before implementing it
- Commit after each task or logical group

## Documentation Standards

- Reference test mappings (TMxxx) for traceability
- Use the project constitution as the governance reference
  (`docs/constitution.md` is the source artifact, `.specify/memory/constitution.md`
  is the governance record)
- Record architectural decisions as ADRs in `docs/adr/`
- State WHAT and WHY; keep implementation HOW in the task list
- Per-phase traceability mappings live in each phase's `spec.md`; the central
  matrix at `docs/traceability-matrix.md` indexes the build-phase5 through
  build-phase11 rows (TM104–TM333) and records which are implemented

## Code Standards

- Follow the existing Python FastAPI patterns in the repository
- Format and lint with `ruff` (`ruff format` and `ruff check`); `mypy` performs
  type checking
- `make verify` runs every required check (`nox` with no session selected):
  format, lint, lockfile, governance, file-coverage, typecheck, test,
  secret-scan and dependency-audit
- `make test` runs the fast lane only (`nox` session `fast_checks`): format,
  lint, lockfile, governance and file-coverage
- Individual checks are available as `make lint`, `make format`,
  `make typecheck`, `make test-cov`, `make secret-scan`,
  `make dependency-audit`, `make governance`, `make file-coverage` and
  `make lockfile`
- `ci/run-checks.sh <session>` runs one check and forwards the exit code
  unchanged for CI callers
- Never commit secrets — read values from environment variables configured in
  `.env`
- Maintain the Python FastAPI on PostgreSQL baseline (BR-012)

## Exception Route

A required check may be waived for a specific change only when the check
cannot run in the contributor's environment and the check's own logic is not
what is in question — a broken format rule is never an exception. The
`required-checks` gate cannot be waived by editing the workflow; only the
repository owner may change the required-check set, and only through an ADR
and an amendment to the constitution's quality-gate list.

Every exception is recorded in the pull request and states:

| Field | What it must contain |
|---|---|
| **Rationale** | Why the check cannot be satisfied as written |
| **Risk** | What defect could pass unnoticed, and how likely it is |
| **Scope** | Which files, paths, or change types the exception covers |
| **Owner** | The person accountable for the risk until the exception lapses |
| **Compensating controls** | The manual or automated step that covers the gap meanwhile |
| **Review date** | The date the exception is re-examined; it lapses on that date |

An exception without all six fields is not an exception. An exception that
expires is not renewed by silence: the check must pass, or a new exception
must be recorded.

## Secret Remediation Runbook

The `secret-scan` check reports the location and the rule of every finding but
never prints the value. When it fails, follow this procedure in order. Do not
skip to step 3.

1. **Confirm the finding.** Read the reported location. If the value is a
   documented placeholder — the repository's placeholders are listed in
   `.gitleaks.toml` and recognised by `ci/secret_scan.py` — fix the scanner's
   allowlist instead, and say so in the pull request.
2. **Rotate first.** If the value is a real credential, revoke or rotate it at
   the issuing provider **before** touching the repository. A deleted file is
   still a live credential in the provider's records, and in every clone.
3. **Record the incident.** Note what leaked, where it was exposed, when it was
   rotated, and who was informed.
4. **Remove the material.** Remove it from the working tree and commit the
   removal. Do not use `git rm --cached` alone: the object stays in history.
5. **Decide about history rewriting.** Rewriting history with `git-filter-repo`
   breaks pull-request diffs and carries a recontamination risk. Rewrite only
   when the credential was exposed publicly and the rotation alone is not
   sufficient, and only with the owner's agreement.
6. **Verify.** Re-run `make secret-scan`. The check scans both the working tree
   and every commit in the history, so a finding that is still present in an
   earlier commit keeps failing.

Never paste a detected value into an issue, a pull request, a commit message,
or a chat message. Reference it by its location only.

## Issue Reporting

- Use the project's issue tracker for bugs and feature requests
- Reference the relevant specification (`specs/<nnn>-<feature>/spec.md`) when
  applicable
- Reference test mappings (TMxxx) when reporting test-related issues
- Check for duplicate issues before creating new ones

## License

No open-source license file has been added to the repository yet. Until one is
added, the project is governed by the project constitution — see
`docs/constitution.md` — and all rights are reserved by the project owner.
Contributors should raise a licensing question before contributing if the
intended terms are unclear.
