"""Rolling-window anomaly detection (FR-052, TM143)."""

from __future__ import annotations

import statistics
import threading
import uuid
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass(frozen=True)
class Anomaly:
    """A metric observation that departed from its rolling baseline."""

    anomaly_id: str
    metric: str
    observed_value: float
    baseline: float
    score: float
    detected_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def as_dict(self) -> dict[str, object]:
        """Return a JSON-serialisable representation."""
        return {
            "anomaly_id": self.anomaly_id,
            "metric": self.metric,
            "observed_value": self.observed_value,
            "baseline": self.baseline,
            "score": self.score,
            "detected_at": self.detected_at.isoformat(),
        }


class AnomalyDetector:
    """Median absolute deviation detector over a rolling window."""

    def __init__(
        self,
        *,
        window_size: int = 30,
        threshold: float = 3.5,
        min_samples: int = 5,
    ) -> None:
        self.window_size = window_size
        self.threshold = threshold
        self.min_samples = min_samples
        self._series: dict[str, deque[float]] = {}
        self._anomalies: deque[Anomaly] = deque(maxlen=200)
        self._lock = threading.Lock()

    def observe(self, metric: str, value: float) -> Anomaly | None:
        """Record a value and return an anomaly when it exceeds the baseline."""
        with self._lock:
            series = self._series.setdefault(metric, deque(maxlen=self.window_size))
            anomaly: Anomaly | None = None
            if len(series) >= self.min_samples:
                baseline = statistics.median(series)
                deviations = [abs(sample - baseline) for sample in series]
                mad = statistics.median(deviations)
                if mad == 0:
                    score = 0.0 if value == baseline else 999.0
                    changed = abs(value - baseline) > max(1e-9, abs(baseline) * 0.5)
                else:
                    score = 0.6745 * abs(value - baseline) / mad
                    changed = score >= self.threshold
                if changed:
                    anomaly = Anomaly(
                        anomaly_id=str(uuid.uuid4()),
                        metric=metric,
                        observed_value=value,
                        baseline=baseline,
                        score=round(score, 3),
                    )
                    self._anomalies.append(anomaly)
            series.append(value)
            return anomaly

    def recent(self, limit: int = 100) -> list[Anomaly]:
        """Return recent anomalies, newest first."""
        with self._lock:
            return list(reversed(list(self._anomalies)))[:limit]

    def reset(self) -> None:
        """Clear all baselines and anomalies."""
        with self._lock:
            self._series.clear()
            self._anomalies.clear()


anomaly_detector = AnomalyDetector()
"""Process-wide detector used by the observability API."""


__all__ = ["Anomaly", "AnomalyDetector", "anomaly_detector"]
