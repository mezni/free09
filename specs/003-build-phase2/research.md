# Research: build-phase2

**Feature**: Data model and database foundation (`specs/003-build-phase2/spec.md`)
**Date**: 2026-10-22
**Task**: T006 — the decisions behind the plan

This file answers the three open questions the phase-2 specification raised
(Q-DM-001 to Q-DM-003) and records the decisions the data model rests on. Each
decision states what was decided, why, what was rejected, and which requirement
or success criterion it settles. Clause references use the numbered form from
`docs/constitution.md` (Art. XI.4).

Where a decision rests on an assumption that a named owner has not confirmed,
the decision says so and the assumption is carried into
`docs/risks/open-questions.md` (Art. I.5).

---

## D-01 — The phase models four domains, one schema each

**Answers**: Q-DM-001

**Decision**: The phase-2 data model covers exactly four domains — `auth`,
`crm`, `inventory`, and `billing` — one PostgreSQL schema per domain, each
owned by exactly one service: `auth-service`, `crm-service`,
`inventory-service`, and `billing-service` (Art. II.1, Art. V.1).

**Rationale**: The service inventory is fixed by the constitution, and the
schema-to-service mapping was recorded by the domain-discovery phase in
`docs/architecture/architecture-overview.md` §2. Every later phase in the build
plan crosses all four domains — Phase 3 writes to `auth`, Phase 4 to `crm`,
Phase 5 to `inventory`, Phase 6 to `billing`, and Phases 7 to 11 read across
all of them — so a model that covers fewer domains cannot satisfy the phases
that depend on it.

**Alternatives considered**:

- *Model only the domains the next phase touches.* Rejected: the phase-2 exit
  gate requires the model to describe the domains the platform owns, and a
  model that stops at `auth` would have to be reopened — and re-approved —
  before each later phase.
- *Introduce a fifth shared `reference` schema for common lookup values.*
  Rejected: the constitution names four services (Art. II.1), so a fifth schema
  would have no owner, and Art. V.1 requires every domain's model to belong to
  exactly one service.
- *One schema per service is not required; one schema for the whole platform.*
  Rejected: it would put every service's tables in one ownership boundary and
  breach Art. II.2 and Art. II.3.

**Settles**: FR-033 (the domains the platform owns), FR-034 (one owning
service per domain), and SC-030. The domain list in the data dictionary is now
closed.

---

## D-02 — The commercial catalogue is shared reference data owned by `inventory-service`

**Answers**: Q-DM-002

**Decision**: The reference data that more than one domain reads is the
commercial catalogue — products, product versions, rate plans, rate-plan
versions, and add-ons. `inventory-service` owns it in the `inventory` schema
(D-01). `billing-service` and `crm-service` read it through the owning
service's API (Art. II.4, Art. VI.1); neither service holds a copy of the
catalogue and neither declares a foreign key into it (D-04).

Standards-based codes — ISO 4217 currency, ISO 3166-1 alpha-2 country, and
their kind — are carried as codes on the rows that use them and are validated
at the owning service's boundary against the published standard. The platform
holds no shared lookup table for them, so no synchronisation mechanism is
needed and no schema is added to the constitution's service list.

**Rationale**: The catalogue is the one body of data that more than one domain
must read: `billing-service` prices an invoice from a rate-plan version, and
`crm-service` shows a customer what they hold. Art. II.4 requires cross-domain
interaction to go through a documented API, and Art. V.1 requires the data to
have exactly one owner, so the catalogue has one owner and two readers.
Standards-based codes are not platform data at all: they are values defined by
an external standard, which makes a stored copy redundant and a synchronisation
problem rather than a modelling one.

**Alternatives considered**:

- *`crm-service` owns the catalogue.* Rejected: the catalogue is a commercial
  product definition with prices, quotas, and effective dates, which is
  inventory data; the architecture overview assigns it to `inventory-service`,
  and `crm-service` owns the customer records that reference it.
  The repository-layout contract still describes `crm-service` as owning the
  "product catalogue"; that phrase conflicts with the domain-discovery
  mapping and is recorded as Q-024 for the architecture owner.
- *Duplicate the catalogue into each reading schema.* Rejected: it creates two
  mutable copies of the same commercial truth with no synchronisation
  mechanism, which the architecture overview forbids without a documented
  strategy, and Art. V.1 gives the data one owner only.
- *A fifth `reference` schema with a shared table of codes.* Rejected for the
  reason given in D-01.

**Settles**: FR-034, FR-035 (the catalogue's owner is named), SC-030. The
identity of the owning service is no longer open.

---

## D-03 — Effective dating has three forms, chosen by the kind of data

**Answers**: Q-DM-003

**Decision**: History is kept in three forms, and every table's form is stated
in the data dictionary:

1. **Temporal master data** — rows carry `valid_from` and `valid_to`, with
   `valid_to IS NULL` meaning *current*; a new version closes the previous row
   and opens a new one. Used for product versions, rate-plan versions,
   subscriptions, subscription add-ons, SIM assignments, device assignments,
   customer addresses, and tax rates.
2. **Append-only event records** — rows are written once and never updated:
   security audit events, ticket status history, ticket assignment history,
   ledger entries, ledger entry groups, and credit-memo approval steps.
3. **Immutable snapshots** — a financial document copies the commercial terms
   it was priced from, so the document stays explainable after the underlying
   rate plan changes: an invoice line carries the rate-plan version and the
   price, quota, and terms that were in force when it was posted.

The platform holds no generic history table. An append-only history table for
every entity would duplicate each table's own lifecycle columns and would make
the audit trail of a row ambiguous — which of the copies is authoritative.

**Rationale**: The requirement is that history is kept; it does not say by one
mechanism. A single mechanism does not fit the three kinds of data. Effective
dating on master data answers "what was true at time T"; append-only rows
answer "what happened"; snapshots answer "why was I charged this". The
domain-model overview already requires that historical invoices remain
explainable when prices change, which is the snapshot case and cannot be
satisfied by either of the other two.

**Alternatives considered**:

- *Valid-from/valid-to columns everywhere.* Rejected: an event that happened
  once has no interval; giving it one would imply it could have been valid in
  a different period.
- *An append-only history table for every entity.* Rejected as above: it
  duplicates the lifecycle columns and produces two candidate truths.
- *A separate temporal table for every entity, as in bitemporal modelling.*
  Rejected: the phase's requirement is that history is kept and that the form
  is stated, not that two time axes are maintained for every row; the cost is
  a wider model than the business rules recorded so far justify (Art. X.7).

**Settles**: FR-041 (audit fields, and which of them are effective-dated),
SC-035, and NFR-033 (the model is reviewable without reading the migrations).
The effective-dating rule is now decided and stated per table.

---

## D-04 — No foreign key crosses a schema boundary

**Answers**: Q-011 in `docs/risks/open-questions.md`

**Decision**: The migration set creates no foreign key from one schema to
another. A reference that crosses an ownership boundary is carried by a stable
identifier — the target's primary key — with no referential constraint
enforced by the database. Within a schema, foreign keys are declared and
enforced normally.

**Rationale**: A cross-schema foreign key makes one service's schema depend on
another service's table: dropping or renaming the referenced column becomes a
breaking change in two services at once, and one service's migration cannot be
applied without the other's table already existing in the target shape
(Art. II.2, Art. II.3, Art. V.4). The architecture overview §3 holds the same
position and requires an ADR for any cross-schema read exception. The
alternative — the reference is carried by an identifier the reader resolves
through the owning service's API — keeps the coupling at the contract level,
where it is documented and versioned.

**Alternatives considered**:

- *Cross-schema foreign keys, with migrations ordered to keep them valid.*
  Rejected: it converts a contract change into a coordinated schema change
  across services, which is exactly the coupling Art. II.4 exists to prevent.
- *A read-only view in the reader's schema.* Not rejected — it is permitted
  under the architecture overview §3, but it requires an ADR stating the
  consistency and permission consequences, so it is not part of the phase-2
  baseline. A view is not a foreign key and does not create the coupling this
  decision avoids.

**Settles**: FR-034, FR-035, the specification's edge case "A table needs a
key owned by another service", and the phase-2 exit-gate condition that
critical relationships are documented.

---

## D-05 — Primary keys are application-generated UUIDs

**Decision**: Every table's primary key is a UUID generated by the application
before insert and stored as `uuid`. No sequence or identity column backs a
primary key. A table may carry additional natural keys with a unique
constraint, but they are never the primary key.

**Rationale**: Identifiers are created before the row exists: one request
creates a subscription, its add-ons, and its provisioning job, and each of
those rows is referenced by the response before the transaction commits. A
sequence would also make identifiers sequential, which leaks ordering and row
counts through an API and makes enumeration trivial. UUIDv7 is
time-ordered, so index locality is preserved without a sequence.

**Alternatives considered**:

- *`bigint` identity.* Rejected: the identifiers are exposed through APIs, and
  a sequential identifier is enumerable and leaks volume.
- *Natural keys as primary keys* (for example `subscriber_number`).
  Rejected: a natural key's meaning can change, and a primary key that can
  change forces every referencing row to be updated. Natural keys are retained
  as unique constraints.

---

## D-06 — Audit fields are the same on every table

**Decision**: Every table in the phase-2 model carries:

| Field | Type | Rule |
|---|---|---|
| `created_at` | `timestamptz` | Not null; set on insert |
| `updated_at` | `timestamptz` | Not null; set on insert and on every update |
| `created_by` | `uuid` | The acting principal's identifier, or the owning service's identifier for system writes; no foreign key (D-04) |
| `updated_by` | `uuid` | The acting principal's identifier for the last update |
| `version` | `integer` | Not null, default 1; incremented on every update; optimistic concurrency |

Effective dating (D-03) is a separate concern from auditing: `valid_from` and
`valid_to` describe when a row is *in force*, while the audit fields describe
when the row was *written* and by whom. A table that is not temporal carries
no `valid_from`/`valid_to`; its lifecycle is expressed by its status column.

Soft deletion is not used. A row is either present and carries a status, or it
is absent; a `deleted_at` column would give two answers to "is this row
active?" and would make historical references ambiguous.

**Rationale**: A single audit shape is auditable; four shapes, one per domain,
are not. `created_by` and `updated_by` are deliberately not foreign keys into
`auth` — the audit trail must survive the deletion of the principal, and a
foreign key would either block that deletion or cascade it (D-04).

**Alternatives considered**:

- *No `version` column.* Rejected: without it, two concurrent writers can
  overwrite each other's update silently, and the audit fields cannot say
  which write won.
- *Soft deletion.* Rejected as above.

---

## D-07 — Money is a decimal with an explicit currency

**Decision**: Every monetary column is `numeric(19, 4)`, paired with an
explicit ISO 4217 currency code column. A binary floating-point type is never
used for an amount, and an amount is never stored without its currency.

**Rationale**: Art. IV.1 requires a decimal type, Art. IV.5 requires the
currency to travel with the amount, and Art. IV.2 forbids silent rounding.
The scale of four decimal places is the one the phase-6 billing rules can
express without a schema change; the currency's own minor-unit rule (how many
decimal places a currency actually uses) is a business rule that Phase 6
settles, and the constraint above keeps both the stored value and the rule
independent of it.

**Alternatives considered**:

- *`numeric(12, 2)`.* Rejected: it cannot express a unit price that needs more
  precision, such as a per-minute rate, without a later migration.
- *An integer in the currency's minor unit.* Rejected: it makes the stored
  value unreadable without the currency's rule, and the rule is not decided
  yet.

---

## D-08 — Timestamps are `timestamptz` in UTC

**Decision**: Every timestamp column is `timestamptz`. No column stores a
local time, a naive timestamp, or a date that means "the day it happened" in
an unspecified zone. A calendar date that is a business fact — an invoice
period, a tax period — is stored as `date` and is named for the fact it
carries.

**Rationale**: A telecom platform operates in more than one zone from the first
day; a naive timestamp is ambiguous the moment a second zone appears. Storing
UTC and rendering in the caller's zone keeps one stored value and one
interpretation.

**Alternatives considered**:

- *`timestamp without time zone`.* Rejected: ambiguous across zones.
- *Storing local time per tenant.* Rejected: it moves the ambiguity into the
  storage and makes cross-tenant comparison incorrect.

---

## D-09 — Deletion is restricted; cascades stay inside a schema

**Decision**: A referenced row is deleted only with an explicit `ON DELETE
RESTRICT` rule. A cascading delete is used only for a child row that has no
meaning on its own — an invoice line without its invoice, a role-permission
pair — and never across a schema boundary. A posted ledger entry, a posted
invoice, and a security audit event are never deletable; they are voided or
superseded by a compensating entry.

**Rationale**: Financial and audit history is the evidence the platform is
built on (Art. IV.4). A cascade that removes financial evidence silently is
not a deletion, it is a loss of the record.

**Alternatives considered**:

- *`ON DELETE CASCADE` throughout, for convenience.* Rejected: it deletes
  evidence and turns one mistaken delete into a large data loss.

---

## D-10 — Data classification is recorded per schema

**Decision**: Every table is classified, and the classification is recorded in
the data dictionary (Art. III.1):

| Schema | Classification | Why |
|---|---|---|
| `auth` | Restricted | Credential material and personal data |
| `crm` | Confidential | Personal data of customers and subscribers |
| `inventory` | Internal | Operational data; a device identifier is an asset record, not personal data |
| `billing` | Restricted | Financial records and personal data |

**Rationale**: Art. III.1 requires the classification to be recorded in the
specification that introduces the data, and the phase-2 model introduces every
table the platform owns.

---

## Traceability of the decisions

| Decision | Answers | Settles | Artefact |
|---|---|---|---|
| D-01 | Q-DM-001 | FR-033, FR-034, SC-030 | `data-model.md` §1 |
| D-02 | Q-DM-002 | FR-034, FR-035, SC-030 | `data-model.md` §1.3, §3.3 |
| D-03 | Q-DM-003 | FR-041, SC-035, NFR-033 | `data-model.md` §2 |
| D-04 | Q-011 | FR-034, FR-035 | `data-model.md` §1.4 |
| D-05 | — | FR-035 | `data-model.md` §2.1 |
| D-06 | — | FR-041, FR-042 | `data-model.md` §2.2 |
| D-07 | — | FR-035 | `data-model.md` §2.3 |
| D-08 | — | FR-035 | `data-model.md` §2.3 |
| D-09 | — | FR-035, FR-038 | `data-model.md` §2.4 |
| D-10 | — | FR-041 | `data-model.md` §2.5 |

## Open items this research does not close

- **Q-024** — the repository-layout contract still names the "product
  catalogue" under `crm-service`, which conflicts with D-02. Owner: architecture
  owner. Due: phase 2.
- **Q-003, Q-004, Q-005** — currency and tax scope, billing-cycle, proration,
  rounding and finalisation rules, and credit-memo approval thresholds remain
  open. The model stores the data those rules need (currency codes, tax rates
  with effective dates, approval steps on a credit memo) without deciding them.
