# Contributing to Telco Platform

## Development Workflow

1. **Fork the repository** and create a feature branch from `main`
2. **Follow the SPEC-001 workflow**: 
   - `/speckit.specify` for feature specifications
   - `/speckit.plan` for implementation plans
   - `/speckit.tasks` for task decomposition
3. **Adhere to the project constitution** (`.specify/memory/constitution.md`, v1.0.0)
4. **Maintain traceability**: All code changes must trace back to approved specifications via test mapping identifiers (TMxxx)
5. **Constitution gates**: All quality gates (format, lint, typecheck, test, secret-scan, dependency-audit) must pass before merge
6. **No new network endpoints or database objects** (BR-011) — extend existing services only
7. **Tooling baseline** (BR-012) — Python FastAPI on PostgreSQL must remain unchanged

## Pull Request Process

1. All changes must be submitted via pull request with a completed review checklist
2. Quality gates (format, lint, typecheck, test, secret-scan, dependency-audit) must pass
3. Changes must not introduce new runtime network endpoints or database objects (BR-011)
4. The implementation-language baseline must remain unchanged (BR-012)
5. Third-party actions are SHA-pinned and the workflow token is read-only
6. Changes must be submitted via pull request with a completed review checklist

## Specification Development

- Use `/speckit.specify` to generate feature specifications
- Follow the template structure in `.specify/templates/spec-template.md`
- All mandatory sections must be completed
- No implementation details (languages, frameworks, APIs) in specifications
- Specifications are the only source of truth for intended behavior

## Task Development

- Use `/speckit.tasks` to generate task lists
- Tasks must follow the checklist format: `- [x] T### [P?] [USx] Description with file path`
- Tasks are organized by user story for independent implementation and testing
- Verify tests fail before implementing (TDD approach)
- Commit after each task or logical group

## Documentation Standards

- Reference test mappings (TMxxx) for traceability
- Use the project constitution as the governance reference
- All ADRs and architectural decisions documented in `docs/adr/`
- Keep specifications written for non-technical stakeholders
- Avoid HOW to implement — focus on WHAT and WHY

## Code Standards

- Follow the existing Python FastAPI patterns in the repository
- Use `black`, `flake8`, `isort` for format/lint
- Run `make test` to execute the fast-checks suite
- Run `make local-verification-command-runs-all-required-checks` for full verification
- No secrets in code — use environment variables from `.env`
- Maintain the Python FastAPI on PostgreSQL baseline (BR-012)

## Issue Reporting

- Use the project's issue tracker for bugs and feature requests
- Reference relevant specifications (specs/xxx-yyy/xxx-spec.md) when applicable
- Reference test mappings (TMxxx) when reporting test-related issues
- Check for duplicate issues before creating new ones

## License

This project is governed by the project constitution. See `constitution.md` for details.
