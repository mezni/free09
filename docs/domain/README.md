# Clinic Domain Documentation

## 1. Purpose

This directory documents the business domain of `clinic-system`: a system for
managing patients, appointments, clinical care, staff, and billing for a
primary-care clinic.

The documentation establishes a shared business vocabulary before domain
models are implemented. It is the reference for developers, domain experts,
stakeholders, and users when they discuss clinic operations.

## 2. Why This Documentation Exists

In Domain-Driven Design (DDD), developers and domain experts should use the
same terminology. Similar words can describe different business concepts:

| Term | Possible interpretation |
|---|---|
| Patient | Person receiving medical care |
| Customer | Person paying for services |
| Client | Person registered at the clinic |
| Appointment | Scheduled visit |
| Visit | Actual patient encounter |
| Consultation | Medical interaction |

Without explicit definitions, these terms lead to incorrect entities,
relationships, and business rules. This documentation fixes their meaning
within the clinic domain.

## 3. Documents

| Document | Purpose |
|---|---|
| [glossary.md](glossary.md) | Business terminology, core concepts, and distinctions between similar terms |
| [ubiquitous-language.md](ubiquitous-language.md) | Business statements, domain interpretations, and naming conventions for future code |
| [domain-model.md](domain-model.md) | Bounded contexts, aggregates, relationships, and lifecycles |
| [domain-modeling.md](domain-modeling.md) | Entities, value objects, aggregates, invariants, and the four primary aggregates |
| [entities.md](entities.md) | Concepts with identity and the aggregate roots that own them |
| [value-objects.md](value-objects.md) | Concepts defined by their values |
| [domain-rules.md](domain-rules.md) | Business invariants and where they are enforced |
| [aggregates.md](aggregates.md) | Aggregate boundaries and what belongs inside the appointment aggregate |
| [aggregate-roots.md](aggregate-roots.md) | The root as the only entry point for changing aggregate state |
| [domain-invariants.md](domain-invariants.md) | Appointment invariants, their owners, and their enforcement |
| [appointment-lifecycle.md](appointment-lifecycle.md) | Appointment statuses and allowed state transitions |
| [domain-services.md](domain-services.md) | Business logic that does not belong to one Entity or Value Object |
| [application-services.md](application-services.md) | Use-case orchestration and its boundaries |
| [domain-events.md](domain-events.md) | Business facts recorded by the domain and delivered to interested handlers |
| [appointment-booking-workflow.md](appointment-booking-workflow.md) | The complete `BookAppointment` use case across all layers |
| [domain-services-events-repositories.md](domain-services-events-repositories.md) | Domain services, events, handlers, repositories, Unit of Work, and Outbox decisions |

## 4. Scope

The initial vocabulary covers five areas:

1. Patient management
2. Appointment management
3. Clinical management
4. Staff management
5. Billing and payments

The glossary is the authoritative vocabulary for these areas. Requirements in
[`../requirements/`](../requirements/) describe what the system must do; this
directory defines the words used to describe it. Where earlier requirements
use `Practitioner`, the specific clinical role discussed here is `Doctor`.

## 5. DDD Principle

> Similar words do not automatically represent the same domain object.

For example, an `Appointment` (a planned visit) and an `Encounter` (an actual
clinical interaction) are separate concepts and must not be represented by the
same entity.

## 6. Domain Model

Step 07 established the initial domain model in
[domain-model.md](domain-model.md), [entities.md](entities.md),
[value-objects.md](value-objects.md), and [domain-rules.md](domain-rules.md).
It identifies which concepts need identity, which are defined by their values,
and which business rules belong inside the domain.

Stage 1 refines this model in
[aggregates.md](aggregates.md), [aggregate-roots.md](aggregate-roots.md),
[domain-invariants.md](domain-invariants.md), and
[appointment-lifecycle.md](appointment-lifecycle.md). These documents describe
design intent; the next implementation step will translate the model into domain
code with tests. The Stage 1 lifecycle introduces `CHECKED_IN` and requires it
before completion, which conflicts with the earlier model in
[domain-rules.md](domain-rules.md); see the reconciliation notes in the Stage 1
documents.

The orchestration documents add the `BookAppointment` workflow: a Domain Service
checks availability, an Application Service coordinates the use case, and a
Domain Event records the successful booking. They describe design intent only;
no production code is implemented yet.
