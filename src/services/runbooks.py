"""Incident runbook storage and execution (FR-054, TM140–TM142)."""

from __future__ import annotations

import threading
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

_NAMESPACE = uuid.UUID("9a7b7d54-6c1d-4ef5-bf9e-5e2f6f59f6aa")


class UnknownServiceError(ValueError):
    """Raised when a runbook targets a service unknown to the resolver."""


@dataclass(frozen=True)
class RunbookStep:
    """One executable step in a runbook."""

    order: int
    title: str
    action: str
    expected: str

    def as_dict(self) -> dict[str, object]:
        """Return a JSON-serialisable representation."""
        return {
            "order": self.order,
            "title": self.title,
            "action": self.action,
            "expected": self.expected,
            "status": "ready",
        }


@dataclass
class Runbook:
    """A named incident response procedure."""

    runbook_id: str
    title: str
    scenario: str
    steps: list[RunbookStep]
    author: str
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def as_dict(self) -> dict[str, object]:
        """Return a JSON-serialisable representation."""
        return {
            "runbook_id": self.runbook_id,
            "title": self.title,
            "scenario": self.scenario,
            "steps": [step.as_dict() for step in self.steps],
            "author": self.author,
            "updated_at": self.updated_at.isoformat(),
        }


def _step(order: int, title: str, action: str, expected: str) -> RunbookStep:
    return RunbookStep(order=order, title=title, action=action, expected=expected)


def _defaults() -> list[Runbook]:
    return [
        Runbook(
            runbook_id=str(uuid.uuid5(_NAMESPACE, "service-error-rate")),
            title="Service error rate above threshold",
            scenario="service_error_rate_high",
            author="platform",
            steps=[
                _step(
                    1,
                    "Identify",
                    "Find the failing service and endpoint in Grafana or /metrics.",
                    "The service and endpoint are identified.",
                ),
                _step(
                    2,
                    "Inspect logs",
                    "Search logs for the service and level=error in the last "
                    "15 minutes.",
                    "A recent error message is available.",
                ),
                _step(
                    3,
                    "Check dependencies",
                    "Verify database and downstream service health.",
                    "Dependencies are healthy or the failing dependency is known.",
                ),
                _step(
                    4,
                    "Mitigate",
                    "Roll back or restart the affected deployment.",
                    "Error rate returns below 1% for 10 minutes.",
                ),
            ],
        ),
        Runbook(
            runbook_id=str(uuid.uuid5(_NAMESPACE, "latency-spike")),
            title="Latency spike",
            scenario="service_latency_high",
            author="platform",
            steps=[
                _step(
                    1,
                    "Confirm",
                    "Compare the p95 latency panel with the 1-hour baseline.",
                    "The spike is confirmed and its start time is known.",
                ),
                _step(
                    2,
                    "Correlate",
                    "Check database connection pool and downstream latency.",
                    "The slow dependency is identified.",
                ),
                _step(
                    3,
                    "Scale",
                    "Scale the service replicas or raise the connection pool limit.",
                    "Capacity matches current demand.",
                ),
                _step(
                    4,
                    "Verify",
                    "Confirm p95 latency is back under 1.5 seconds.",
                    "Latency is stable for 10 minutes.",
                ),
            ],
        ),
        Runbook(
            runbook_id=str(uuid.uuid5(_NAMESPACE, "database-connection-failure")),
            title="Database connection failure",
            scenario="database_connection_failure",
            author="database",
            steps=[
                _step(
                    1,
                    "Check availability",
                    "Run the readiness probe and inspect the PostgreSQL "
                    "container status.",
                    "The database state is known.",
                ),
                _step(
                    2,
                    "Check capacity",
                    "Inspect active connections and disk usage.",
                    "Connection and disk usage are below limits.",
                ),
                _step(
                    3,
                    "Recover",
                    "Restart the database or release stale connections.",
                    "New connections succeed.",
                ),
                _step(
                    4,
                    "Verify",
                    "Confirm /readyz returns ready for every service.",
                    "All services report ready.",
                ),
            ],
        ),
    ]


class RunbookStore:
    """In-memory runbook CRUD and execution."""

    def __init__(self) -> None:
        self._runbooks: dict[str, Runbook] = {}
        self._lock = threading.Lock()
        self.reset()

    def reset(self) -> None:
        """Restore the seeded runbooks."""
        with self._lock:
            self._runbooks = {runbook.runbook_id: runbook for runbook in _defaults()}

    def list_runbooks(self) -> list[Runbook]:
        """Return all runbooks ordered by title."""
        with self._lock:
            return sorted(self._runbooks.values(), key=lambda runbook: runbook.title)

    def get(self, runbook_id: str) -> Runbook | None:
        """Return a runbook or ``None``."""
        with self._lock:
            return self._runbooks.get(runbook_id)

    def create(
        self,
        *,
        title: str,
        scenario: str,
        steps: list[RunbookStep],
        author: str,
    ) -> Runbook:
        """Create and store a runbook."""
        runbook = Runbook(
            runbook_id=str(uuid.uuid4()),
            title=title,
            scenario=scenario,
            steps=steps,
            author=author,
        )
        with self._lock:
            self._runbooks[runbook.runbook_id] = runbook
        return runbook

    def update(
        self,
        runbook_id: str,
        *,
        title: str | None = None,
        scenario: str | None = None,
        steps: list[RunbookStep] | None = None,
        author: str | None = None,
    ) -> Runbook | None:
        """Update a stored runbook."""
        with self._lock:
            runbook = self._runbooks.get(runbook_id)
            if runbook is None:
                return None
            if title is not None:
                runbook.title = title
            if scenario is not None:
                runbook.scenario = scenario
            if steps is not None:
                runbook.steps = steps
            if author is not None:
                runbook.author = author
            runbook.updated_at = datetime.now(timezone.utc)
            return runbook

    def execute(
        self,
        runbook_id: str,
        *,
        target_service: str | None = None,
        available_services: set[str] | None = None,
    ) -> dict[str, Any] | None:
        """Execute a runbook, validating the target service when supplied."""
        runbook = self.get(runbook_id)
        if runbook is None:
            return None
        if (
            available_services is not None
            and target_service is not None
            and target_service not in available_services
        ):
            raise UnknownServiceError(f"unknown service: {target_service}")
        return {
            "runbook_id": runbook.runbook_id,
            "title": runbook.title,
            "target_service": target_service,
            "status": "completed",
            "steps": [step.as_dict() for step in runbook.steps],
            "started_at": datetime.now(timezone.utc).isoformat(),
        }


runbook_store = RunbookStore()
"""Process-wide runbook store used by the observability API."""


__all__ = [
    "Runbook",
    "RunbookStep",
    "RunbookStore",
    "UnknownServiceError",
    "runbook_store",
]
