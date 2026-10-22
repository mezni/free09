"""Alert routing, deduplication and escalation (FR-053, TM131–TM133)."""

from __future__ import annotations

import threading
import uuid
from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone

TEAM_CHANNELS: dict[str, tuple[str, ...]] = {
    "backend": ("slack", "email"),
    "platform": ("slack", "email", "webhook"),
    "database": ("slack", "pagerduty"),
}
DEFAULT_CHANNELS = ("slack", "email")
CRITICAL_CHANNEL = "pagerduty"


def _now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class Alert:
    """An alert instance tracked by the router."""

    alert_id: str
    alertname: str
    severity: str
    team: str
    labels: dict[str, str]
    annotations: dict[str, str]
    status: str = "active"
    started_at: datetime = field(default_factory=_now)
    updated_at: datetime = field(default_factory=_now)

    def as_dict(self) -> dict[str, object]:
        """Return a JSON-serialisable representation."""
        return {
            "alert_id": self.alert_id,
            "alertname": self.alertname,
            "severity": self.severity,
            "team": self.team,
            "labels": self.labels,
            "annotations": self.annotations,
            "status": self.status,
            "started_at": self.started_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


class AlertRouter:
    """Route alerts to team channels with four-hour deduplication."""

    def __init__(self, repeat_interval: timedelta = timedelta(hours=4)) -> None:
        self.repeat_interval = repeat_interval
        self._active: dict[str, Alert] = {}
        self._lock = threading.Lock()

    @staticmethod
    def channels_for(severity: str, team: str) -> list[str]:
        """Return destination channels for a severity/team pair."""
        channels = list(TEAM_CHANNELS.get(team, DEFAULT_CHANNELS))
        if severity.lower() == "critical" and CRITICAL_CHANNEL not in channels:
            channels.append(CRITICAL_CHANNEL)
        return channels

    @staticmethod
    def _key(alertname: str, labels: Mapping[str, str]) -> str:
        return "|".join(
            (
                alertname,
                labels.get("service", ""),
                labels.get("instance", ""),
                labels.get("metric", ""),
            )
        )

    def record(
        self,
        alertname: str,
        labels: Mapping[str, str],
        annotations: Mapping[str, str] | None = None,
    ) -> tuple[Alert, bool, list[str], str | None]:
        """Record an alert, returning the alert, dedupe flag, channels, warning."""
        team = labels.get("team", "platform")
        severity = labels.get("severity", "warning")
        channels = self.channels_for(severity, team)
        key = self._key(alertname, labels)
        now = _now()

        with self._lock:
            existing = self._active.get(key)
            if existing is not None:
                duplicate = now - existing.updated_at < self.repeat_interval
                existing.updated_at = now
                if duplicate:
                    return existing, True, channels, None

            alert = Alert(
                alert_id=str(uuid.uuid4()),
                alertname=alertname,
                severity=severity,
                team=team,
                labels=dict(labels),
                annotations=dict(annotations or {}),
            )
            self._active[key] = alert
            warning = (
                None
                if channels
                else f"no notification channel configured for team {team!r}"
            )
            return alert, False, channels, warning

    def resolve(self, alert_id: str) -> Alert | None:
        """Mark an alert resolved, returning ``None`` when unknown."""
        with self._lock:
            for key, alert in self._active.items():
                if alert.alert_id == alert_id:
                    alert.status = "resolved"
                    alert.updated_at = _now()
                    self._active[key] = alert
                    return alert
        return None

    def list_alerts(self, status: str | None = None) -> list[Alert]:
        """Return alerts, newest first, optionally filtered by status."""
        with self._lock:
            alerts = sorted(
                self._active.values(),
                key=lambda alert: alert.started_at,
                reverse=True,
            )
        if status is None:
            return alerts
        return [alert for alert in alerts if alert.status == status]

    def reset(self) -> None:
        """Clear all tracked alerts."""
        with self._lock:
            self._active.clear()


alert_router = AlertRouter()
"""Process-wide alert router used by the observability API."""


__all__ = ["Alert", "AlertRouter", "alert_router"]
