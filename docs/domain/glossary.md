# Domain Glossary

## 1. Purpose

Define the business terminology of the clinic domain. Each term has one meaning
across the system. When a term is not listed here or is marked as not used,
do not introduce it as a domain concept.

## 2. Core Concepts

### Patient

A person registered with the clinic to receive healthcare services.

| Term | Definition |
|---|---|
| Patient ID | Unique aggregate identifier |
| Registration Identity (`identity_number`) | Unique clinic registration identity owned by `Patient` |
| Patient Record | Information maintained about a patient |
| Medical History | Patient's historical health information |
| Contact Information | Patient's phone, email, and address |
| Registration | Process of registering a new patient |

A patient is a healthcare recipient, not a customer or a client. Billing
relationships do not change the term used for the person receiving care.

### Appointment

A scheduled time for a patient to receive a clinic service.

| Term | Definition |
|---|---|
| Appointment ID | Unique appointment identifier |
| Appointment Slot | Period available for booking |
| Appointment Schedule | Collection of scheduled appointments |
| Cancellation | Termination of a scheduled appointment |
| Rescheduling | Changing an appointment's date or time |
| No-show | Patient does not attend the appointment |
| Check-in | Recording the patient's arrival |

An appointment is a plan, not the clinical interaction itself. It has a
lifecycle: scheduled, confirmed, cancelled, completed, or no-show.

### Encounter

An actual clinical interaction between a patient and a healthcare professional.

| Term | Definition |
|---|---|
| Encounter ID | Unique clinical encounter identifier |
| Consultation | Professional medical assessment |
| Diagnosis | Clinical identification of a health condition |
| Treatment | Intervention performed to address a diagnosed condition |
| Treatment Plan | Planned medical interventions |
| Clinical Note | Documentation of clinical observations |
| Prescription | Medication order issued by an authorized provider |
| Vital Signs | Measurements such as blood pressure and temperature |

An encounter records clinical care. Check-in at an appointment records
arrival; it does not create an encounter by itself.

### Staff

| Term | Definition |
|---|---|
| Staff Member | Person working for the clinic |
| Doctor | Healthcare professional providing medical care |
| Nurse | Healthcare professional providing nursing care |
| Receptionist | Staff member managing patient reception |
| Availability | Period when a staff member can work |
| Working Schedule | Defined working hours |
| Role | Responsibility assigned to a staff member |

`Doctor` is a specific professional role; `Staff Member` is the general term
for anyone employed by the clinic. Requirements that refer to a `Practitioner`
describe a clinic healthcare professional; when medical care is being
provided, use `Doctor` in this domain vocabulary.

### Billing and Payments

| Term | Definition |
|---|---|
| Invoice | Document requesting payment |
| Invoice Item | Individual service or charge on an invoice |
| Payment | Money received against an amount owed |
| Outstanding Balance | Amount still owed |
| Refund | Money returned to a patient |
| Service Fee | Amount charged for a clinic service |

## 3. Important Business Distinctions

| Concept A | Concept B | Difference |
|---|---|---|
| Patient | Staff Member | Healthcare recipient vs clinic employee |
| Appointment | Encounter | Planned visit vs actual clinical interaction |
| Doctor | Staff Member | Specific professional role vs general employee |
| Invoice | Payment | Amount requested vs money received |
| Cancellation | No-show | Appointment cancelled vs patient fails to attend |
| Diagnosis | Treatment | Identified condition vs intervention |

Additional distinctions:

- `Appointment` vs `Appointment Slot`: the reservation vs the period that can
  be reserved.
- `Check-in` vs `Encounter`: arrival recorded vs clinical care provided.
- `Consultation` vs `Encounter`: a professional medical assessment vs the
  complete clinical interaction in which it may occur.
- `Clinical Note` vs `Medical History`: documentation of one encounter vs the
  patient's accumulated historical health information.
- `Prescription` vs `Treatment Plan`: a medication order vs the overall plan
  of interventions.

## 4. Terms Not Used as Domain Concepts

| Avoid | Use instead | Reason |
|---|---|---|
| Customer | Patient | The person receiving care is not defined by payment |
| Client | Patient | Registration does not create a different identity |
| Visit | Appointment or Encounter | Ambiguous between a plan and actual care |
| Consultation (as a synonym for encounter) | Encounter | Consultation is an assessment within care |

> **DDD rule:** Similar words do not automatically represent the same domain
> object. An `Appointment` and an `Encounter` must never share one entity.
