
# Development Log — telco-si

## Step 1: Initialize Repository

**Goal:** Establish a consistent Python development environment and repository structure.

**Problem:** Without a standard project structure, development, testing, and future service integration become harder to maintain.

**Solution:**
- Initialized the project using `uv`.
- Added `pytest` and Ruff as development dependencies.
- Created directories for services, infrastructure, synthetic data, AI agents, and tests.
- Added project documentation.

**Trade-offs:**
- Started with one repository instead of multiple repositories to simplify local development.
- Will use a shared PostgreSQL instance for the learning environment.
- Will maintain service ownership boundaries even though the database is shared.

**Active Work:** Repository initialization.

**Code State:** Python environment and project structure initialized.

**Next Steps:** Configure Docker Compose and PostgreSQL.


## Step 2: Set Up Docker Compose and PostgreSQL

**Goal:** Run PostgreSQL through a reproducible local Docker environment.

**Problem:** A locally installed database can create inconsistent development environments and make setup difficult to reproduce.

**Solution:**
- Added `docker-compose.yml`.
- Configured PostgreSQL 16 and the `telco_si` database.
- Added a named persistent volume.
- Configured a PostgreSQL health check.
- Added environment-based configuration using `.env`.

**Trade-offs:**
- One shared PostgreSQL instance simplifies the learning environment.
- A named volume preserves data across container recreation.
- The initial database role has elevated privileges; service-specific least-privilege roles will be introduced later.

**Active Work:** Local database infrastructure.

**Code State:** PostgreSQL runs through Docker Compose and accepts connections.

**Next Steps:** Design the telecom database schemas, tables, relationships, indexes, and constraints.


## Step 3: Design the Initial Database Schema

**Goal:** Establish the relational foundation for the telecom simulation platform.

**Problem:** Microservices and synthetic data require a consistent data model with enforceable relationships and constraints.

**Solution:**
- Created eight PostgreSQL domain schemas.
- Added core IAM, CRM, catalog, subscription, device, billing, support, and audit tables.
- Added primary keys, foreign keys, uniqueness rules, check constraints, and indexes.
- Configured Alembic to manage database migrations.
- Added schema verification tests.

**Trade-offs:**
- Used one PostgreSQL database with separate schemas for easier local development.
- Used explicit SQL DDL for the initial migration to make the baseline schema clear.
- Some cross-table business rules will be enforced by services and data validation rather than simple constraints.

**Active Work:** Database foundation.

**Code State:** Initial migration creates the core telecom tables.

**Next Steps:** Build the deterministic fake data generator foundation using Faker, seeded randomness, and stable synthetic identifiers.

