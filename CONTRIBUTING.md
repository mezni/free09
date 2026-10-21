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
2. Quality gates (format, lint, typecheck, test, secret-scan, dependency-audit)
   must pass — the required-check set reports PASS (0), FAIL (1), COULD NOT RUN
   (2) or INTERNAL ERROR (3); both 1 and 2 fail the gate (BR-003)
3. Changes must not introduce new runtime network endpoints or database objects
   (BR-011)
4. The implementation-language baseline must remain unchanged (BR-012)
5. Any GitHub Actions workflow added to the repository must pin third-party
   actions by SHA and use a read-only workflow token. No workflow files exist
   in the repository today, so this rule applies from the first workflow added
6. A change to approved behaviour must update the specification and the
   affected tests in the same change set

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
- `make test` runs the full local verification lane (`nox` session
  `fast_checks`): format, lint, lockfile, typecheck, test, secret-scan and
  dependency-audit
- Individual lanes are available as `make lint`, `make format`,
  `make typecheck`, `make test-cov`, `make secret-scan`, `make dep-audit` and
  `make lockfile`
- `ci/run-checks.sh fast_checks` runs the same lane and forwards the exit code
  unchanged for CI callers
- Never commit secrets — read values from environment variables configured in
  `.env`
- Maintain the Python FastAPI on PostgreSQL baseline (BR-012)

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
