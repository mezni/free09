"""Performance benchmark harness and phase-3 baseline comparison (FR-046).

The phase-3 baseline is the documented latency budget for the contract layer:
the health probe must answer within 100 ms and the contract document within
250 ms. Phase 5 must improve on that budget by at least 20%, so the targets are
80 ms and 200 ms respectively. The harness records p50/p95 latency, throughput
and error rate so the comparison is reproducible.
"""

from __future__ import annotations

import time
from dataclasses import dataclass

from fastapi import FastAPI
from fastapi.testclient import TestClient

TARGET_IMPROVEMENT = 0.20
"""Phase 5 must be at least 20% better than the phase-3 baseline."""


@dataclass(frozen=True)
class Baseline:
    """A phase-3 metric budget."""

    name: str
    p95_ms: float


PHASE3_BASELINE: tuple[Baseline, ...] = (
    Baseline(name="health", p95_ms=100.0),
    Baseline(name="openapi", p95_ms=250.0),
)
"""Documented phase-3 latency budgets (NFR-022 and the contract layer)."""

PHASE3_ERROR_RATE = 0.01


def _percentile(values: list[float], fraction: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = min(len(ordered) - 1, max(0, int(round(fraction * (len(ordered) - 1)))))
    return ordered[index]


def measure_endpoint(
    client: TestClient, path: str, *, iterations: int = 50
) -> dict[str, float]:
    """Measure latency, throughput and error rate for one endpoint."""
    durations: list[float] = []
    errors = 0
    started = time.perf_counter()
    for _ in range(iterations):
        request_started = time.perf_counter()
        response = client.get(path)
        durations.append((time.perf_counter() - request_started) * 1000.0)
        if response.status_code >= 500:
            errors += 1
    elapsed = time.perf_counter() - started

    return {
        "p50_ms": round(_percentile(durations, 0.50), 3),
        "p95_ms": round(_percentile(durations, 0.95), 3),
        "throughput_rps": round(iterations / elapsed, 2) if elapsed else 0.0,
        "error_rate": round(errors / iterations, 6),
    }


def run_benchmark(app: FastAPI, *, iterations: int = 50) -> dict[str, object]:
    """Run the benchmark suite against an application."""
    with TestClient(app) as client:
        client.get("/healthz")
        client.get("/openapi.json")
        return {
            "iterations": iterations,
            "metrics": {
                "health": measure_endpoint(client, "/healthz", iterations=iterations),
                "openapi": measure_endpoint(
                    client, "/openapi.json", iterations=iterations
                ),
            },
        }


def compare_to_baseline(result: dict[str, object]) -> dict[str, object]:
    """Compare benchmark output with the phase-3 baseline and the 20% target."""
    metrics = result.get("metrics", {})
    if not isinstance(metrics, dict):
        return {"passed": False, "reasons": ["benchmark produced no metrics"]}

    reasons: list[str] = []
    for baseline in PHASE3_BASELINE:
        metric = metrics.get(baseline.name, {})
        if not isinstance(metric, dict):
            reasons.append(f"{baseline.name}: no measurement")
            continue
        target = round(baseline.p95_ms * (1.0 - TARGET_IMPROVEMENT), 3)
        measured = float(metric.get("p95_ms", float("inf")))
        if measured > target:
            reasons.append(
                f"{baseline.name}: p95 {measured} ms exceeds the "
                f"{target} ms target (20% better than {baseline.p95_ms} ms)"
            )
        if float(metric.get("error_rate", 1.0)) > PHASE3_ERROR_RATE:
            reasons.append(
                f"{baseline.name}: error rate {metric.get('error_rate')} exceeds "
                f"{PHASE3_ERROR_RATE}"
            )

    return {"passed": not reasons, "reasons": reasons}


__all__ = [
    "PHASE3_BASELINE",
    "PHASE3_ERROR_RATE",
    "TARGET_IMPROVEMENT",
    "Baseline",
    "compare_to_baseline",
    "measure_endpoint",
    "run_benchmark",
]
