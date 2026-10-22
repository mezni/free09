"""Structured request logging for Loki (FR-050, TM125–TM127).

The request path never blocks on the log shipper. Entries are written to the
process log and retained in a bounded buffer; a flush either ships the buffered
entries to Loki or leaves them buffered and reports why delivery failed.
"""

from __future__ import annotations

import json
import logging as stdlib_logging
import re
import threading
import uuid
from collections import deque
from collections.abc import Iterable
from dataclasses import dataclass, field
from datetime import datetime, timezone
from time import perf_counter

import httpx
from opentelemetry import trace as otel_trace
from starlette.types import ASGIApp, Message, Receive, Scope, Send

logger = stdlib_logging.getLogger("telco.access")

_HEADER_TRACE = re.compile(r"^00-([0-9a-f]{32})-[0-9a-f]{16}-[0-9a-f]{2}$")
_SERVICE_QUERY = re.compile(r'service\s*=\s*"([^"]+)"')
_LEVEL_QUERY = re.compile(r'(?:\.level|level)\s*(?:\|=|=)\s*"([^"]+)"')
_CONTAINS_QUERY = re.compile(r'(?:contains|\|=)\s*"([^"]+)"')


@dataclass(frozen=True)
class LogEntry:
    """One structured log record."""

    log_entry_id: str
    service: str
    level: str
    message: str
    timestamp: datetime
    request_id: str | None
    trace_id: str | None
    attributes: dict[str, object] = field(default_factory=dict)

    def as_dict(self) -> dict[str, object]:
        """Return a JSON-serialisable representation."""
        return {
            "log_entry_id": self.log_entry_id,
            "service": self.service,
            "level": self.level,
            "message": self.message,
            "timestamp": self.timestamp.isoformat(),
            "request_id": self.request_id,
            "trace_id": self.trace_id,
            "attributes": self.attributes,
        }


@dataclass(frozen=True)
class FlushResult:
    """Outcome of a log-buffer flush."""

    shipped: int
    buffered: int
    error: str | None = None

    @property
    def ok(self) -> bool:
        """Whether the flush delivered every buffered entry."""
        return self.error is None


class LokiShipError(RuntimeError):
    """Raised when a log batch cannot be delivered to Loki."""


class LokiShipper:
    """Minimal Loki push-API client."""

    def __init__(self, endpoint: str, *, timeout: float = 1.0) -> None:
        base = endpoint.rstrip("/")
        self.endpoint = (
            base if base.endswith("/loki/api/v1/push") else f"{base}/loki/api/v1/push"
        )
        self.timeout = timeout

    @classmethod
    def from_env(cls) -> LokiShipper | None:
        """Build a shipper from ``TELECO_LOG_LOKI_URL`` when configured."""
        import os

        base = os.environ.get("TELECO_LOG_LOKI_URL", "").strip()
        if not base:
            return None
        return cls(base)

    def ship(self, entries: Iterable[LogEntry]) -> int:
        """Send entries to Loki and return the number delivered."""
        batch = list(entries)
        if not batch:
            return 0

        streams: dict[tuple[str, str], list[list[str]]] = {}
        for entry in batch:
            labels = (entry.service, entry.level)
            streams.setdefault(labels, []).append(
                [
                    str(int(entry.timestamp.timestamp() * 1_000_000_000)),
                    json.dumps(entry.as_dict(), separators=(",", ":")),
                ]
            )

        payload = {
            "streams": [
                {
                    "stream": {"service": service, "level": level},
                    "values": values,
                }
                for (service, level), values in streams.items()
            ]
        }

        try:
            response = httpx.post(self.endpoint, json=payload, timeout=self.timeout)
            response.raise_for_status()
        except Exception as error:
            raise LokiShipError(str(error)) from error
        return len(batch)


class LogBuffer:
    """Bounded, thread-safe buffer of structured log entries."""

    def __init__(self, capacity: int = 2000) -> None:
        self.capacity = capacity
        self._entries: deque[LogEntry] = deque(maxlen=capacity)
        self._lock = threading.Lock()
        self.dropped = 0
        self.last_error: str | None = None

    def append(self, entry: LogEntry) -> None:
        """Append an entry, counting the oldest entry as dropped when full."""
        with self._lock:
            if len(self._entries) >= self.capacity:
                self.dropped += 1
            self._entries.append(entry)

    def __len__(self) -> int:
        with self._lock:
            return len(self._entries)

    def entries(self) -> list[LogEntry]:
        """Return a snapshot of the buffer, oldest first."""
        with self._lock:
            return list(self._entries)

    def reset(self) -> None:
        """Clear the buffer and counters (used by tests and rotations)."""
        with self._lock:
            self._entries.clear()
            self.dropped = 0
            self.last_error = None

    def search(
        self,
        *,
        service: str | None = None,
        level: str | None = None,
        contains: str | None = None,
        start: datetime | None = None,
        end: datetime | None = None,
        limit: int = 100,
    ) -> list[LogEntry]:
        """Search buffered entries, newest first."""
        with self._lock:
            snapshot = list(self._entries)

        matches: list[LogEntry] = []
        needle = contains.lower() if contains else None
        for entry in reversed(snapshot):
            if service is not None and entry.service != service:
                continue
            if level is not None and entry.level.lower() != level.lower():
                continue
            if needle is not None and needle not in entry.message.lower():
                continue
            if start is not None and entry.timestamp < start:
                continue
            if end is not None and entry.timestamp > end:
                continue
            matches.append(entry)
            if len(matches) >= limit:
                break
        return matches

    def flush(self, shipper: LokiShipper | None) -> FlushResult:
        """Ship the buffered entries, retaining them when delivery fails."""
        with self._lock:
            snapshot = list(self._entries)

        if shipper is None:
            self.last_error = "TELECO_LOG_LOKI_URL is not configured"
            return FlushResult(0, len(snapshot), self.last_error)
        if not snapshot:
            self.last_error = None
            return FlushResult(0, 0)

        try:
            shipped = shipper.ship(snapshot)
        except Exception as error:
            self.last_error = f"log shipper unavailable: {error}"
            return FlushResult(0, len(snapshot), self.last_error)

        with self._lock:
            for _ in range(min(shipped, len(self._entries))):
                self._entries.popleft()
            remaining = len(self._entries)
        self.last_error = None
        return FlushResult(shipped, remaining)


log_buffer = LogBuffer()
"""Process-wide buffer used by the application middleware."""


def parse_log_query(query: str) -> dict[str, str]:
    """Extract service, level and message filters from a Loki-style query."""
    service = _SERVICE_QUERY.search(query)
    level = _LEVEL_QUERY.search(query)
    contains = _CONTAINS_QUERY.search(query)
    filters: dict[str, str] = {}
    if service:
        filters["service"] = service.group(1)
    if level:
        filters["level"] = level.group(1)
    if contains:
        filters["contains"] = contains.group(1)
    return filters


def _parse_timestamp(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


def parse_time_range(value: str | None) -> tuple[datetime | None, datetime | None]:
    """Parse the contract's ``<start>-<end>`` range, tolerating ISO offsets."""
    if not value:
        return None, None
    for separator in (" - ", "/"):
        if separator in value:
            start_text, end_text = value.split(separator, 1)
            return _parse_timestamp(start_text), _parse_timestamp(end_text)
    raise ValueError("time_range must contain '<start> - <end>'")


def query_log_entries(
    buffer: LogBuffer,
    query: str,
    *,
    time_range: str | None = None,
    limit: int = 100,
) -> list[LogEntry]:
    """Run a Loki-style query against the local buffer."""
    filters = parse_log_query(query)
    start, end = parse_time_range(time_range)
    return buffer.search(
        service=filters.get("service"),
        level=filters.get("level"),
        contains=filters.get("contains"),
        start=start,
        end=end,
        limit=limit,
    )


def _header_map(scope: Scope) -> dict[str, str]:
    headers: dict[str, str] = {}
    for raw_key, raw_value in scope.get("headers", []):
        try:
            headers[raw_key.decode("latin-1").lower()] = raw_value.decode("latin-1")
        except (UnicodeDecodeError, AttributeError):  # pragma: no cover
            continue
    return headers


def _trace_id(headers: dict[str, str]) -> str | None:
    context = otel_trace.get_current_span().get_span_context()
    if context.is_valid:
        return f"{context.trace_id:032x}"
    match = _HEADER_TRACE.match(headers.get("traceparent", ""))
    return match.group(1) if match else None


class LoggingMiddleware:
    """Emit one structured log entry per HTTP request."""

    def __init__(
        self,
        app: ASGIApp,
        service_name: str,
        buffer: LogBuffer | None = None,
    ) -> None:
        self.app = app
        self.service_name = service_name
        self.buffer = buffer or log_buffer

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        headers = _header_map(scope)
        state = scope.setdefault("state", {})
        if not isinstance(state, dict):  # pragma: no cover - Starlette contract
            state = {}
            scope["state"] = state
        request_id = str(
            state.get("request_id") or headers.get("x-request-id") or uuid.uuid4()
        )
        state["request_id"] = request_id
        trace_id = _trace_id(headers)
        started = perf_counter()
        status_code = 500

        async def send_with_status(message: Message) -> None:
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = int(message["status"])
            await send(message)

        try:
            await self.app(scope, receive, send_with_status)
        finally:
            duration_ms = round((perf_counter() - started) * 1000, 3)
            level = "error" if status_code >= 500 else "info"
            entry = LogEntry(
                log_entry_id=str(uuid.uuid4()),
                service=self.service_name,
                level=level,
                message=f"{scope.get('method', 'GET')} {scope.get('path', '/')} "
                f"{status_code}",
                timestamp=datetime.now(timezone.utc),
                request_id=request_id,
                trace_id=trace_id,
                attributes={
                    "method": str(scope.get("method", "GET")),
                    "path": str(scope.get("path", "/")),
                    "status": status_code,
                    "duration_ms": duration_ms,
                },
            )
            self.buffer.append(entry)
            stdlib_logging.getLogger("telco.access").log(
                stdlib_logging.ERROR if level == "error" else stdlib_logging.INFO,
                json.dumps(entry.as_dict(), separators=(",", ":")),
            )


def install_logging(
    app: object,
    service_name: str,
    *,
    buffer: LogBuffer | None = None,
) -> None:
    """Attach the structured logging middleware to a FastAPI application."""
    add_middleware = getattr(app, "add_middleware", None)
    if add_middleware is None:  # pragma: no cover - defensive
        return
    add_middleware(
        LoggingMiddleware,
        service_name=service_name,
        buffer=buffer or log_buffer,
    )


__all__ = [
    "FlushResult",
    "LogBuffer",
    "LogEntry",
    "LoggingMiddleware",
    "LokiShipError",
    "LokiShipper",
    "install_logging",
    "log_buffer",
    "parse_log_query",
    "parse_time_range",
    "query_log_entries",
]
