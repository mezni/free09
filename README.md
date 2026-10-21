
# telco-si

A simulated telecom platform for learning and testing:

- Python microservices built with FastAPI
- PostgreSQL shared database with service-owned schemas
- Synthetic telecom customers, plans, subscriptions, and billing data
- Traefik API gateway
- Authentication, authorization, and audit logging
- AI agents with tools, guardrails, observability, and evaluations

## Technology Stack

- Python 3.12
- uv
- FastAPI
- PostgreSQL
- SQLAlchemy and Alembic
- pytest and Ruff
- Docker Compose
- Traefik
- OpenTelemetry

## Development Setup

Install dependencies:

```bash
uv sync
```

Run tests:

```bash
uv run pytest
```

Check code quality:

```bash
uv run ruff check .
```

## Project Status

Step 1: Repository initialization.

