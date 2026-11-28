
# Use Cases

## 1. Purpose

Describe the main interactions between clinic-system actors
and the application.

## 2. Actors

| Actor | Description |
|---|---|
| Clinic Administrator | Manages clinic configuration and users |
| Receptionist | Registers patients and manages appointments |
| Physician | Manages consultations and clinical records |
| Nurse | Records observations and clinical information |
| Laboratory Technician | Manages laboratory results |
| Pharmacist | Handles medication-related workflows |
| Patient | Accesses permitted personal information |
| IT Administrator | Maintains technical infrastructure |

## 3. Use Case Inventory

| ID | Name | Primary Actor |
|---|---|---|
| UC-PAT-001 | Register Patient | Receptionist |
| UC-PAT-002 | Search Patients | Receptionist |
| UC-PAT-003 | Update Patient | Authorized User |
| UC-PRA-001 | Register Practitioner | Administrator |
| UC-APT-001 | Schedule Appointment | Receptionist |
| UC-APT-002 | Reschedule Appointment | Receptionist |
| UC-APT-003 | Cancel Appointment | Receptionist |
| UC-APT-004 | View Appointment Calendar | Receptionist |
| UC-ENC-001 | Start Encounter | Physician |
| UC-ENC-002 | Complete Encounter | Physician |
| UC-CLI-001 | Review Clinical Records | Physician |
| UC-MED-001 | Manage Medication | Authorized Clinician |
| UC-LAB-001 | Record Laboratory Result | Laboratory Technician |
| UC-IAM-001 | Assign User Role | Administrator |
| UC-AUD-001 | Review Audit Records | Administrator |

## 4. Detailed Use Case: UC-PAT-001

### Name
Register Patient

### Primary Actor
Receptionist

### Goal
Create a patient record.

### Preconditions
- User is authenticated.
- User has patient:create permission.
- Clinic is active.

### Trigger
Receptionist selects Register Patient.

### Main Flow
1. Open patient registration.
2. Enter patient information.
3. Validate required fields.
4. Check for possible duplicates.
5. Confirm the information.
6. Create patient record.
7. Generate `Patient ID` and capture unique registration identity (`identity_number`).
8. Record audit event.
9. Display patient record.

### Alternative Flows
- A1: Invalid input: display validation errors.
- A2: Possible duplicate: display matching patients.
- A3: Unauthorized: reject operation.
- A4: Database unavailable: return controlled error.

### Postconditions
- Patient record exists.
- Patient has a unique `Patient ID` and registration identity.
- Creation event is auditable.

## 5. Business Rules

- BR-PAT-001: Every patient has a unique system identifier and registration identity.
- BR-PAT-002: Patient date of birth must be valid.
- BR-PAT-003: Possible duplicates require review.
- BR-PAT-004: Patient creation requires authorization.
- BR-PAT-005: Patient creation must be auditable.
- BR-PAT-006: Patient records must not be silently deleted.

## 6. Open Questions

- What patient identification information is mandatory?
- How should duplicate patients be resolved?
- Can a patient be registered without a phone number?
- Who can correct patient demographic information?
- What is the process for merging duplicate records?

