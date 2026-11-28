# Bounded Contexts

## 1. Purpose

Define the explicit boundaries of the `clinic-system` domain model: which
business capability each context owns, which concepts live inside it, and which
business rules it enforces.

This document is the authority for context ownership.
[context-map.md](context-map.md) describes how the contexts integrate, and
[architecture-decisions.md](architecture-decisions.md) records why the system is
a modular monolith.

## 2. Definition

A **bounded context** is an explicit boundary within which a domain model, its
terminology, and its business rules have one consistent meaning. The same
real-world person can appear in several contexts without those contexts sharing
one model.

| Context | Meaning of `Patient` |
|---|---|
| Patient Management | A person registered with the clinic |
| Appointment Management | A person requesting or attending an appointment |
| Clinical Management | A person receiving healthcare |
| Billing & Payments | A person responsible for payment or an account balance |

These meanings are related, but they are not interchangeable.

## 3. Why boundaries are needed

One large `Patient` class holding `appointments`, `diagnoses`,
`prescriptions`, `invoices`, `payments`, and `insurance_details` has too many
reasons to change:

| Problem | Consequence |
|---|---|
| Too many responsibilities | The class cannot be described with one business purpose |
| Strong coupling | A billing change can affect clinical code |
| Mixed rules | Registration, clinical, and financial invariants compete in one place |
| Slow testing | Testing one capability drags in unrelated behavior |
| Ambiguous language | `Patient` means registration, care, and payment at the same time |

Boundaries replace that class with four models, each with one owner. A context
references another context's aggregate only by identity (`patient_id`), never by
holding its object graph.

## 4. Context ownership

| Business capability | Owning context |
|---|---|
| Patient registration and identification | Patient Management |
| Patient demographics, contact details, addresses, emergency contacts | Patient Management |
| Patient status and profile updates | Patient Management |
| Appointment booking, rescheduling, cancellation, reminders | Appointment Management |
| Appointment-slot availability and conflict checks | Appointment Management |
| Clinical encounters, diagnoses, observations, prescriptions | Clinical Management |
| Service charges, invoices, payments, refunds, outstanding balances | Billing & Payments |

The availability item means the appointment-level rule: whether a practitioner
can be booked in a slot, enforced by the `AppointmentAvailabilityService` in
[`../domain/domain-services.md`](../domain/domain-services.md). It does not
transfer ownership of a practitioner's working schedule; that remains with the
supporting Staff Management context described in
[`../domain/domain-model.md`](../domain/domain-model.md).

Staff Management is not one of the four primary contexts in this design. It
remains a supporting upstream context for practitioner identity and working
schedules. Two vocabulary differences are inherited from the existing domain
documents and must be reconciled before implementation:

- requirements say `Practitioner`, but the ubiquitous language uses `Doctor`
  (see [`../domain/glossary.md`](../domain/glossary.md)); this document uses
  `doctor_id` in contracts and keeps "practitioner" in prose;
- [`../domain/domain-model.md`](../domain/domain-model.md) places
  `Prescription` in a future Medication context, while this step assigns
  medication requests to Clinical Management. The two documents disagree on
  ownership until that decision is revisited.

## 5. Patient Management Context

**Business responsibility:** maintain the clinic's patient registration and
demographic records. This context owns the authoritative registration record.

**Belongs here:** patient registration, patient identification, demographics,
contact information, address management, emergency contacts, patient status,
and patient profile updates.

**Does not belong here:** appointments, encounters, diagnoses, prescriptions,
invoices, payments, or insurance claim state.

| Type | Concept | Notes |
|---|---|---|
| Aggregate root | `Patient` | The authoritative registration record |
| Attribute | `identity_number` | Unique registration identity owned by `Patient` |
| Entity | `PatientContact` | Contact details with their own continuity inside the aggregate |
| Value object | `PatientName` | First and last name |
| Value object | `DateOfBirth` | Validated date of birth |
| Value object | `Address` | Postal address |
| Value object | `MedicalRecordNumber` | Clinical identifier assigned to the patient |

**Business rules:**

- every patient has a unique registration identity (`identity_number`);
- a patient has a valid date of birth;
- required registration information is present;
- only authorized users can update patient information.

## 6. Appointment Management Context

**Business responsibility:** manage scheduling. It decides whether a slot can
be reserved and owns the appointment lifecycle.

**Belongs here:** appointment booking, availability checks, rescheduling,
cancellation, practitioner scheduling for appointments, appointment status, and
appointment reminders.

**Does not belong here:** registration data, clinical documentation, or
financial data.

| Type | Concept | Notes |
|---|---|---|
| Aggregate root | `Appointment` | Owns the scheduling lifecycle |
| Entity | `AppointmentParticipant` | Patient or practitioner role in the appointment |
| Value object | `AppointmentPeriod` | Valid time period; the current model calls this `TimeSlot` |
| Value object | `AppointmentStatus` | `SCHEDULED`, `CONFIRMED`, `CANCELLED`, `COMPLETED`, `NO_SHOW` |
| Value object | `AppointmentType` | Kind of appointment |

The Stage 1 lifecycle in
[`../domain/appointment-lifecycle.md`](../domain/appointment-lifecycle.md) adds
`CHECKED_IN` before `COMPLETED`.

`Appointment` stores `patient_id` and `doctor_id`, not a `Patient` or
`StaffMember` object. This is a deliberate DDD decision: cross-context
references are identities, not object graphs.

**Business rules:**

- an appointment must reference a registered patient;
- an appointment must have a valid time period;
- a practitioner cannot have conflicting appointments;
- a cancelled appointment cannot be treated as active;
- rescheduling must respect the same availability rules as booking.

## 7. Clinical Management Context

**Business responsibility:** manage healthcare delivery and clinical
information. It has its own representation of patient identity and does not own
registration data.

**Belongs here:** clinical encounters, diagnoses, allergies, observations,
vital signs, laboratory results, medication requests, medication
administration, procedures, care plans, and clinical documentation.

**Does not belong here:** appointment availability, invoicing, payment state, or
patient registration.

| Type | Concept | Notes |
|---|---|---|
| Aggregate root | `Encounter` | Owns clinical records created during care |
| Entity | `Diagnosis` | Clinical assessment within the encounter |
| Entity | `ClinicalNote` | Amended rather than overwritten |
| Value object | `BloodPressure` | Validated measurement and units |
| Value object | `BodyTemperature` | Validated measurement and units |
| Value object | `ClinicalCode` | Code system plus code value |

**Business rules:**

- a clinical encounter references a patient;
- clinical records preserve their history;
- only authorized practitioners create or update certain clinical records;
- observations have valid measurements and units;
- documentation follows completion and amendment rules.

## 8. Billing & Payments Context

**Business responsibility:** manage financial transactions for clinic services.

**Belongs here:** service charges, invoice generation, invoice items, payment
processing, payment allocation, refunds, insurance claims if included in scope,
and outstanding balances.

**Does not belong here:** clinical decisions, scheduling, or patient
registration.

| Type | Concept | Notes |
|---|---|---|
| Aggregate root | `Invoice` | Owns items, totals, and invoice status |
| Aggregate root | `Payment` | Has its own identity, lifecycle, and transaction history |
| Entity | `InvoiceItem` | A billable service or charge |
| Value object | `Money` | Amount and currency; replaces an unrestricted integer |
| Value object | `PaymentMethod` | How money was tendered |
| Value object | `InvoiceStatus` | `DRAFT`, `ISSUED`, `PAID`, `OVERDUE` |

**Business rules:**

- an invoice has at least one billable item;
- invoice totals are calculated correctly;
- a payment cannot exceed the outstanding balance unless an explicit
  overpayment policy allows it;
- a refunded payment retains its transaction history;
- financial transactions are auditable.

## 9. Aggregate ownership

| Aggregate root | Owner | Seen by other contexts as |
|---|---|---|
| `Patient` | Patient Management | `patient_id` plus an explicit integration contract |
| `Appointment` | Appointment Management | `appointment_id` and published appointment facts |
| `Encounter` | Clinical Management | `encounter_id` and published billable-service facts |
| `Invoice` | Billing & Payments | `invoice_id`; no other context changes its state |
| `Payment` | Billing & Payments | `payment_id` and payment status from an integration contract |

An aggregate is never modified from outside its owning context. Clinical
Management does not create invoices; Appointment Management does not update
patient demographics; Billing does not change encounter status.

## 10. Boundary rules

- Code in one context must not import domain classes from another context.
- Code in one context must not read or write another context's tables directly.
- Cross-context information passes through the interfaces and events documented
  in [context-map.md](context-map.md).
- A shared database is allowed; shared ownership is not. Each context keeps its
  own persistence boundary.
- A context may keep a local copy of information it needs, but that copy is its
  own model, not another context's aggregate.

## 11. Verification checklist

- [x] The four bounded contexts and their responsibilities are defined.
- [x] `Patient`, `Appointment`, `Encounter`, `Invoice`, and `Payment` have one
      owning context each.
- [x] Each context lists what belongs inside and what stays outside.
- [x] Cross-context references are identities, not object graphs.
- [x] Business rules are assigned to the context that owns the capability.
- [x] Known conflicts with earlier domain documents are recorded, not hidden.

## 12. Related documents

- [context-map.md](context-map.md) — relationships, patterns, and contracts.
- [architecture-decisions.md](architecture-decisions.md) — modular monolith and
  integration decisions.
- [`../domain/domain-model.md`](../domain/domain-model.md) — earlier aggregate
  and lifecycle model.
- [`../domain/domain-services.md`](../domain/domain-services.md) — appointment
  availability rule.
- [`../domain/glossary.md`](../domain/glossary.md) — authoritative vocabulary.
