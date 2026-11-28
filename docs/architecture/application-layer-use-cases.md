# Application Layer & Use Case Design

## 1. Application Layer Responsibilities

The Application Layer coordinates what users and other systems want to do. It
connects the Presentation and Infrastructure layers to the Domain Layer without
containing the core business rules.

```text
Presentation Layer    HTTP API, web interface, CLI
Application Layer     Use cases, commands, queries, DTOs, workflow coordination
Domain Layer          Entities, value objects, aggregates, domain services
Infrastructure Layer  Databases, repositories, email, external services
```

| Responsibility | Example |
|---|---|
| Coordinate a use case | `RegisterPatient`, `BookAppointment` |
| Load and save aggregates | Call `PatientRepository` and `AppointmentRepository` ports |
| Call Domain Services | `AppointmentAvailabilityService.ensure_available(...)` |
| Manage transaction boundaries | Commit or roll back through a Unit of Work |
| Coordinate domain events | Dispatch events recorded by aggregates |
| Return application results | Return the saved aggregate or an identifier DTO |
| Enforce application policy | Authorization through injected abstractions |

The Application Layer must not parse HTTP requests, write SQL, define tables,
implement email providers, format frontend responses, or decide business rules.
Those belong in Presentation, Infrastructure, or Domain.

This layer is the workflow coordinator. The Domain Layer decides **what is
allowed**; the Application Layer decides **which steps run and in what order**.

## 2. Application Services vs Domain Services

| Application Service | Domain Service |
|---|---|
| Coordinates one use case | Contains a business decision |
| Controls workflow | Defines what the business allows |
| Uses repositories and domain objects | Uses domain concepts only |
| Belongs to Application Layer | Belongs to Domain Layer |
| Example: `BookAppointment` | Example: `AppointmentAvailabilityService` |

The availability service answers:

```text
Is this time available under the scheduling rules?
```

The booking use case answers:

```text
How do I complete the booking operation?
```

| Question | Owner |
|---|---|
| Is the time slot well formed? | `TimeSlot` |
| Is the doctor free at that time? | `AppointmentAvailabilityService` |
| Which steps book an appointment? | `BookAppointment` application use case |
| How is the appointment stored? | Infrastructure repository implementation |
| What happened after booking? | `AppointmentBooked` event |

Keep Domain Services narrow. If a service starts opening transactions, building
HTTP responses, or sending email, that logic belongs in another layer.

## 3. Use Case Design

A use case represents one application operation with one clear responsibility.
`RegisterPatient` registers a patient; it does not also book an appointment or
create an invoice.

| Context | Use cases |
|---|---|
| Patient Management | `RegisterPatient`, `UpdatePatientAddress`, `DeactivatePatient` |
| Appointment Management | `BookAppointment`, `CancelAppointment`, `RescheduleAppointment` |
| Clinical Management | `StartEncounter`, `CompleteEncounter` |
| Billing & Payments | `CreateInvoice`, `IssueInvoice`, `RecordPayment` |

The general shape is:

```text
Input command or query
        |
        v
Application use case
        |
        +-- load required aggregates through repository ports
        +-- call domain behavior and Domain Services
        +-- save changed aggregates
        +-- commit through Unit of Work
        +-- dispatch recorded domain events
        v
Application result
```

Target package structure inside each bounded context:

```text
src/clinic_system/
├── patient_management/
│   ├── presentation/
│   ├── application/
│   │   ├── commands/
│   │   ├── queries/
│   │   ├── dto/
│   │   └── use_cases/
│   ├── domain/
│   │   ├── entities/
│   │   ├── value_objects/
│   │   ├── services/
│   │   ├── events/
│   │   └── repositories/
│   └── infrastructure/
├── appointment_management/
├── clinical_management/
└── billing/
```

Do not create empty folders for every possible pattern. Add packages when the
first real class or test needs them.

Use case tests inject in-memory repositories, fake units of work, and mock
dispatchers. They cover success and failure paths without FastAPI, PostgreSQL,
or real email delivery.

## 4. Commands and Queries

We use CQRS-style separation inside the modular monolith. There is no separate
read database and no separate service deployment.

| Command | Query |
|---|---|
| Requests a state change | Requests information |
| Uses domain behavior | Uses read-oriented access |
| Usually returns an identifier or aggregate | Returns a DTO or projection |
| May publish domain events | Does not publish domain events |
| Can fail business validation | Primarily validates query input |

Examples:

| Command | Query |
|---|---|
| `RegisterPatientCommand` | `GetPatientByIdQuery` |
| `BookAppointmentCommand` | `GetAppointmentByIdQuery` |
| `CancelAppointmentCommand` | `ListAppointmentsQuery` |
| `IssueInvoiceCommand` | `GetInvoiceDetailsQuery` |

Commands are imperative requests: `BookAppointmentCommand`. Events are past
tense facts: `AppointmentBooked`. A command can be rejected; an event has
already succeeded.

Commands and queries are DTOs in the Application Layer. They are not entities
and carry no business behavior.

## 5. DTOs and Validation

A DTO carries data across a boundary. DTOs are immutable, framework-neutral,
and free of business rules.

```python
from dataclasses import dataclass
from datetime import date
from uuid import UUID


@dataclass(frozen=True)
class RegisterPatientCommand:
    patient_id: UUID
    identity_number: str
    first_name: str
    last_name: str
    date_of_birth: date
    email: str
    street: str | None = None
    city: str | None = None
    province: str | None = None
    postal_code: str | None = None
    country: str | None = None


@dataclass(frozen=True)
class PatientResult:
    patient_id: UUID
    first_name: str
    last_name: str
```

Input validation and business validation are different:

| Input validation | Business validation |
|---|---|
| Is `first_name` present? | Is the patient eligible for registration? |
| Is the date a valid date? | Is the date of birth allowed by clinic rules? |
| Is the email syntactically valid? | Is the registration identity already registered? |
| Are field types correct? | Is the operation permitted for this user? |

Input validation may happen in the Presentation Layer and again at the
application boundary. Business validation stays in the Domain Layer:
`PatientName`, `DateOfBirth`, `TimeSlot`, and aggregate roots must reject invalid
data even if the request schema already checked it.

Use explicit application exceptions such as `DuplicatePatientIdentity`,
`DuplicatePatientId`, and `PatientNotFound`, not bare `ValueError`. Presentation
translates those exceptions into API responses.

## 6. Dependency Injection

Dependency Injection means supplying collaborators from outside instead of
creating them inside a use case.

Tightly coupled:

```python
class RegisterPatient:
    def execute(self, command: RegisterPatientCommand) -> None:
        repository = PostgresPatientRepository()
```

Injected:

```python
class RegisterPatient:
    def __init__(
        self,
        repository: "PatientRepository",
        unit_of_work: "UnitOfWork",
        event_dispatcher: "EventDispatcher",
    ) -> None:
        self.repository = repository
        self.unit_of_work = unit_of_work
        self.event_dispatcher = event_dispatcher
```

We use constructor injection. The composition root selects implementations:

| Environment | Repository | Unit of Work | Dispatcher |
|---|---|---|---|
| Unit test | In-memory fake | FakeUnitOfWork | Mock dispatcher |
| Integration test | Test database implementation | Database Unit of Work | In-process dispatcher |
| Production | PostgreSQL implementation | Database Unit of Work | In-process dispatcher, later outbox |

This supports Dependency Inversion, testability, loose coupling, and replaceable
infrastructure. Use cases import protocols, not concrete PostgreSQL classes.

## 7. RegisterPatient Use Case

The requirement is to register a patient with a unique registration identity, a
valid name, and a validated date of birth. Duplicate registration identities
are rejected; possible duplicate *people* remain a separate review rule recorded
in [`../requirements/use-cases.md`](../requirements/use-cases.md).

The command includes the registration identity required by
[infrastructure-and-persistence.md](infrastructure-and-persistence.md):

```python
@dataclass(frozen=True)
class RegisterPatientCommand:
    patient_id: UUID
    identity_number: str
    first_name: str
    last_name: str
    date_of_birth: date
    email: str
    street: str | None = None
    city: str | None = None
    province: str | None = None
    postal_code: str | None = None
    country: str | None = None
```

`patient_id` is the aggregate identity. `identity_number` is the clinic's
registration identity and is unique. `PatientRepository.exists_by_identity(...)`
checks the registration rule; database uniqueness is the final concurrent guard.

Ports used by the use case:

```python
class PatientRepository(Protocol):
    def exists(self, patient_id: UUID) -> bool: ...

    def exists_by_identity(self, identity_number: str) -> bool: ...

    def save(self, patient: "Patient") -> None: ...

    def get_by_id(self, patient_id: UUID) -> "Patient | None": ...


class UnitOfWork(Protocol):
    def commit(self) -> None: ...

    def rollback(self) -> None: ...


class EventDispatcher(Protocol):
    def dispatch(self, event: object) -> None: ...
```

Illustrative use case:

```python
class RegisterPatient:
    def __init__(
        self,
        repository: PatientRepository,
        unit_of_work: UnitOfWork,
        event_dispatcher: EventDispatcher,
    ) -> None:
        self.repository = repository
        self.unit_of_work = unit_of_work
        self.event_dispatcher = event_dispatcher

    def execute(self, command: RegisterPatientCommand) -> "Patient":
        if self.repository.exists_by_identity(command.identity_number):
            raise DuplicatePatientIdentity(command.identity_number)

        address = None
        if command.street is not None:
            address = Address(
                street=command.street,
                city=command.city,
                province=command.province,
                postal_code=command.postal_code,
                country=command.country,
            )

        patient = Patient.register(
            patient_id=command.patient_id,
            identity_number=command.identity_number,
            name=PatientName(
                first_name=command.first_name,
                last_name=command.last_name,
            ),
            date_of_birth=DateOfBirth(command.date_of_birth),
            email=command.email,
            address=address,
        )

        try:
            self.repository.save(patient)
            self.unit_of_work.commit()
        except Exception:
            self.unit_of_work.rollback()
            raise

        for event in patient.collect_events():
            self.event_dispatcher.dispatch(event)

        return patient
```

| Step | Owner |
|---|---|
| Receive and validate request shape | Presentation |
| Check duplicate registration identity | Application via `PatientRepository` |
| Validate name and birth date | Domain value objects |
| Create the aggregate | `Patient.register(...)` |
| Save and commit | Application via repository and Unit of Work |
| React to registration | Event handlers, once `PatientRegistered` is implemented |

`Patient.collect_events()` and `PatientRegistered` are planned, not yet
implemented. Until then, the notification example in
[solid-principles.md](solid-principles.md) uses an injected `NotificationSender`
for illustration only.

## 8. BookAppointment Use Case

The command uses `doctor_id` to match the ubiquitous-language decision;
requirements that say `practitioner_id` are translated at the boundary.

```python
@dataclass(frozen=True)
class BookAppointmentCommand:
    patient_id: UUID
    doctor_id: UUID
    start: datetime
    end: datetime
```

The use case coordinates patient identity, the availability rule, aggregate
creation, persistence, and event dispatch.

```python
class BookAppointment:
    def __init__(
        self,
        patient_repository: "PatientRepository",
        appointment_repository: "AppointmentRepository",
        availability_service: "AppointmentAvailabilityService",
        unit_of_work: "UnitOfWork",
        event_dispatcher: "EventDispatcher",
    ) -> None:
        self.patient_repository = patient_repository
        self.appointment_repository = appointment_repository
        self.availability_service = availability_service
        self.unit_of_work = unit_of_work
        self.event_dispatcher = event_dispatcher

    def execute(self, command: BookAppointmentCommand) -> Appointment:
        if not self.patient_repository.exists(command.patient_id):
            raise PatientNotFound(command.patient_id)

        time_slot = TimeSlot(start=command.start, end=command.end)
        self.availability_service.ensure_available(
            doctor_id=command.doctor_id,
            time_slot=time_slot,
        )

        appointment = Appointment.book(
            appointment_id=uuid4(),
            patient_id=command.patient_id,
            doctor_id=command.doctor_id,
            time_slot=time_slot,
        )

        try:
            self.appointment_repository.save(appointment)
            self.unit_of_work.commit()
        except Exception:
            self.unit_of_work.rollback()
            raise

        for event in appointment.collect_events():
            self.event_dispatcher.dispatch(event)

        return appointment
```

| Step | Owner |
|---|---|
| Check patient identity | Application via Patient Management port |
| Build `TimeSlot` | Application command translation |
| Check conflict | `AppointmentAvailabilityService` |
| Create aggregate and record event | `Appointment.book(...)` |
| Save and commit | Application via repository and Unit of Work |
| Dispatch `AppointmentBooked` | Application via `EventDispatcher` |

Patient active status and doctor existence are not yet implemented. They
require explicit cross-context contracts; the aggregate itself must not load
`Patient` or `StaffMember` objects. Concurrent booking protection belongs in
Infrastructure constraints or locking. See
[`../domain/appointment-booking-workflow.md`](../domain/appointment-booking-workflow.md).

Earlier sketches named this class `BookAppointmentService`; `BookAppointment`
is the target use-case name. Choose one name before implementation.

## 9. Transaction Management

A Unit of Work coordinates which changes commit together. A Repository answers
which aggregates are accessed.

| Repository | Unit of Work |
|---|---|
| Loads and saves aggregates | Coordinates the transaction |
| Collection-like access | Commits changes |
| Persistence access | Rolls back failed work |

Rules for `clinic-system`:

- one transaction changes aggregates inside one bounded context;
- the repository and Unit of Work share the same infrastructure session;
- a failure before commit calls `rollback()` and dispatches no events;
- a failed save dispatches no events;
- no transaction spans Patient Management, Appointment Management, Billing, an
  external API, or a message broker;
- `PatientRepository.exists(...)` is a cross-context fact, not part of the
  appointment transaction.

Current order in both use cases:

```text
load/check -> domain behavior -> save -> commit -> dispatch recorded events
```

The current order is simple and testable. It has a failure window after commit
and before dispatch, addressed in section 10.

## 10. Domain Event Coordination

Aggregates record facts; Application use cases coordinate delivery. The
dispatcher is an injected port:

```python
class EventDispatcher(Protocol):
    def dispatch(self, event: object) -> None: ...
```

```text
Appointment.book()          -> records AppointmentBooked
repository.save()           -> persists the aggregate
unit_of_work.commit()       -> makes the change durable
collect_events()            -> reads and clears recorded events
EventDispatcher.dispatch()  -> delivers to interested handlers
```

Handlers perform reactions such as confirmation notices and audit entries. They
do not make business decisions, and the aggregate does not know they exist.

Our initial modular monolith dispatches in-process. There is no Kafka,
RabbitMQ, or microservice requirement. Handlers must still be idempotent because
delivery can be retried.

The save/dispatch crash is the dual-write problem:

1. the aggregate is saved and committed;
2. the process crashes before dispatch;
3. the event is lost.

The target production order uses the Outbox Pattern:

```text
BEGIN
  save aggregate
  save event to outbox
COMMIT
outbox publisher reads pending events
publisher dispatches to handlers
publisher marks entries published
```

With an outbox, events must not be cleared before they are durably written. This
is future work; the current stage records the direction in
[domain-events.md](../domain/domain-events.md) and
[domain-services-events-repositories.md](../domain/domain-services-events-repositories.md).

Verification checklist:

- [ ] Use cases contain workflow, not business rules.
- [ ] Commands and results are immutable DTOs.
- [ ] Validation is split between boundary input checks and domain rules.
- [ ] Dependencies are constructor-injected protocols.
- [ ] Failed saves roll back and dispatch no events.
- [ ] Events are dispatched after commit.
- [ ] Cross-context transactions and brokers are not introduced.
