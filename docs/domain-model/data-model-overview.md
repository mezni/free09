# Domain Model Overview

**Status**: Approved — the non-specialist description of the phase-2 data model
**Phase**: Phase 2 — Data model and database foundation
**Companion documents**: the table-by-table dictionary is
[`specs/003-build-phase2/data-model.md`](../../specs/003-build-phase2/data-model.md);
the decisions behind it are
[`specs/003-build-phase2/research.md`](../../specs/003-build-phase2/research.md).

This document explains what the platform stores and why, in the terms a domain
owner or reviewer uses. It deliberately holds no column types and no index
definitions — those are in the data dictionary. Read this document to review
the model; read the dictionary to implement it.

## 1. The short version

The platform stores four groups of things, and each group belongs to exactly
one team:

| Group | Owner | Plainly |
|---|---|---|
| Identity | `auth-service` | Who can sign in, what they may do, and what happened when they tried |
| Customers | `crm-service` | Who the customers are, how to reach them, what they asked for, and what has happened to their cases |
| Products and services | `inventory-service` | What the operator sells, what each subscriber holds, which devices and SIMs exist, and what has been provisioned |
| Money | `billing-service` | What is owed, what was paid, what the ledger says happened |

Two rules hold the model together. **Each piece of data has exactly one
owner**, so there is never a question of which copy is correct. **A service
may only write its own group's data**, and it reaches the other groups through
their APIs rather than through their tables.

## 2. The story the model tells

A **customer** buys services from the operator. A **subscriber** is the
identity that actually carries the service — a SIM, a line, an account the
customer can be reached on. A **subscription** is what a subscriber holds: a
rate plan taken from the catalogue, plus any add-ons. A **billing account** is
the thing that gets invoiced. An **invoice** states what was owed in one
period, itemised as **lines**. A **payment** is money received, and
**allocations** apply it to invoices. Every financial movement is written to
the **ledger**, which is never edited.

## 3. Concepts that must stay distinct

- **Customer**: a person or organisation receiving commercial services.
- **Subscriber**: the service identity that holds subscriptions. One customer
  may have many subscribers; a subscriber is not a login and not an invoice.
- **Billing account**: the entity responsible for invoices and payments. A
  customer may have more than one.
- **Subscription**: a customer-specific purchase or activation of a product or
  rate plan, with its own status and its own period.
- **Service/device asset**: a device, or a SIM/eSIM, assigned to a subscriber
  for a period.

Do not assume one customer equals one subscriber, one billing account, or one
subscription.

## 4. Catalogue and subscription concepts

- **Product**: a sellable commercial definition.
- **Product version**: a time-bounded or versioned definition.
- **Rate plan**: a commercial/technical plan definition.
- **Rate-plan version**: versioned prices, quotas, and terms, in force over a
  period.
- **Add-on**: an optional product or feature.
- **Subscription**: a customer-specific purchase or activation with status and
  effective dates.
- **Subscription add-on**: an add-on attached to a subscription with its own
  lifecycle.

The catalogue is **shared**: the billing group needs the prices, and the
customer group needs to show what a customer holds. It is owned once, by the
products and services group, and the others read it through that group's API.
No other group keeps a copy.

Historical invoices must remain explainable when prices or plan definitions
change — see §6.

## 5. Device and provisioning concepts

- **Device**: physical equipment, with relevant identifiers such as IMEI and
  serial number.
- **SIM/eSIM**: SIM identity, with ICCID and lifecycle state; an eSIM profile
  lifecycle may require additional entities.
- **Assignment**: a time-bounded association between an asset and a
  subscriber or subscription.
- **Provisioning profile**: a configuration template such as APN or VoLTE
  parameters.
- **Provisioning job**: an activation or change request with status, attempts,
  timestamps, and sanitised failure details.

An inventory assignment does not prove that a service is provisioned. Commercial
and network lifecycle states remain distinct, and a provisioning job's outcome
is never inferred from a subscription's status.

## 6. How history is kept, in three ways

The model keeps history three ways, and which one applies depends on what the
record is:

1. **Things that change over time** — a plan's price, a subscription, a SIM
   assignment — are written as a series of rows. Each row says when it came
   into force, and the last one has no end date. Asking "what was in force in
   March?" is then a question with an answer, rather than a reconstruction.
2. **Things that happened** — a security event, a ticket status change, a
   ledger posting — are written once and never edited. They are a trail, not a
   current value.
3. **Things that were priced** — an invoice line copies the price, quota, and
   terms it was charged from. If the operator changes the price tomorrow, the
   invoice issued last month still shows what the customer was actually
   charged, and why.

There is no separate "history table" for every record. Each record says which
of the three ways it keeps its history.

## 7. What crosses a group boundary, and what does not

A record may point at a record owned by another group — a subscription points
at the subscriber it belongs to. It points by identifier only; the database
does **not** enforce the link with a foreign key across groups.

The reason is coupling. If one group's table were constrained by another
group's table, changing the second would silently break the first, and one
group's migration could not be applied on its own. Carrying the identifier
keeps that relationship at the level of a documented API, where it is
reviewed and versioned like any other contract.

Within a group, links are enforced normally, and a record that others depend
on is not deleted out from under them.

## 8. Money

- Every amount is stored as a decimal, never as a floating-point number, and
  every amount carries the currency it is in.
- An amount is never quietly rounded; where a rounding rule applies, it is a
  stated business rule, and it is decided with the billing rules rather than
  assumed here.
- The sum of a payment's allocations never exceeds the payment, and never
  exceeds what is outstanding on the invoice.
- A posted ledger entry is never edited or deleted. A correction is a
  compensating entry that leaves the original in place, so the ledger always
  explains itself.
- Every ledger posting names the event that caused it and the request it came
  from, so any movement can be traced back to what triggered it.

## 9. Invariants to formalize

These are the rules the model holds to; the migrations and the later phases
must not break them.

- Every subscription references a valid customer/subscriber and valid
  product/plan version.
- Asset identifiers follow explicit uniqueness and lifecycle rules.
- Every invoice line belongs to an invoice.
- Invoice totals reconcile according to documented tax and rounding rules.
- Payment allocations cannot exceed the permitted allocatable payment amount
  or obligation balance, unless a documented exception applies.
- Posted ledger entries are immutable.
- Credit memos obey approval policy and reference a valid source transaction
  where required.
- A provisioning job's outcome is not silently inferred from subscription
  status.
- Historical prices and terms are retained or snapshotted sufficiently to
  explain past charges.

## 10. How a reviewer can check this model

A reviewer who does not read the migrations can check the following against
this document and the dictionary:

- Every domain appears once, with one owning service, and no other service
  writes to it.
- Every table states its key, its links, its constraints, its lifecycle, its
  history form, and its data classification.
- Every table that more than one domain reads has one owner.
- Every amount is decimal and carries a currency.
- Every rule in §9 is stated, and the table that holds it is named.

## 11. Required next artifacts

The remaining artefacts the platform still owes are recorded by the build
plan, not by this phase:

- The initial migration set, the migration policy, and the local database
  environment (Phase 2, tasks T009–T012).
- The billing rules this model stores but does not decide: billing cycles,
  proration, rounding, invoice finalisation, tax scope, and credit-memo
  approval thresholds (Phase 6). The questions and their owners are in
  [`docs/risks/open-questions.md`](../risks/open-questions.md).
- The tenant decision (Phase 9): the model carries no tenant column, because
  that decision has not been taken.
