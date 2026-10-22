# Precedence and Conventions

This document states the order in which the repository's governing documents
take precedence, and the numbering conventions the repository follows. It is
referenced by Constitution Article XI and by the
[repository layout contract](../../specs/001-project-setup/contracts/repository-layout-contract.md).

## Precedence Order

When two documents make statements about the same subject and cannot both be
true, the higher-ranked document governs. The order is, from highest to
lowest:

| Rank | Document | Governs |
|---|---|---|
| 1 | `docs/constitution.md` | Principles, quality gates, amendment procedure |
| 2 | An accepted ADR in `docs/adr/` | One recorded technical decision |
| 3 | The contracts in `specs/<feature>/contracts/` | Interfaces between components |
| 4 | An approved `specs/<feature>/spec.md` | What a feature must deliver |
| 5 | `specs/<feature>/plan.md` and `tasks.md` | How a feature is sequenced |
| 6 | `docs/` prose | Design rationale and background |
| 7 | `CONTRIBUTING.md` and `README.md` | How to work in the repository |

Two rules qualify the order:

- **A contract outranks the specification that owns it** for the interface it
  defines. If a spec and its contract disagree about a field name, the
  contract is right and the spec is corrected.
- **An ADR outranks the prose that describes it**, but an ADR never
  outranks the constitution. An ADR that contradicts the constitution is
  rejected, not applied.

### Resolving a conflict

1. Name the two documents and the conflicting statements.
2. Rank them using the table above.
3. Apply the higher-ranked document.
4. Record the correction in the lower-ranked document, in the same change set
   as the fix. A conflict that is resolved but left in place is still a
   conflict.
5. If the conflict cannot be resolved by ranking — because both documents sit
   at the same rank and disagree — the technical lead decides, and the
   decision is recorded as an ADR.

The `governance` required check enforces part of this rule mechanically: it
rejects a tree in which the constitution source and its governance record
disagree, in which a template carries a resolved identifier, or in which the
configuration contract and `.env.example` disagree.

## Feature Numbering

Feature directories live under `specs/` and are named
`<nnn>-<kebab-case-name>`, where `nnn` is a zero-padded three-digit sequence
number.

- Numbers are assigned in creation order and are never reused, even if a
  feature is abandoned.
- Each feature directory holds `spec.md`, `tasks.md`, `plan.md`, and
  `checklists/requirements.md`. A feature that has not reached the planning
  stage may omit `plan.md`.
- The specification is addressed as `SPEC-<nnn>`.

## Decision Record Numbering

Architecture decision records live under `docs/adr/` and are named
`ADR-<nnnn>-<kebab-case-title>.md`, where `nnnn` is a zero-padded four-digit
sequence number.

- Numbers are assigned in creation order and are never reused.
- A record's filename never changes. A superseded record keeps its number and
  has its status set to `Superseded`, with a pointer to the superseding
  record.
- A record's status is one of `Proposed`, `Accepted`, `Rejected`,
  `Superseded`. Only `Accepted` records are binding.
- Every accepted record states: the context, the decision drivers, the
  options considered, the decision, the consequences, and the conditions under
  which it should be revisited.

## Test Mapping Identifiers

Requirement-to-test mappings use the `TM<nnn>` form and are recorded in
`docs/quality/traceability-matrix.md` for Phase 0 requirements and in
`docs/traceability-matrix.md` for the build phases.

- A `TM` identifier is never reused for a different requirement.
- A row that names a test that does not exist is not a traceability claim. It
  is replaced with an implemented test name or an approved manual
  verification.

## Requirement Identifiers

Requirements use the `FR-<nnn>` form within a specification, and `BR-<nnn>`
for a boundary or constraint. Acceptance criteria use `AC-<nnn>`. The
numbering is local to the specification that owns it.
