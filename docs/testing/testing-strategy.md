# Testing Strategy

## 1. Testing Pyramid

Testing must follow the same architectural boundaries as the application. A
fast unit test should verify domain rules; slower tests should verify that the
layers work together.

```text
                  /\
                 /  \
                / E2E \          few, broad, slower
               /------\
              /  API   \         HTTP contracts + real application wiring
             /----------\
            / Integration \      repository + SQLAlchemy + PostgreSQL
           /--------------\
          /     Unit       \     many, fast, isolated
         /__________________\
```

| Level | Tests | Example | Database? |
|---|---|---|---|
| Unit | One component | `Patient.register(...)` rejects blank identity | No |
| Application unit | Use case with fakes | `RegisterPatientUseCase` rejects duplicate identity | No |
| Integration | Several real components | `PostgresPatientRepository` saves and loads a patient | Yes |
| API integration | HTTP through real layers | `POST /api/v1/patients` persists a patient | Yes |
| End-to-end | Complete workflow | Receptionist registers and retrieves a patient | Yes |

The pyramid is a guide, not a quota. We want many fast tests and a smaller number
of slower tests that prove layer wiring.

Target structure:

```text
tests/
├── conftest.py
├── factories/
│   └── patient_factory.py
├── unit/
│   ├── domain/
│   │   └── test_patient.py
│   └── application/
│       └── test_register_patient.py
├── integration/
│   └── infrastructure/
│       └── test_patient_repository.py
├── api/
│   ├── test_patients.py
│   └── test_patients_integration.py
└── e2e/
    └── test_patient_registration_workflow.py
```

| Directory | Responsibility |
|---|---|
| `unit/domain` | Aggregates, entities, and value-object rules |
| `unit/application` | Use-case orchestration with fakes |
| `integration/infrastructure` | Repository, mapper, constraints, rollback |
| `api` | HTTP schema, status codes, headers, dependency wiring |
| `e2e` | Complete backend workflows |
| `factories` | Reusable domain objects and request payloads |

Install test dependencies:

```bash
uv add --dev pytest pytest-cov httpx
```

Run the suite:

```bash
uv run pytest
```

## 2. Unit Testing Strategy

Unit tests verify one component in isolation. They do not need FastAPI,
SQLAlchemy, or PostgreSQL.

Domain unit tests check invariants:

```python
from datetime import date
from uuid import uuid4

import pytest

from clinic_system.patient_management.domain.entities.patient import Patient
from clinic_system.patient_management.domain.value_objects.address import Address
from clinic_system.patient_management.domain.value_objects.date_of_birth import (
    DateOfBirth,
)
from clinic_system.patient_management.domain.value_objects.patient_name import (
    PatientName,
)


def make_patient(identity_number: str = "PAT-1001") -> Patient:
    return Patient.register(
        patient_id=uuid4(),
        identity_number=identity_number,
        name=PatientName("Alex", "Morgan"),
        date_of_birth=DateOfBirth(date(1990, 1, 1)),
        email="alex.morgan@example.com",
        address=Address(
            street="10 Main Street",
            city="Oakville",
            province="Ontario",
            postal_code="L6H 1A1",
            country="Canada",
        ),
    )


def test_patient_registration_sets_identity_and_active_state() -> None:
    patient = make_patient()

    assert patient.identity_number == "PAT-1001"
    assert patient.name.first_name == "Alex"
    assert patient.active is True


def test_patient_registration_rejects_blank_identity() -> None:
    with pytest.raises(ValueError):
        make_patient("   ")
```

Domain tests use the established names `patient_id` and `date_of_birth.value`.
The lesson's `patient.id` example is adapted to the current domain contract.

Application unit tests use fakes:

```python
class FakePatientRepository:
    def __init__(self) -> None:
        self.patients = {}

    def save(self, patient) -> None:
        self.patients[patient.patient_id] = patient

    def get_by_id(self, patient_id):
        return self.patients.get(patient_id)

    def exists_by_identity(self, identity_number: str) -> bool:
        return any(
            patient.identity_number == identity_number
            for patient in self.patients.values()
        )
```

| Scenario | Expected result |
|---|---|
| Valid patient | Registration succeeds |
| Existing identity number | Duplicate identity error |
| Invalid business data | Domain validation error |
| Repository failure | Error propagates through use case |
| Unknown patient ID | Not-found error |

Unit tests prove business behavior, not database behavior.

## 3. Integration Testing Strategy

Integration tests verify that several real components work together. The key
patient repository flow is:

```text
PostgresPatientRepository
          |
          v
      SQLAlchemy
          |
          v
   PostgreSQL test database
```

Repository tests should verify:

1. a patient can be saved;
2. a patient can be retrieved by `patient_id`;
3. all value objects are mapped correctly;
4. duplicate identity numbers are rejected;
5. database unique constraints work under repeated identities;
6. rollback leaves no persisted patient.

Example:

```python
def test_repository_saves_and_retrieves_patient(patient_repository) -> None:
    patient = make_patient("PAT-3001")

    patient_repository.save(patient)
    retrieved = patient_repository.get_by_id(patient.patient_id)

    assert retrieved is not None
    assert retrieved.patient_id == patient.patient_id
    assert retrieved.identity_number == "PAT-3001"
    assert retrieved.name.first_name == "Alex"
    assert retrieved.address.city == "Oakville"


def test_repository_rejects_duplicate_identity(patient_repository) -> None:
    patient_repository.save(make_patient("PAT-3002"))

    with pytest.raises(DuplicatePatientIdentityError):
        patient_repository.save(make_patient("PAT-3002"))
```

Integration tests use the real mapper and Unit of Work. They do not bypass the
repository with direct SQL asserts except to verify a constraint or cleanup.

If a raw SQL check is needed, keep it inside the test only:

```python
row = session.execute(
    text("SELECT identity_number FROM patients WHERE identity_number = :value"),
    {"value": "PAT-3002"},
).fetchone()
```

The production Application Layer never performs this kind of query.

## 4. API Testing Strategy

Step 18 API tests replace the use case with a fake. That verifies the HTTP
contract without PostgreSQL. Step 19 adds API integration tests with real
application wiring.

Fake-use-case test boundary:

```text
TestClient --> FastAPI route --> fake use case --> response schema
```

Real API integration boundary:

```text
TestClient
    |
    v
FastAPI router
    |
    v
RegisterPatientUseCase
    |
    v
SqlAlchemyUnitOfWork
    |
    v
PostgresPatientRepository
    |
    v
PostgreSQL test database
```

Example:

```python
def test_register_patient_persists_record(client) -> None:
    response = client.post(
        "/api/v1/patients",
        json=valid_patient_payload(identity_number="PAT-2001"),
    )

    assert response.status_code == 201
    patient_id = response.json()["id"]

    get_response = client.get(f"/api/v1/patients/{patient_id}")

    assert get_response.status_code == 200
    assert get_response.json()["identity_number"] == "PAT-2001"
```

API scenarios:

| Scenario | Expected status |
|---|---|
| Valid registration | `201 Created` |
| Missing `first_name` | `422 Unprocessable Content` |
| Missing required address field | `422` |
| Invalid UUID in GET path | `422` |
| Duplicate identity number | `409 Conflict` |
| Existing patient retrieval | `200 OK` |
| Unknown patient ID | `404 Not Found` |

Pydantic validates request structure. The domain and application validate
business meaning. Both paths must be tested:

```python
def test_missing_first_name_returns_422(client) -> None:
    payload = valid_patient_payload()
    del payload["first_name"]

    response = client.post("/api/v1/patients", json=payload)

    assert response.status_code == 422


def test_duplicate_identity_returns_409(client) -> None:
    payload = valid_patient_payload(identity_number="PAT-2002")

    assert client.post("/api/v1/patients", json=payload).status_code == 201
    assert client.post("/api/v1/patients", json=payload).status_code == 409
```

When overriding dependencies, restore them after each test:

```python
@pytest.fixture
def client(test_uow_factory, event_dispatcher) -> TestClient:
    def register_use_case() -> RegisterPatientUseCase:
        return RegisterPatientUseCase(
            uow_factory=test_uow_factory,
            event_dispatcher=event_dispatcher,
        )

    def get_use_case() -> GetPatientByIdUseCase:
        return GetPatientByIdUseCase(uow_factory=test_uow_factory)

    app.dependency_overrides[get_register_patient_use_case] = register_use_case
    app.dependency_overrides[get_get_patient_by_id_use_case] = get_use_case
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
```

The app must be configured for the test database before the client is created.
Override the use-case dependencies, not just `get_unit_of_work_factory`, because
a nested factory called directly inside another dependency is not automatically
managed by FastAPI.

## 5. End-to-End Testing Strategy

End-to-end tests verify the complete workflow rather than individual methods.
At this stage, "end-to-end" means the complete backend path from HTTP request to
PostgreSQL and back.

Scenario: a receptionist registers a patient.

| Step | Component | Expected behavior |
|---|---|---|
| 1 | Client | Submits patient information |
| 2 | FastAPI | Validates Pydantic schema |
| 3 | Application | Maps to command and checks duplicate identity |
| 4 | Domain | Creates a valid `Patient` aggregate |
| 5 | Infrastructure | Persists patient and commits |
| 6 | API | Returns `201`, ID, and `Location` header |

Example:

```python
def test_patient_registration_workflow(client) -> None:
    payload = valid_patient_payload(identity_number="PAT-4001")

    create_response = client.post("/api/v1/patients", json=payload)
    assert create_response.status_code == 201

    body = create_response.json()
    assert body["identity_number"] == "PAT-4001"
    assert body["active"] is True
    assert create_response.headers["location"].endswith(body["id"])

    get_response = client.get(f"/api/v1/patients/{body['id']}")
    assert get_response.status_code == 200
    assert get_response.json() == body
```

Workflow scenarios:

| Scenario | Expected result |
|---|---|
| Valid patient registration | `201 Created` |
| Duplicate identity number | `409 Conflict` |
| Missing name or address | `422` |
| Patient retrieval | `200 OK` |
| Unknown patient ID | `404 Not Found` |

Future browser E2E tests may add React and Playwright:

```text
Receptionist
    |
    v
Patient registration form
    |
    v
React frontend
    |
    v
FastAPI
    |
    v
PostgreSQL
```

That frontend workflow is out of scope here. The current E2E layer stops at the
HTTP API boundary.

## 6. Test Database Architecture

Use a dedicated PostgreSQL database for tests:

```text
clinic_system          development
clinic_system_test     automated tests
```

Never point tests at development or production data.

Environment variables:

```text
DATABASE_URL=postgresql+psycopg://user:password@localhost:5432/clinic_system
TEST_DATABASE_URL=postgresql+psycopg://user:password@localhost:5432/clinic_system_test
```

`.env.example` should contain placeholders only. Real credentials stay in local
`.env` files or CI secrets.

Test engine configuration:

```python
import os

import pytest
from sqlalchemy import create_engine


@pytest.fixture(scope="session")
def test_engine():
    engine = create_engine(
        os.environ["TEST_DATABASE_URL"],
        pool_pre_ping=True,
    )
    yield engine
    engine.dispose()
```

Session factory:

```python
from sqlalchemy.orm import sessionmaker


@pytest.fixture(scope="session")
def test_session_factory(test_engine):
    return sessionmaker(
        bind=test_engine,
        expire_on_commit=False,
    )
```

Schema rules:

- apply Alembic migrations to `clinic_system_test`;
- use an isolated schema if multiple test runners share a server;
- never rely on production seed data;
- never call `Base.metadata.create_all()` as a production migration substitute;
- verify the database name contains `test` before running destructive cleanup.

Fail fast if `TEST_DATABASE_URL` is missing or points to the development
database. A mistaken target can destroy real clinic data.

## 7. Transaction Isolation and Cleanup

Every test must start from a predictable state.

Bad isolation:

```text
Test 1: insert PAT-1001 --> commit --> leave data behind
Test 2: insert PAT-1001 --> fails unexpectedly
```

Good isolation:

```text
Test 1: insert --> rollback
Test 2: insert --> rollback
Test 3: insert --> rollback
```

Two common strategies:

| Strategy | How it works | Trade-off |
|---|---|---|
| Savepoint per test | Outer transaction is rolled back after each test | Fast, but app must share the connection |
| Clean schema per test | Delete/truncate tables or rebuild schema | Simpler wiring, slower and riskier with shared DBs |

Savepoint approach:

```python
from sqlalchemy import event
from sqlalchemy.orm import sessionmaker


@pytest.fixture
def db_session(test_engine):
    connection = test_engine.connect()
    outer_transaction = connection.begin()
    session_factory = sessionmaker(bind=connection, expire_on_commit=False)
    session = session_factory()

    @event.listens_for(session, "after_transaction_end")
    def restart_savepoint(session, transaction):
        if transaction.nested and not transaction._parent.nested:
            session.expire_all()
            session.begin_nested()

    session.begin_nested()

    yield session

    session.close()
    outer_transaction.rollback()
    connection.close()
```

Critical rule:

```text
Rolling back a separate test session does not undo commits made by the
application's own session.
```

Therefore, the repository and application Unit of Work used by a test must be
bound to the same test connection when using savepoint rollback. For API tests,
override the use-case dependencies with instances built from a test Unit of Work
factory bound to that connection.

Cleanup rules:

- use unique identity numbers per test where possible;
- clear FastAPI dependency overrides after every test;
- dispose engines at session end;
- close sessions even when a test fails;
- assert the table is empty in a dedicated isolation test;
- never clean tables in a production-configured database.

Rollback tests should verify failed workflows too:

```python
def test_duplicate_identity_does_not_create_second_patient(client) -> None:
    payload = valid_patient_payload(identity_number="PAT-5001")

    assert client.post("/api/v1/patients", json=payload).status_code == 201
    assert client.post("/api/v1/patients", json=payload).status_code == 409

    list_response = client.get("/api/v1/patients?identity_number=PAT-5001")
    assert len(list_response.json()) == 1
```

If a list endpoint does not exist, use a repository or raw test query to make
the same assertion.

## 8. Test Fixtures and Factories

Fixtures provide reusable dependencies. Factories provide reusable data. Keep
them separate.

`tests/conftest.py` responsibilities:

- FastAPI `client` fixture;
- `test_engine` and `test_session_factory`;
- `patient_repository` fixture bound to the test session;
- `test_uow_factory` for API integration;
- `event_dispatcher` fake for post-commit events;
- `fake_uow` for application unit tests;
- automatic cleanup after each test.

Example repository fixture:

```python
@pytest.fixture
def patient_repository(db_session) -> PostgresPatientRepository:
    return PostgresPatientRepository(db_session)
```

Example fake Unit of Work fixture:

```python
@pytest.fixture
def fake_uow() -> FakeUnitOfWork:
    return FakeUnitOfWork(patient_repository=FakePatientRepository())
```

Factory functions:

```python
def valid_patient_payload(identity_number: str = "PAT-1001") -> dict:
    return {
        "identity_number": identity_number,
        "first_name": "Alex",
        "last_name": "Morgan",
        "date_of_birth": "1990-01-01",
        "email": "alex.morgan@example.com",
        "street": "10 Main Street",
        "city": "Oakville",
        "province": "Ontario",
        "postal_code": "L6H 1A1",
        "country": "Canada",
    }


def patient_aggregate(identity_number: str = "PAT-1001") -> Patient:
    return Patient.register(
        patient_id=uuid4(),
        identity_number=identity_number,
        name=PatientName("Alex", "Morgan"),
        date_of_birth=DateOfBirth(date(1990, 1, 1)),
        email="alex.morgan@example.com",
        address=Address(
            street="10 Main Street",
            city="Oakville",
            province="Ontario",
            postal_code="L6H 1A1",
            country="Canada",
        ),
    )
```

Fixture guidelines:

- prefer function scope for data that can collide;
- use session scope only for engines and immutable configuration;
- make unusual cases explicit instead of hiding them in defaults;
- keep credentials out of fixtures;
- do not hide database commits inside data factories;
- name fixtures after the dependency they provide.

## 9. Coverage Strategy

Install coverage support:

```bash
uv add --dev pytest-cov
```

Run coverage:

```bash
uv run pytest --cov=clinic_system --cov-report=term-missing
```

Generate an HTML report:

```bash
uv run pytest --cov=clinic_system --cov-report=html
```

The report is written to:

```text
htmlcov/
```

Add `htmlcov/` and `.coverage` to `.gitignore`.

Prioritize behavior over a percentage:

| Priority | Behavior |
|---|---|
| High | Duplicate identity registration |
| High | Transaction rollback on failure |
| High | Patient mapping through repository |
| High | HTTP status translation |
| Medium | Not-found and validation paths |
| Medium | Event dispatch after successful commit |
| Low | Defensive branches with no business meaning |

A high coverage number does not prove correctness. Coverage only shows which
lines executed. Tests must assert the right behavior.

Suggested minimum coverage policy after implementation stabilizes:

| Layer | Target |
|---|---|
| Domain | High, because rules are cheap to test |
| Application | High, including failure paths |
| Infrastructure | Critical repository paths |
| Presentation | All status codes used by current endpoints |

Do not use a single global threshold to hide untested critical workflows.

## 10. Architectural Boundary Tests

Architecture tests protect the design from erosion. They check structural rules
that ordinary behavior tests may miss.

Rules to verify:

| Rule | Check |
|---|---|
| Domain independence | Domain does not import `fastapi` |
| Domain independence | Domain does not import `sqlalchemy` |
| Application independence | Application does not import HTTP request types |
| Persistence abstraction | Application imports repository protocols, not implementations |
| Presentation separation | Routes do not open sessions |
| Presentation separation | Routes do not call repositories directly |
| Dependency direction | Infrastructure imports inner-layer contracts |

Example structural test:

```python
import ast
from pathlib import Path


def python_files(path: str):
    return Path(path).rglob("*.py")


def imported_modules(path: Path) -> set[str]:
    tree = ast.parse(path.read_text())
    names = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(alias.name for alias in node.names)
        if isinstance(node, ast.ImportFrom) and node.module:
            names.add(node.module)

    return names


def test_domain_does_not_import_web_or_database_frameworks() -> None:
    forbidden = ("fastapi", "sqlalchemy", "psycopg")

    for path in python_files("src/clinic_system/patient_management/domain"):
        for module in imported_modules(path):
            assert not module.startswith(forbidden)


def test_routes_do_not_import_persistence_models() -> None:
    for path in python_files("src/clinic_system/patient_management/presentation"):
        imports = imported_modules(path)

        assert "sqlalchemy" not in imports
        assert not any("infrastructure.persistence.models" in name for name in imports)
```

Add checks for direct session usage:

```python
def test_routes_do_not_open_database_sessions() -> None:
    for path in python_files("src/clinic_system/patient_management/presentation"):
        source = path.read_text()

        assert "SessionFactory(" not in source
        assert "sessionmaker(" not in source
        assert "session.execute(" not in source
```

Architecture tests are guardrails, not a replacement for review. When a rule
must change, update the test deliberately and record the architectural decision.

Verification checklist:

- [ ] Unit tests cover domain and application behavior.
- [ ] Integration tests use the real repository and test database.
- [ ] API tests cover fake and real dependency paths.
- [ ] E2E tests verify the complete registration workflow.
- [ ] `TEST_DATABASE_URL` is separate from `DATABASE_URL`.
- [ ] Each test cleans up or rolls back its data.
- [ ] Coverage report is reviewed for critical paths.
- [ ] Architecture tests enforce inward dependencies.
