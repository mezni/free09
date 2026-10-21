# Data Model: Project Setup and Governance

**Feature**: `SPEC-001` — Project Setup and Governance
**Plan**: [plan.md](./plan.md) | **Spec**: [spec.md](./spec.md)
**Date**: 2026-10-21

---

## 1. Storage Scope

**This phase creates no application database object.** No schema, no table, no
migration, no view, no sequence, no database function, and no seed data are
introduced (BR-011). The PostgreSQL 16.15 instance provisioned for local
development and CI remains empty of application objects; it exists in this
phase only so that the Phase 2 migration baseline has a verified environment
and so that the test-topology decisions in
[research.md](./research.md) (R-07, R-13) are validated against a real engine
rather than assumed.

Any appearance of a database object in this phase is a scope error, and the
governance check `test_no_network_endpoint_or_database_object_introduced`
enforces that.

## 2. Persistence Model

This phase's persisted artefacts are **repository files**. The unit of
persistence is the Git commit, and the unit of consistency is the single
commit that changes a governance document, the templates it references, and
its evidence together.

| Property | Value |
|---|---|
| Storage medium | Git-tracked files in the working tree |
| Transaction boundary | One commit — a change to a governance document, the templates it references, and its exit-gate evidence MUST be committed together or not at all |
| Concurrency control | Git's normal merge and rebase; a governance document conflict MUST be resolved by a human, never auto-resolved |
| Schema versioning | Not applicable — no schema exists |
| Migration | Not applicable — template updates apply prospectively and MUST NOT rewrite artefacts already created from an earlier template (BR-006) |
| Retention | Version history of governance documents MUST be retained; a superseded constitution MUST NOT be deleted in a way that removes the record of what governed the work at the time |
| Deletion | An artefact is removed by a commit that deletes it and updates every reference to it in the same commit |

## 3. Entities

Nine artefact types are introduced. Each is defined below with its
identifiers, fields, owning location, and lifecycle. No entity has a foreign
key into another; the relationships are expressed as **path references** and
are validated by the governance check, not by a database constraint.

### 3.1 Feature artefact set

| Property | Definition |
|---|---|
| **Identifier** | Feature identifier — `NNN` for the sequential numbering convention (FR-026), combined with the directory name to form the unambiguous identifier, e.g. `001-project-setup` |
| **Location** | `specs/<feature>/` |
| **Fields** | `spec.md`, `plan.md`, `research.md`, `data-model.md`, `quickstart.md`, `contracts/`, `tasks.md`, `checklists/requirements.md` |
| **Owner** | The feature's author; review is by a reviewer other than the author |
| **Lifecycle** | `Draft` → `Approved` → `Implemented` → `Superseded`. The status lives in `spec.md` under Status and MUST be updated when approval occurs (Art. I.1) |
| **Validation** | `check_spec_artifacts.py` verifies the directory exists, holds the required files, and that the numbering is unique and sequential |

### 3.2 Governance document set

| Property | Definition |
|---|---|
| **Identifier** | Path-based; the constitution is additionally identified by its version string |
| **Location** | `docs/` — `docs/constitution.md`, `docs/build-plan.md`, `docs/quality/`, `docs/architecture/`, `docs/domain-model/`, `docs/risks/`; the binding copy is `.specify/memory/constitution.md` |
| **Fields** | Purpose, owner, status, last-amended date, change history (for the constitution: version, ratification state, Sync Impact Report) |
| **Owner** | Project owner for the constitution and the build plan; technical reviewer for quality and architecture documents |
| **Lifecycle** | `Draft` → `Approved` → `Superseded`. A superseded document is retained, never deleted |
| **Validation** | `check_spec_artifacts.py` verifies that exactly one constitution document exists in the tracked tree (FR-020) and that the binding copy and the `docs/` copy have not diverged |

### 3.3 Decision record (ADR)

| Property | Definition |
|---|---|
| **Identifier** | `ADR-NNNN` — unique within the repository, following the documented numbering convention |
| **Location** | `docs/adr/ADR-NNNN-<slug>.md`, created from `templates/adr-template.md` |
| **Fields** | Status (`Proposed` / `Accepted` / `Superseded` / `Deprecated`), Context, Options Considered, Decision, Consequences, Revisit Conditions, Traceability to requirements |
| **Owner** | Author of the decision; acceptance by the project owner and the technical reviewer |
| **Lifecycle** | `Proposed` → `Accepted` → (`Superseded` \| `Deprecated`). A `Superseded` record names its successor and is retained |
| **Validation** | `check_spec_artifacts.py` verifies unique identifiers, sequential numbering, and that every ADR carries a status and non-empty context, decision, and consequences |

### 3.4 Environment variable contract entry

| Property | Definition |
|---|---|
| **Identifier** | The variable name — `<SERVICE>_<DOMAIN>_<NAME>`, or `TELECO_*` / `COMMON_*` for cross-cutting settings |
| **Location** | The contract source of truth is `specs/001-project-setup/contracts/configuration-contract.md`; the realised instance is `.env.example` |
| **Fields** | Name, purpose, type, required/optional, default, placeholder value, and whether the value is secret-bearing |
| **Owner** | The service that consumes it; `TELECO_*` and `COMMON_*` are owned by the repository maintainers |
| **Lifecycle** | `Reserved` → `Declared` → `Consumed`. A name is Reserved when the convention is fixed but the consumer does not exist yet; Declared when it appears in `.env.example`; Consumed when a service reads it |
| **Constraint** | The contract carries **names and shapes, never values**. Only `.env.example` is tracked, and it contains placeholder values only (FR-014, BR-007) |
| **Validation** | `check_spec_artifacts.py` verifies that every name in `.env.example` appears in the contract and vice versa, that no value is a plausible secret, and that the naming convention holds |

### 3.5 Required check

| Property | Definition |
|---|---|
| **Identifier** | Check ID — stable kebab-case slug, e.g. `format`, `lint`, `typecheck`, `test`, `secret-scan`, `dependency-audit`, `governance`, `file-coverage` |
| **Location** | Defined as a nox session in `noxfile.py`; invoked identically by CI |
| **Fields** | ID, purpose, what it verifies, local command, CI job name, pass condition, fail condition, timeout, exit-code semantics |
| **Owner** | Repository maintainers |
| **Lifecycle** | `Required` (a merge gate) or `Advisory` (reported, never blocking). A check becomes Required only by amendment to the constitution's quality-gate list or to the gate job's `needs:` |
| **Constraint** | A Required check that cannot run MUST be reported as a failure (BR-003). A check that is skipped, cancelled, or never reported counts as a failure at the gate |

### 3.6 Check coverage rule

| Property | Definition |
|---|---|
| **Identifier** | The path glob, within the manifest |
| **Location** | `ci/file-coverage.yml` |
| **Fields** | Glob pattern, the Required check that covers it, and — for an exclusion — a reason, an owner, and a review date |
| **Owner** | Repository maintainers |
| **Lifecycle** | Created when a path or a check is added; an exclusion lapses on its review date and MUST be re-justified or removed |
| **Constraint** | Every tracked file MUST be covered by at least one Required check or matched by exactly one exclusion. An exclusion matching no tracked file MUST fail the check — stale exemptions are themselves a defect |

### 3.7 Phase exit gate evidence

| Property | Definition |
|---|---|
| **Identifier** | Phase identifier plus gate-condition identifier, e.g. `phase-0/condition-3` |
| **Location** | `docs/quality/` — the evidence record for the phase defined in `docs/build-plan.md` |
| **Fields** | Condition, result (`Satisfied` / `Not satisfied` / `Accepted exception`), evidence reference (a command's output, a commit SHA, a file path), reviewer, date |
| **Owner** | The technical reviewer |
| **Lifecycle** | Recorded once per condition; amended only with a new dated entry that preserves the prior entry |
| **Constraint** | A gate MUST NOT be recorded as satisfied without evidence for **every** one of its conditions (BR-010). An accepted exception MUST carry an owner, a mitigation, and a review date |

### 3.8 Open question register entry

| Property | Definition |
|---|---|
| **Identifier** | Stable slug |
| **Location** | `docs/risks/open-questions.md` |
| **Fields** | Question, why it matters, owner, due phase, status, affected gate |
| **Owner** | Named in the entry — an unowned question is not a register entry, it is an omission |
| **Lifecycle** | `Open` → `Resolved` (with the resolving ADR or document referenced) → `Accepted` (with an owner, mitigation, and review date) |
| **Constraint** | A phase gate MUST NOT be recorded as satisfied while a question affecting it is unowned, unresolved, and unaccepted (FR-027) |

### 3.9 Traceability matrix row

| Property | Definition |
|---|---|
| **Identifier** | The requirement identifier — `FR-nnn`, `BR-nnn`, `AC-nnn`, `SC-nnn` |
| **Location** | `docs/quality/traceability-matrix.md` |
| **Fields** | Requirement, source document and section, verification method (`Automated` / `Manual`), test or procedure name, phase, status, evidence reference |
| **Owner** | The technical reviewer |
| **Lifecycle** | Created when the requirement is specified; status updated as evidence appears; the row is never deleted while the requirement exists |
| **Constraint** | Every MUST requirement MUST have an acceptance criterion, and every acceptance criterion MUST have a test or an approved manual verification procedure (Art. VII.1, FR-029). An item MUST NOT be marked complete without evidence |

## 4. Relationships

All relationships are path references. There are no database foreign keys,
joins, or cascade behaviours.

```
Feature artefact set ──contains──▶ governance artefacts (plan, research,
      │                                  data model, contracts, quickstart)
      │
      └──references──▶ Decision record        (via "Traceability" section)
      │
      └──references──▶ Traceability matrix row
      │
      └──references──▶ Phase exit gate evidence

Environment variable contract entry ──realised as──▶ .env.example
Required check ──covers──▶ Check coverage rule ──maps to──▶ tracked file path
Phase exit gate evidence ──evidences──▶ Traceability matrix row
Open question register entry ──resolved by──▶ Decision record
```

## 5. Consistency and Validation Rules

| Rule | Enforcement |
|---|---|
| A feature directory holds exactly one specification, and its quality checklist is created alongside it | `check_spec_artifacts.py` |
| Templates contain unfilled placeholders only and no approved content (FR-023, BR-006) | `check_spec_artifacts.py` |
| Exactly one constitution document exists in the tracked tree (FR-020) | `check_spec_artifacts.py` |
| Every tracked file is covered by a Required check or a justified, unexpired exclusion (FR-032, SC-010) | `check_file_coverage.py` |
| Every Required check appears in the gate job's `needs:` list | `check_file_coverage.py` |
| Every declared check corresponds to a real CI job, and every CI job is declared | `check_file_coverage.py` |
| The environment variable contract and `.env.example` agree in both directions | `check_spec_artifacts.py` |
| No tracked file contains a plausible secret value | `gitleaks` plus `check_spec_artifacts.py` |
| No database object or network endpoint is introduced by this phase (BR-011) | `test_no_network_endpoint_or_database_object_introduced` |
| A phase gate is satisfied only with evidence for every condition (BR-010) | `test_exit_gate_evidence_recorded_for_every_condition` |

## 6. What This Phase Deliberately Does Not Model

- **Service domain entities** (subscriber, account, invoice, SIM, order). These
  belong to the Phase 2 feature specifications for each service and require
  their own data models under Constitution Article V.
- **Audit-log and ledger schemas.** The constitution's Article IV requires an
  immutable, append-only ledger for financial events; its storage design is an
  open architecture question (Q-008) and must not be invented in a setup phase.
- **Cross-schema foreign keys.** Whether a cross-service relationship is a
  foreign key, an event, or a replicated projection is unresolved under
  ADR-0001's revisit conditions and belongs to the Phase 2 design, not here.
- **Event broker and its topics.** Undecided under the same ADR.
