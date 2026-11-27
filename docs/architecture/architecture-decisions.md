# Architecture Decisions

## 1. Purpose

Record the significant architecture choices for `clinic-system` and the
reasoning behind them. Code shows what exists; this document explains why these
boundaries and integration mechanisms were chosen and which alternatives were
rejected.

The decisions are initial. When one changes, record a new decision here or in a
dedicated ADR and update [context-map.md](context-map.md) at the same time; do
not silently rewrite history.

## 2. Status

| Item | Value |
|---|---|
| Status | Accepted |
| Date | 2026-11-27 |
| Scope | Initial architecture of `clinic-system` |
| Authority | [bounded-contexts.md](bounded-contexts.md) for ownership; [context-map.md](context-map.md) for integration |

## 3. Context

- The system serves one clinic and is in early development.
- The domain model is still changing; several concepts are recorded as future
  work in [`../domain/domain-model.md`](../domain/domain-model.md).
- The team needs to test business rules without databases, brokers, or web
  servers.
- There is no documented requirement for independent deployment or independent
  scaling of business capabilities.
- Clear boundaries are required now; distributed-system complexity is not.

## 4. Decision summary

| Decision | Choice |
|---|---|
| Architecture style | Modular monolith |
| Domain boundaries | Four primary bounded contexts |
| Domain model ownership | Each context owns its model and business rules |
| Context communication | Application interfaces and in-process domain events |
| Shared database initially | Yes, with separate persistence boundaries per context |
| Direct cross-context table access | No |
| Microservices | Not now |
| External integrations | Adapters with an Anti-Corruption Layer where necessary |

## 5. ADR-001: Use a modular monolith

### Context

Boundaries are needed, but the product is one application with one deployment.
Introducing separate services would add network calls, distributed transactions,
deployment coordination, and operational work before the domain is stable.

### Decision

Build one application with clearly separated modules for the four contexts.
One deployment, one codebase, independent domain models, and controlled
communication between modules.

### Alternatives considered

| Alternative | Assessment |
|---|---|
| Microservices from the start | Rejected: distributed complexity before boundaries or deployment needs are proven |
| One undifferentiated domain model | Rejected: couples registration, scheduling, clinical, and financial rules |
| Separate services per aggregate | Rejected: fine-grained services amplify coupling and coordination cost |

### Consequences

- Boundaries are enforced by code structure, interfaces, and review.
- Refactoring a boundary is cheaper than changing a service contract.
- Contexts share one process and one deployment; they cannot scale or deploy
  independently yet.
- Boundary violations are easy to introduce and must be checked in code review
  and architecture tests.

## 6. ADR-002: Four bounded contexts with independent models

### Context

The same patient appears in registration, scheduling, care, and payment. One
model would mix four sets of business rules and four meanings of `Patient`.

### Decision

Adopt the four contexts defined in
[bounded-contexts.md](bounded-contexts.md): Patient Management, Appointment
Management, Clinical Management, and Billing & Payments. Each owns its
aggregates, terminology, and rules. Other contexts hold identities, not object
graphs. Staff Management remains a supporting context outside the four.

### Alternatives considered

| Alternative | Assessment |
|---|---|
| Single large `Patient` class with all lists | Rejected: too many responsibilities and reasons to change |
| Contexts defined by technical layer | Rejected: layers do not establish business ownership |
| Add all future contexts now | Deferred: Medication, Laboratory, and Audit are recorded as future work |

### Consequences

- `patient_id` is a reference in three contexts; only Patient Management owns
  the registration record.
- Each context can change its model without changing the others, provided the
  integration contract is stable.
- Some data is duplicated as local copies; that duplication is intentional and
  owned locally.

## 7. ADR-003: Integrate through application interfaces and events

### Context

Workflows cross capabilities: booking needs registration, clinical care needs
appointment facts, and invoicing needs completed encounters. Direct calls into
another context's domain objects would couple the models.

### Decision

Use application-level interfaces when a consumer needs a fact immediately and
domain events when a consumer reacts to a fact that has already happened. Only
contracts and published facts cross a boundary. Dispatch events in process
after the producing aggregate is saved.

### Alternatives considered

| Alternative | Assessment |
|---|---|
| Share domain objects between modules | Rejected: makes one context's model another context's dependency |
| Join across context tables in queries | Rejected: bypasses ownership and rules |
| Synchronous HTTP between modules | Deferred: unnecessary inside one process |
| Message broker now | Deferred: Kafka or RabbitMQ adds infrastructure without a current need |

### Consequences

- Consumers stay independent of producer internals.
- Handlers must be idempotent because dispatch can be retried.
- Save-then-dispatch can lose an event on a crash; the transactional outbox is
  the planned fix described in
  [`../domain/domain-events.md`](../domain/domain-events.md).
- Published events are part of the contract and need careful versioning.

## 8. ADR-004: Share a database, not ownership

### Context

A modular monolith can use one database without merging the domain models. The
question is where ownership lies, not how many physical schemas exist.

### Decision

A shared database is acceptable initially. Each context has its own persistence
boundary and repository contracts; no context reads or writes another context's
tables. Other contexts interact only through the interfaces and events in
[context-map.md](context-map.md).

### Alternatives considered

| Alternative | Assessment |
|---|---|
| One database per context now | Deferred: useful for isolation, but premature before deployment boundaries exist |
| One shared schema with shared ORM models | Rejected: recreates the coupled model under a different name |

### Consequences

- Fewer deployment and migration mechanisms in the first implementation.
- Table names and foreign keys must not be treated as integration contracts.
- Splitting storage later is possible because contexts do not access each
  other's tables.

## 9. ADR-005: Choose context mapping patterns explicitly

### Context

Each upstream/downstream relationship needs an integration style. Different
relationships have different needs, so one pattern does not fit all of them.

### Decision

| Relationship | Pattern | Status | Revisit when |
|---|---|---|---|
| Patient → Appointment | Customer-Supplier | Accepted | The patient contract no longer satisfies booking needs |
| Patient → Clinical | Open Host Service | Accepted | A second consumer needs a different patient view |
| Patient → Billing | Published Language | Accepted | Event versioning becomes a problem |
| Appointment → Clinical | Published Language | Accepted | Clinical needs synchronous availability or status queries |
| Clinical → Billing | Customer-Supplier | Accepted | Billing needs more than completed-encounter facts |
| External provider → Billing | Anti-Corruption Layer | Accepted | The provider adopts our contract exactly |

Shared Kernel is limited to identifiers used by value; Conformist is rejected
for internal contexts because it strengthens upstream coupling; Separate Ways
applies where no integration is needed.

### Consequences

- Every cross-context dependency has an owner and a named integration style.
- Upstream contexts must keep their published contracts stable for downstream
  customers.
- Changes to a pattern require an update to the context map, not just code.

## 10. ADR-006: Translate external payment provider models

### Context

An external provider uses its own fields and states, for example
`customer_reference` and `invoice_state`. Those terms do not belong in
`Invoice`, `Payment`, or `InvoiceStatus`.

### Decision

Place an adapter at the boundary. It translates provider statuses, amounts, and
references into Billing's own value objects and rejects unsupported values. No
provider DTO is stored as a domain object.

### Alternatives considered

| Alternative | Assessment |
|---|---|
| Conform to the provider model | Rejected: leaks foreign terminology into our domain |
| Store provider responses unchanged | Rejected: makes future provider changes affect domain code |

### Consequences

- Billing rules are expressed only in Billing terminology.
- Adding a provider means adding an adapter, not changing the domain.
- Translation and unsupported-value handling need their own tests.

## 11. Overall consequences

| Effect | Detail |
|---|---|
| Positive | Business rules live with the context that owns them |
| Positive | Billing, clinical, and scheduling code can change independently |
| Positive | Tests can exercise domain rules without infrastructure |
| Cost | More modules, contracts, and adapters to maintain |
| Cost | Local copies of cross-context data can become stale |
| Risk | Module boundaries can erode without review and architecture tests |
| Risk | In-process event delivery needs an outbox before production reliability |

## 12. When to revisit

Consider separate deployment or services when:

- a context needs independent scaling or release cadence;
- separate teams own separate contexts and need contract-based coordination;
- reliability isolation becomes more important than transactional simplicity;
- the shared database becomes a deployment bottleneck;
- durable cross-context event delivery is required at scale.

Until then, refine modules and contracts rather than adding infrastructure.

## 13. Verification checklist

- [x] Modular monolith chosen instead of microservices, with reasons.
- [x] Four bounded contexts and independent domain models recorded.
- [x] Application interfaces and domain events chosen for communication.
- [x] Shared database separated from shared ownership.
- [x] Direct cross-context table access rejected.
- [x] Integration patterns assigned per relationship in the context map.
- [x] External integrations protected by an Anti-Corruption Layer.
- [x] Revisit criteria recorded for future architectural change.

## 14. Related documents

- [bounded-contexts.md](bounded-contexts.md) — responsibilities and ownership.
- [context-map.md](context-map.md) — upstream/downstream relationships and
  patterns.
- [`../domain/domain-events.md`](../domain/domain-events.md) — event dispatch
  order, idempotency, and outbox plan.
- [`../domain/domain-model.md`](../domain/domain-model.md) — current domain
  model and open questions.
