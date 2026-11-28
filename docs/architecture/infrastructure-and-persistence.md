# Infrastructure Layer & Persistence Design

## 1. Infrastructure Layer Responsibilities

The Infrastructure Layer implements the technical capabilities the inner layers
need. In `clinic-system`, that means PostgreSQL persistence, SQLAlchemy ORM
models, repository implementations, Unit of Work, migrations, configuration, and
later external service adapters.

| Component | Responsibility | Technology |
|---|---|---|
| Database | Persist clinic data | PostgreSQL |
| ORM | Map persistence records to tables | SQLAlchemy 2.x |
| Repository | Implement aggregate persistence | SQLAlchemy `Session` |
| Unit of Work | Coordinate database transactions | SQLAlchemy `Session` |
| Migrations | Evolve the schema | Alembic |
| Configuration | Load connection settings | Environment variables |

Dependency direction:

```text
Application use case --> Repository protocol --> Infrastructure implementation
Domain aggregate     --> no persistence dependency
Infrastructure       --> SQLAlchemy, Psycopg, PostgreSQL
```

The Application Layer defines what it needs through protocols. Infrastructure
provides implementations. The Domain Layer must never import SQLAlchemy,
Psycopg, FastAPI, or database models.

Rejected coupling:

```python
class Patient:
    def save_to_postgres(self) -> None:
        ...
```

Accepted separation:

```python
class PostgresPatientRepository:
    def save(self, patient: Patient) -> None:
        ...
```

Although we use one PostgreSQL database initially, the four bounded contexts
own their data. There is no global repository giving every context unrestricted
access to every table.

## 2. Domain Models vs Persistence Models

A Domain Model represents business concepts and rules. A Persistence Model
describes how data is stored. They are deliberately separate.

Domain model:

```python
from dataclasses import dataclass
from datetime import date
from uuid import UUID, uuid4


@dataclass(frozen=True)
class PatientName:
    first_name: str
    last_name: str


@dataclass(frozen=True)
class DateOfBirth:
    value: date


@dataclass
class Address:
    street: str
    city: str
    province: str
    postal_code: str
    country: str


@dataclass
class Patient:
    patient_id: UUID
    identity_number: str
    name: PatientName
    date_of_birth: DateOfBirth
    email: str
    address: Address | None = None
    active: bool = True

    @classmethod
    def register(
        cls,
        patient_id: UUID,
        identity_number: str,
        name: PatientName,
        date_of_birth: DateOfBirth,
        email: str,
        address: Address | None = None,
    ) -> "Patient":
        if not identity_number.strip():
            raise ValueError("registration identity is required")
        return cls(
            patient_id=patient_id,
            identity_number=identity_number,
            name=name,
            date_of_birth=date_of_birth,
            email=email,
            address=address,
        )

    @classmethod
    def rehydrate(
        cls,
        patient_id: UUID,
        identity_number: str,
        first_name: str,
        last_name: str,
        date_of_birth: date,
        email: str,
        street: str | None,
        city: str | None,
        province: str | None,
        postal_code: str | None,
        country: str | None,
        active: bool,
    ) -> "Patient":
        address = None
        if street is not None:
            address = Address(street, city, province, postal_code, country)
        return cls(
            patient_id=patient_id,
            identity_number=identity_number,
            name=PatientName(first_name, last_name),
            date_of_birth=DateOfBirth(date_of_birth),
            email=email,
            address=address,
            active=active,
        )

    def deactivate(self) -> None:
        if not self.active:
            raise ValueError("patient is already inactive")
        self.active = False
```

`patient_id` is the aggregate identity. `identity_number` is the clinic's
registration identity and is unique. The exact format and uniqueness policy must
be confirmed with registration requirements, but the model now owns it.

Persistence model:

```python
class PatientRecord:
    id: UUID
    identity_number: str
    first_name: str
    last_name: str
    date_of_birth: date
    email: str
    street: str | None
    city: str | None
    province: str | None
    postal_code: str | None
    country: str | None
    active: bool
```

| Domain model | Persistence model |
|---|---|
| `Patient` | `PatientRecord` |
| `PatientName` | `first_name`, `last_name` columns |
| `DateOfBirth` | `date_of_birth` column |
| `Address` | Address columns |
| `deactivate()` | No persistence equivalent |
| Business invariants | Database constraints complement domain rules |
| Independent of SQLAlchemy | Uses SQLAlchemy mapping |

Database constraints do not replace domain validation. Both are needed: the
domain explains the rule, and the database protects it under concurrency.

## 3. PostgreSQL Database Design

We use PostgreSQL because relational consistency, constraints, and transactions
fit the clinic's initial needs. One database does not mean one shared model.

| Table | Owning context | Notes |
|---|---|---|
| `patients` | Patient Management | Registration identity and demographics |
| `appointments` | Appointment Management | Added when that context is persisted |
| `encounters` | Clinical Management | Added when that context is persisted |
| `invoices`, `payments` | Billing & Payments | Added when that context is persisted |

`patients` initial columns:

| Column | Type | Constraints |
|---|---|---|
| `id` | `UUID` | Primary key |
| `identity_number` | `VARCHAR(100)` | `NOT NULL`, `UNIQUE`, indexed |
| `first_name` | `VARCHAR(100)` | `NOT NULL` |
| `last_name` | `VARCHAR(100)` | `NOT NULL` |
| `date_of_birth` | `DATE` | `NOT NULL` |
| `email` | `VARCHAR(255)` | `NOT NULL` |
| `street` | `VARCHAR(255)` | Nullable initially |
| `city` | `VARCHAR(100)` | Nullable initially |
| `province` | `VARCHAR(100)` | Nullable initially |
| `postal_code` | `VARCHAR(20)` | Nullable initially |
| `country` | `VARCHAR(100)` | Nullable initially |
| `active` | `BOOLEAN` | `NOT NULL`, default `TRUE` |

The unique index on `identity_number` is the final protection against two
concurrent registrations claiming the same identity. Application checks are
helpful but not sufficient.

Do not add foreign keys from one bounded context's table to another context's
table in this stage. Appointment Management stores `patient_id` and
`doctor_id` as identity references; their existence is checked through
application contracts.

Dependencies and local configuration:

```bash
uv add sqlalchemy "psycopg[binary]" alembic
uv add --dev pytest
uv tree
```

Create `.env` in the project root:

```text
DATABASE_URL=postgresql+psycopg://clinic_user:your_password@localhost:5432/clinic_system
```

Never commit `.env`. Add to `.gitignore`:

```text
.env
.env.*
!.env.example
```

Create `.env.example` with placeholders only:

```text
DATABASE_URL=postgresql+psycopg://username:password@localhost:5432/clinic_system
```

Create the development database with your PostgreSQL tooling:

```sql
CREATE USER clinic_user WITH PASSWORD 'your_password';

CREATE DATABASE clinic_system
    OWNER clinic_user;
```

Use secure credentials outside development.

## 4. SQLAlchemy Configuration

Suggested shared persistence location:

```text
src/clinic_system/shared/infrastructure/persistence/
├── base.py
├── database.py
├── sqlalchemy_unit_of_work.py
└── models/
```

Base:

```python
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass
```

Database configuration:

```python
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.environ["DATABASE_URL"]

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)

SessionFactory = sessionmaker(
    bind=engine,
    expire_on_commit=False,
)
```

`pool_pre_ping=True` detects stale connections before use.
`expire_on_commit=False` keeps objects usable after commit for mapping into
domain objects.

Load environment variables before starting the application through the shell,
Docker Compose, or a development configuration tool. Do not hard-code a
password in source code or `alembic.ini`.

`Base.metadata.create_all()` is useful for isolated tests, not for production
schema evolution. Use Alembic migrations instead.

## 5. ORM Models

Location:

```text
src/clinic_system/patient_management/infrastructure/persistence/models/patient_record.py
```

```python
from datetime import date
from uuid import UUID

from sqlalchemy import Boolean, Date, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from clinic_system.shared.infrastructure.persistence.base import Base


class PatientRecord(Base):
    __tablename__ = "patients"

    id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
    )
    identity_number: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
        index=True,
    )
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    date_of_birth: Mapped[date] = mapped_column(Date, nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    street: Mapped[str | None] = mapped_column(String(255), nullable=True)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    province: Mapped[str | None] = mapped_column(String(100), nullable=True)
    postal_code: Mapped[str | None] = mapped_column(String(20), nullable=True)
    country: Mapped[str | None] = mapped_column(String(100), nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
```

| Python attribute | Database column | Type |
|---|---|---|
| `id` | `id` | UUID |
| `identity_number` | `identity_number` | VARCHAR, unique |
| `first_name` | `first_name` | VARCHAR |
| `last_name` | `last_name` | VARCHAR |
| `date_of_birth` | `date_of_birth` | DATE |
| `email` | `email` | VARCHAR |
| address fields | address columns | VARCHAR, nullable |
| `active` | `active` | BOOLEAN |

`PatientRecord` has no `register()` or `deactivate()` methods. It is a storage
representation, not the business object.

## 6. Domain-to-Persistence Mapping

A Mapper converts between `Patient` and `PatientRecord`. It belongs in
Infrastructure so SQLAlchemy details stay out of the Domain and Application
layers.

Location:

```text
src/clinic_system/patient_management/infrastructure/persistence/mappers/patient_mapper.py
```

```python
from clinic_system.patient_management.domain.entities.patient import Patient
from clinic_system.patient_management.infrastructure.persistence.models.patient_record import (
    PatientRecord,
)


class PatientMapper:
    @staticmethod
    def to_domain(record: PatientRecord) -> Patient:
        return Patient.rehydrate(
            patient_id=record.id,
            identity_number=record.identity_number,
            first_name=record.first_name,
            last_name=record.last_name,
            date_of_birth=record.date_of_birth,
            email=record.email,
            street=record.street,
            city=record.city,
            province=record.province,
            postal_code=record.postal_code,
            country=record.country,
            active=record.active,
        )

    @staticmethod
    def to_record(patient: Patient) -> PatientRecord:
        return PatientRecord(
            id=patient.patient_id,
            identity_number=patient.identity_number,
            first_name=patient.name.first_name,
            last_name=patient.name.last_name,
            date_of_birth=patient.date_of_birth.value,
            email=patient.email,
            street=patient.address.street if patient.address else None,
            city=patient.address.city if patient.address else None,
            province=patient.address.province if patient.address else None,
            postal_code=patient.address.postal_code if patient.address else None,
            country=patient.address.country if patient.address else None,
            active=patient.active,
        )
```

```text
Patient aggregate --> PatientMapper --> PatientRecord --> SQLAlchemy --> PostgreSQL
PatientRecord --> PatientMapper --> Patient aggregate
```

Mapping rules:

- `to_domain()` uses `rehydrate(...)`, not `register(...)`, so loading a patient
  does not record a new `PatientRegistered` event;
- `to_record()` extracts primitive values from value objects;
- the Mapper does not open sessions, query tables, or commit;
- the repository owns persistence operations.

## 7. Repository Implementations

The repository accepts and returns domain objects. It never exposes
`PatientRecord` to the Application Layer.

Protocol:

```python
from typing import Protocol
from uuid import UUID

from clinic_system.patient_management.domain.entities.patient import Patient


class PatientRepository(Protocol):
    def get_by_id(self, patient_id: UUID) -> Patient | None: ...

    def exists(self, patient_id: UUID) -> bool: ...

    def exists_by_identity(self, identity_number: str) -> bool: ...

    def save(self, patient: Patient) -> None: ...
```

SQLAlchemy implementation:

```python
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from clinic_system.patient_management.domain.entities.patient import Patient
from clinic_system.patient_management.infrastructure.persistence.mappers.patient_mapper import (
    PatientMapper,
)
from clinic_system.patient_management.infrastructure.persistence.models.patient_record import (
    PatientRecord,
)


class PostgresPatientRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_id(self, patient_id: UUID) -> Patient | None:
        record = self.session.get(PatientRecord, patient_id)
        if record is None:
            return None
        return PatientMapper.to_domain(record)

    def exists(self, patient_id: UUID) -> bool:
        statement = (
            select(PatientRecord.id)
            .where(PatientRecord.id == patient_id)
            .limit(1)
        )
        return self.session.scalar(statement) is not None

    def exists_by_identity(self, identity_number: str) -> bool:
        statement = (
            select(PatientRecord.id)
            .where(PatientRecord.identity_number == identity_number)
            .limit(1)
        )
        return self.session.scalar(statement) is not None

    def save(self, patient: Patient) -> None:
        record = self.session.get(PatientRecord, patient.patient_id)
        mapped = PatientMapper.to_record(patient)

        if record is None:
            self.session.add(mapped)
        else:
            for field in (
                "identity_number",
                "first_name",
                "last_name",
                "date_of_birth",
                "email",
                "street",
                "city",
                "province",
                "postal_code",
                "country",
                "active",
            ):
                setattr(record, field, getattr(mapped, field))

        try:
            self.session.flush()
        except IntegrityError as error:
            raise DuplicatePatientIdentity(patient.identity_number) from error
```

`flush()` exposes constraint violations before the use case commits. The
repository translates infrastructure errors into application-level exceptions.
The unique database constraint remains the concurrency safeguard.

## 8. Unit of Work

The Unit of Work owns repository instances so they share one SQLAlchemy
session. This prevents saving with one session and committing another.

Protocol in `shared/application/unit_of_work.py`:

```python
from typing import Protocol

from clinic_system.patient_management.domain.repositories.patient_repository import (
    PatientRepository,
)


class UnitOfWork(Protocol):
    patient_repository: PatientRepository

    def __enter__(self) -> "UnitOfWork": ...

    def __exit__(
        self,
        exc_type: object,
        exc_value: object,
        traceback: object,
    ) -> None: ...

    def commit(self) -> None: ...

    def rollback(self) -> None: ...
```

SQLAlchemy implementation:

```python
from sqlalchemy.orm import Session, sessionmaker

from clinic_system.patient_management.domain.repositories.patient_repository import (
    PatientRepository,
)
from clinic_system.patient_management.infrastructure.persistence.repositories.postgres_patient_repository import (
    PostgresPatientRepository,
)


class SqlAlchemyUnitOfWork:
    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self.session_factory = session_factory
        self.session: Session | None = None
        self.patient_repository: PatientRepository | None = None

    def __enter__(self) -> "SqlAlchemyUnitOfWork":
        self.session = self.session_factory()
        self.patient_repository = PostgresPatientRepository(self.session)
        return self

    def __exit__(
        self,
        exc_type: object,
        exc_value: object,
        traceback: object,
    ) -> None:
        try:
            if exc_type is not None:
                self.rollback()
        finally:
            if self.session is not None:
                self.session.close()

    def commit(self) -> None:
        if self.session is None:
            raise RuntimeError("unit of work has no active session")
        self.session.commit()

    def rollback(self) -> None:
        if self.session is None:
            raise RuntimeError("unit of work has no active session")
        self.session.rollback()
```

Behavior:

- creates a session on entry;
- exposes repositories built with that session;
- commits only when the use case calls `commit()`;
- rolls back when an exception escapes the context;
- closes the session on exit.

Tests use `FakeUnitOfWork` with in-memory repositories. The Application Layer
sees only the protocol in both cases.

## 9. Transaction Management

A database transaction makes a group of changes all-or-nothing.

| ACID property | Meaning | Clinic example |
|---|---|---|
| Atomicity | All changes succeed or none do | Patient registration completes fully or not at all |
| Consistency | Data remains valid | Registration identity stays unique |
| Isolation | Concurrent work is controlled | Two registrations cannot claim one identity |
| Durability | Committed data survives restart | A registered patient remains after restart |

Registration transaction:

```text
BEGIN
  check registration identity
  insert patient record
COMMIT
```

If the insert fails, the transaction rolls back. No partial patient record is
left behind.

Use case with Unit of Work:

```python
class RegisterPatient:
    def __init__(
        self,
        unit_of_work: UnitOfWork,
        event_dispatcher: "EventDispatcher",
    ) -> None:
        self.unit_of_work = unit_of_work
        self.event_dispatcher = event_dispatcher

    def execute(self, command: "RegisterPatientCommand") -> Patient:
        with self.unit_of_work as uow:
            if uow.patient_repository.exists_by_identity(
                command.identity_number
            ):
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
            uow.patient_repository.save(patient)
            uow.commit()
            events = patient.collect_events()

        for event in events:
            self.event_dispatcher.dispatch(event)

        return patient
```

The use case does not know whether the Unit of Work uses PostgreSQL, SQLite, or
memory. It also does not open a SQLAlchemy session.

Transaction boundaries:

- one transaction stays inside one bounded context;
- no transaction spans an external API, email provider, or broker;
- appointment conflict protection needs constraints, locking, or serialization;
- event delivery needs the Outbox Pattern for reliability.

`BEGIN`, `COMMIT`, and `ROLLBACK` apply to database work. They cannot roll back
an email already sent. That is why external reactions are event handlers, not
steps inside the database transaction.

## 10. Database Migrations

Alembic version-controls the database schema. We do not manually alter
production tables and we do not use `create_all()` in production.

Initialize Alembic from the repository root:

```bash
uv run alembic init migrations
```

This creates:

```text
migrations/
├── versions/
├── env.py
└── script.py.mako

alembic.ini
```

In `migrations/env.py`, import `Base` and every model module so the table is
registered in metadata:

```python
from clinic_system.shared.infrastructure.persistence.base import Base
from clinic_system.patient_management.infrastructure.persistence.models import patient_record

target_metadata = Base.metadata
```

Configure the URL from the environment. Do not commit a password in
`alembic.ini`.

Generate the first migration:

```bash
uv run alembic revision --autogenerate -m "create patients table"
```

Review the generated migration before applying it:

```bash
uv run alembic upgrade head
uv run alembic history
uv run alembic current
```

Migration workflow:

```text
change SQLAlchemy model
        |
        v
generate migration
        |
        v
review and correct migration
        |
        v
apply to a test database
        |
        v
commit model and migration together
```

Review checklist:

- column types and lengths;
- `NULL` and default values;
- primary keys, unique constraints, and indexes;
- data transformations for populated databases;
- reversible `downgrade()` behavior where possible;
- no accidental cross-context foreign keys.

Autogenerated migrations are candidates, not final code.

Persistence testing levels:

| Test type | Tests | Database required? |
|---|---|---|
| Unit | Domain rules | No |
| Application | Use-case orchestration | No |
| Integration | Repository, mapper, constraints, rollback | Yes |

Integration tests use a dedicated test database or isolated transactions. Never
run them against production.

Verification checklist:

- [ ] Domain objects contain no SQLAlchemy imports.
- [ ] `PatientRecord` contains no business behavior.
- [ ] Repository input and output are domain objects.
- [ ] Repository and Unit of Work share one session.
- [ ] Duplicate identity is enforced by both domain and database.
- [ ] Use case commits explicitly and dispatches events after commit.
- [ ] Schema changes are made through reviewed Alembic migrations.
- [ ] Secrets are supplied by environment variables and never committed.
