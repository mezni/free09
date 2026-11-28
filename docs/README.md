# Documentation Index

## 1. Purpose

This directory is the reference for `clinic-system`. It records what the system
must do (requirements), what the business concepts mean (domain), and how the
software is structured (architecture).

Most documents describe design intent. Source modules are introduced
progressively, so a written rule or component is not necessarily implemented
yet.

## 2. Architecture

| Document | Contents |
|---|---|
| [bounded-contexts.md](architecture/bounded-contexts.md) | Four contexts, responsibilities, aggregate ownership, and boundaries |
| [context-map.md](architecture/context-map.md) | Upstream/downstream relationships, mapping patterns, contracts, and context map |
| [architecture-decisions.md](architecture/architecture-decisions.md) | Modular monolith rationale, ADRs, consequences, and revisit criteria |
| [layered-architecture.md](architecture/layered-architecture.md) | Presentation, Application, Domain, Infrastructure; dependency direction; repository port |
| [solid-principles.md](architecture/solid-principles.md) | Five SOLID principles, bad and refactored examples, Patient Management design |
| [design-patterns.md](architecture/design-patterns.md) | Pattern categories, Python implementations, DDD/SOLID links, and adoption decisions |
| [application-layer-use-cases.md](architecture/application-layer-use-cases.md) | Use cases, commands, DTOs, DI, transaction boundaries, and event coordination |
| [infrastructure-and-persistence.md](architecture/infrastructure-and-persistence.md) | PostgreSQL, SQLAlchemy, ORM models, mappers, repositories, Unit of Work, transactions, and Alembic |

Start here for context ownership and boundaries. The other architecture
documents build on those decisions.

## 3. Domain

| Document | Contents |
|---|---|
| [README.md](domain/README.md) | Domain documentation guide and vocabulary principles |
| [glossary.md](domain/glossary.md) | Business terminology and distinctions between similar terms |
| [ubiquitous-language.md](domain/ubiquitous-language.md) | Business statements, domain interpretations, and naming conventions |
| [domain-model.md](domain/domain-model.md) | Bounded contexts, aggregates, relationships, and lifecycles |
| [domain-modeling.md](domain/domain-modeling.md) | Entities, value objects, aggregates, invariants, and the four primary aggregates |
| [domain-services-events-repositories.md](domain/domain-services-events-repositories.md) | Domain services, events, handlers, repositories, Unit of Work, and Outbox decisions |
| [entities.md](domain/entities.md) | Concepts with identity and the aggregate roots that own them |
| [value-objects.md](domain/value-objects.md) | Concepts defined by their values |
| [domain-rules.md](domain/domain-rules.md) | Business invariants and where they are enforced |
| [aggregates.md](domain/aggregates.md) | Aggregate boundaries and what belongs inside the appointment aggregate |
| [aggregate-roots.md](domain/aggregate-roots.md) | The root as the only entry point for changing aggregate state |
| [domain-invariants.md](domain/domain-invariants.md) | Appointment invariants, owners, and enforcement |
| [appointment-lifecycle.md](domain/appointment-lifecycle.md) | Appointment statuses and allowed transitions |
| [domain-services.md](domain/domain-services.md) | Business logic that does not belong to one Entity or Value Object |
| [application-services.md](domain/application-services.md) | Use-case orchestration and its boundaries |
| [domain-events.md](domain/domain-events.md) | Business facts, dispatch, and delivery concerns |
| [appointment-booking-workflow.md](domain/appointment-booking-workflow.md) | Complete `BookAppointment` use case across all layers |

The domain guide also records known differences between earlier documents, for
example the `CHECKED_IN` status introduced in Stage 1. Check those notes before
changing the model.

## 4. Requirements

| Document | Contents |
|---|---|
| [product-overview.md](requirements/product-overview.md) | Product purpose and scope |
| [stakeholders.md](requirements/stakeholders.md) | Stakeholders and user roles |
| [functional-requirements.md](requirements/functional-requirements.md) | Functional requirements by capability |
| [non-functional-requirements.md](requirements/non-functional-requirements.md) | Quality attributes and technical constraints |
| [use-cases.md](requirements/use-cases.md) | Use cases, flows, and business rules |

## 5. Suggested reading order

1. [product overview](requirements/product-overview.md) and
   [use cases](requirements/use-cases.md) — what the clinic needs.
2. [glossary](domain/glossary.md) and
   [ubiquitous language](domain/ubiquitous-language.md) — the shared vocabulary.
3. [domain model](domain/domain-model.md) and
   [domain rules](domain/domain-rules.md) — the concepts and their rules.
4. [bounded contexts](architecture/bounded-contexts.md) and
   [context map](architecture/context-map.md) — the boundaries and integration.
5. [layered architecture](architecture/layered-architecture.md) and
   [SOLID principles](architecture/solid-principles.md) — the internal design.

[architecture-decisions.md](architecture/architecture-decisions.md) explains why
the architectural choices were made and when they should be revisited.
