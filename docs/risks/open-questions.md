# Risks and Open Questions

Keep each item assigned to an owner and close or explicitly accept it before the affected implementation gate.

## Open

| ID | Question / risk | Why it matters | Owner | Due phase | Status |
|---|---|---|---|---|---|
| Q-001 | What is the precise meaning of subscriber in this business? | Affects identity relationships and APIs | Product/domain owner | 1 | Open |
| Q-002 | Can one customer have multiple billing accounts and legal entities? | Affects CRM and billing model | Product/domain owner | 1 | Open |
| Q-003 | What currencies and tax jurisdictions are in scope? | Affects invoice calculations and ledger | Billing owner | 1 | Open |
| Q-004 | What are billing-cycle, proration, rounding, and invoice-finalization rules? | Required for correct invoices | Billing owner | 1 | Open |
| Q-005 | What are credit-memo approval thresholds and separation-of-duties rules? | Financial control requirement | Finance/domain owner | 1 | Open |
| Q-006 | Are phone numbers globally unique, time-bounded, or recyclable in the modeled domain? | Affects indexing and history | CRM owner | 1 | Open |
| Q-007 | What device/SIM identifiers and lifecycle states are mandatory? | Affects inventory constraints | Inventory owner | 1 | Open |
| Q-008 | Is the system single-tenant or multi-tenant? | Affects authorization and data isolation | Architecture owner | 1 | Open |
| Q-009 | What availability, RPO, RTO, retention, and audit-retention targets apply? | Required for production readiness | Operations owner | 1 | Open |
| Q-010 | Is an API gateway required in the first release? | Affects auth and deployment | Architecture owner | 1 | Open |
| Q-011 | Are cross-schema foreign keys allowed? | Affects coupling and integrity | Database owner | 2 | Open |
| Q-012 | What payment provider or payment interface is in scope? | Affects integration and idempotency | Billing owner | 1 | Open |
| Q-013 | Which provisioning interfaces are real versus mocked? | Affects OSS integration | Inventory owner | 1 | Open |
| Q-014 | What dataset sizes and performance targets must be met? | Affects synthetic data and test strategy | Test/operations owner | 1 | Open |
| Q-015 | When is the constitution ratified, and by whom? | The constitution is not binding until ratified; Article I.2 permits implementation only against an approved specification, so this blocks the Phase 0 exit gate | Project owner | 0 | Open |
| Q-016 | Is `ADR-0001-centralized-postgresql` accepted? | The one-database, four-schema topology is treated as a planning input, not a settled constraint. The constitution's deployment-topology policy cites it while its status is *Proposed* | Architecture owner | 0 | Open |
| Q-017 | Should the required dependency check use the offline vendored advisory snapshot or a networked audit? | The offline snapshot satisfies FR-011 and keeps CI deterministic, but it is only as fresh as the last refresh. A networked `uv audit` is more current but violates the literal reading of FR-011 and makes the same commit pass or fail depending on when it ran. The plan implements the offline snapshot and enables Dependabot and GitHub dependency review so both readings are covered, but the owner must confirm the trade-off is acceptable | Technical lead | 0 | Open |
| Q-018 | Which copy of the constitution is authoritative — `docs/constitution.md` or `.specify/memory/constitution.md`? | The two currently differ. The constitution's own Sync Impact Report carries a `TODO(DOC_RECONCILIATION)` for this. FR-020 requires exactly one constitution document in the tracked tree | Technical lead | 0 | Open |
| Q-019 | When is the SPEC-001 specification approved? | Constitution Article I.2 permits implementation only against an approved specification; `specs/001-project-setup/spec.md` is complete with a 16/16 quality checklist but still carries status *Draft* | Technical reviewer | 0 | Open |
| Q-020 | Should `httpx2` be adopted when its mocking ecosystem catches up? | The project pins `httpx` 0.28.1 because neither `respx` nor `pytest-httpx` supports `httpx2` yet. Adopting it early puts BR-005 at risk. The trigger is recorded in ADR-0004 | Technical lead | 2 | Open — revisit trigger recorded in ADR-0004 |
| Q-021 | Should a second type checker (`ty` or `pyrefly`) run alongside mypy? | mypy was chosen for its pydantic plugin and for not duplicating ruff's rules. A second checker would give broader type-system conformance at the cost of a second configuration and a second failure mode | Technical lead | 1 | Open |
| Q-022 | Should the workflow dependency-lockfile feature be adopted? | It is the strongest available supply-chain control for GitHub Actions, but it is public preview. SHA pinning is in place meanwhile | Technical lead | 1 | Open |
| Q-023 | Should `prek` replace `pre-commit` for the local hook runner? | `prek` is a Rust reimplementation reading the same configuration and is significantly faster. `pre-commit` was chosen for documentation maturity; the committed artefact is identical either way | Technical lead | 1 | Open |

## Resolved

| ID | Question | Resolution | Owner | Resolved in |
|---|---|---|---|---|
| Q-R01 | Which continuous verification platform and runner are used? | GitHub Actions — a single workflow with a `fast-checks` lane, a `slow-checks` lane, and a `required-checks` gate job that fails closed on any inconclusive result. Rationale in `specs/001-project-setup/research.md` R-01, R-14 | Architecture owner | Phase 0 planning |
| Q-R02 | Which runtime and operating system baselines are supported? | Python 3.13 floor (`>=3.13,<4`) with a 3.13/3.14 CI matrix; Linux CI and containers; Linux and macOS workstations. Rationale in `research.md` R-02 | Technical lead | Phase 0 planning |
| Q-R03 | Who ratifies the constitution, and on what date? | The project owner, with the technical reviewer as second signatory, as a Phase 0 exit-gate condition. Tracked as Q-015 | Project owner | Phase 0 planning — awaiting ratification |
| Q-R04 | Which environment variable names are reserved for services not yet implemented? | The `<SERVICE>_<DOMAIN>_<NAME>` convention with the four constitution service prefixes. Only tooling and database variables are declared now; the rest are Reserved. Contract in `specs/001-project-setup/contracts/configuration-contract.md` | Architecture owner | Phase 0 planning |
| Q-R05 | What is the remediation path when secret material has already been committed? | Rotate-first: revoke or rotate at the issuing provider, then rewrite history with `git-filter-repo` only if a rewrite is warranted, since rewriting breaks pull-request diffs and carries a recontamination risk. Runbook in `research.md` R-09 and `CONTRIBUTING.md` | Technical lead | Phase 0 planning |
