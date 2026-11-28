# Domain Rules

## 1. Purpose

Record the business rules (invariants) that must remain true when the domain
model is implemented. Rules are expressed with the ubiquitous language from
[glossary.md](glossary.md).

This document defines where each rule belongs. Putting a rule in the wrong
layer allows the domain to enter an invalid state.

## 2. Rule Placement

| Rule type | Enforced by | Example |
|---|---|---|
| Invariant of one entity or value object | The entity or value object itself | An appointment slot must start before it ends |
| Invariant of one aggregate | The aggregate root | No overlapping appointments for the same doctor |
| Cross-context policy | Domain service with data supplied by the application layer | Doctor must be available at the requested time |
| Authorization | Application or security layer | Only a receptionist may cancel an appointment |
| Transaction and audit requirements | Application layer | Record an audit event when a clinical note changes |
| Storage uniqueness | Infrastructure as a safety net | Cannot insert two patients with the same patient ID |

Infrastructure constraints never replace domain rules. A rule that protects a
business concept belongs in the domain.

## 3. Patient Management Rules

| ID | Rule | Enforced by |
|---|---|---|
| BR-PAT-001 | Every patient has a system-generated `Patient ID` and a unique registration identity (`identity_number`) | `Patient` creation policy; infrastructure uniqueness as backup |
| BR-PAT-002 | Patient date of birth must be valid and not in the future | `Patient` |
| BR-PAT-003 | Patient contact information must be valid | `Contact Information` value object |
| BR-PAT-004 | Possible duplicate patients require review before registration is finalized | Application service with a domain duplicate-check policy |
| BR-PAT-005 | A patient record must not be silently deleted | `Patient`; only deactivation is allowed |
| BR-PAT-006 | Patient demographic changes preserve the same `Patient ID` | `Patient` |

Rules BR-PAT-001 to BR-PAT-006 correspond to the rules recorded in
[`../requirements/use-cases.md`](../requirements/use-cases.md).

## 4. Appointment Management Rules

| ID | Rule | Enforced by |
|---|---|---|
| BR-APT-001 | Every appointment has a unique `Appointment ID` | `Appointment` creation policy |
| BR-APT-002 | An appointment must reference one existing patient and one existing doctor | Application service resolves the identifiers before creation |
| BR-APT-003 | An appointment slot must have a start before its end | `Appointment Slot` value object |
| BR-APT-004 | An appointment must reserve an available slot | `Appointment` with availability data supplied by Staff Management |
| BR-APT-005 | Two appointments for the same doctor must not overlap | `Appointment` reservation policy |
| BR-APT-006 | Only valid status transitions are allowed | `Appointment Status` and `Appointment` |
| BR-APT-007 | A terminal appointment cannot be rescheduled or checked in | `Appointment` |
| BR-APT-008 | `Cancellation` and `No-show` are mutually exclusive outcomes | `Appointment` |
| BR-APT-009 | `Check-in` records arrival only; it does not create an `Encounter` | `Appointment` behavior |
| BR-APT-010 | Rescheduling releases the old slot and reserves the new slot atomically | Application transaction; `Appointment` enforces both states |

### Appointment Status Transitions

| From | Allowed operation | To |
|---|---|---|
| `SCHEDULED` | Confirm | `CONFIRMED` |
| `SCHEDULED` | Cancel | `CANCELLED` |
| `SCHEDULED` | Mark no-show | `NO_SHOW` |
| `CONFIRMED` | Check in | `CONFIRMED` with arrival recorded |
| `CONFIRMED` | Cancel | `CANCELLED` |
| `CONFIRMED` | Mark no-show | `NO_SHOW` |
| `CONFIRMED` | Complete | `COMPLETED` |
| `SCHEDULED` / `CONFIRMED` | Reschedule | `SCHEDULED` or `CONFIRMED` with new slot |
| `CANCELLED` / `COMPLETED` / `NO_SHOW` | Any status change | Not allowed |

A cancellation before the appointment time releases the slot. A no-show at the
scheduled time does not release the slot retroactively.

## 5. Clinical Management Rules

| ID | Rule | Enforced by |
|---|---|---|
| BR-ENC-001 | Every encounter has a unique `Encounter ID` | `Encounter` creation policy |
| BR-ENC-002 | An encounter belongs to one patient and one doctor | `Encounter` |
| BR-ENC-003 | An encounter is created only when care starts, never by booking an appointment | `Encounter` factory |
| BR-ENC-004 | If linked, the appointment must reference the same patient and doctor | `Encounter` with appointment data supplied by the application layer |
| BR-ENC-005 | Only valid encounter status transitions are allowed | `Encounter Status` and `Encounter` |
| BR-ENC-006 | Clinical notes are attributed to an author and cannot be silently deleted | `Encounter` and `Clinical Note` |
| BR-ENC-007 | `Diagnosis` is not the same object as `Treatment` or `Treatment Plan` | Domain model separation |
| BR-ENC-008 | Vital signs must contain valid measurements | `Vital Signs` value object |
| BR-ENC-009 | A prescription may be issued only by an authorized provider | Application policy; Medication context |
| BR-ENC-010 | Completing an encounter requires the required clinical documentation | `Encounter` |

The exact documentation required for completion is an open business question
and must be confirmed with domain experts before implementation.

### Encounter Status Transitions

| From | Operation | To |
|---|---|---|
| `IN_PROGRESS` | Complete | `COMPLETED` |
| `COMPLETED` | Any status change | Not allowed |

An encounter is never deleted. Corrections are recorded as new clinical note
content or an amendment on the existing note.

## 6. Staff Management Rules

| ID | Rule | Enforced by |
|---|---|---|
| BR-STF-001 | A staff member has one or more valid roles | `Role` value object and `StaffMember` |
| BR-STF-002 | `Doctor`, `Nurse`, and `Receptionist` describe roles, not separate people | Domain model separation |
| BR-STF-003 | Availability intervals must be valid and must not contradict the working schedule | `Availability`, `Working Schedule`, `StaffMember` |
| BR-STF-004 | Only an active doctor may be assigned to a new appointment | Application service with Staff Management data |
| BR-STF-005 | A deactivated doctor cannot start a new encounter | Application service with Staff Management data |
| BR-STF-006 | Appointment availability is derived from the doctor's working schedule and existing appointments | Cross-context policy |

## 7. Billing and Payment Rules

| ID | Rule | Enforced by |
|---|---|---|
| BR-BIL-001 | An invoice contains one or more invoice items | `Invoice` |
| BR-BIL-002 | Every invoice item has a service fee | `Invoice Item`, `Service Fee` |
| BR-BIL-003 | Invoice total equals the sum of invoice items | `Invoice` |
| BR-BIL-004 | A payment amount must be positive | `Money` value object |
| BR-BIL-005 | A payment must reference a valid invoice | Application service resolves `Invoice ID` |
| BR-BIL-006 | `Outstanding Balance` is derived and is never edited directly | `Invoice` calculation |
| BR-BIL-007 | A refund cannot exceed the payment being refunded | `Payment` |
| BR-BIL-008 | An invoice is settled only when the outstanding balance is zero | `Invoice` |
| BR-BIL-009 | Money values used together must share a currency | `Money` |

An invoice requests payment; a payment provides money. They must remain
separate records.

## 8. Cross-Aggregate Coordination

Some rules involve more than one aggregate. They are not enforced by embedding
one aggregate inside another:

- Booking checks the patient, doctor availability, and existing appointments,
  then creates the `Appointment`.
- Rescheduling releases the old slot and reserves the new one in one
  transaction.
- Starting an encounter checks the patient and doctor identities; the
  appointment link is optional and validated when present.
- Recording a payment updates the payment aggregate; the invoice derives its
  outstanding balance from all payments and refunds.

Application services orchestrate these steps. The domain owns the decisions
and state transitions.

## 9. Rules That Do Not Belong in the Domain

| Concern | Location |
|---|---|
| User authentication | Security layer |
| "Only a receptionist may reschedule" | Application policy / authorization |
| HTTP validation and error formatting | API layer |
| Database table constraints | Infrastructure |
| Audit log storage | Infrastructure, triggered by application events |
| Report formatting and filtering | Read model / query layer |

These concerns support the rules but do not define the business concepts.

## 10. Verification Checklist

Before implementing a rule, confirm:

- [ ] The rule is written using glossary terminology.
- [ ] Its owner (entity, value object, aggregate root, service, or application layer) is named.
- [ ] It protects an invariant, not just an input format.
- [ ] Cross-aggregate rules preserve aggregate boundaries.
- [ ] It is traceable to a requirement or an approved business decision.
- [ ] A test can demonstrate the rule being violated and rejected.
