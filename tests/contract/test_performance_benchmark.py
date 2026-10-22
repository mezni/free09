"""Performance benchmark tests (FR-046, TM122–TM124)."""

from __future__ import annotations

import pytest

from src.main import app
from src.observability.benchmark import (
    PHASE3_BASELINE,
    TARGET_IMPROVEMENT,
    compare_to_baseline,
    run_benchmark,
)

pytestmark = [pytest.mark.unit, pytest.mark.performance]


def test_health_probe_meets_the_latency_budget():
    """The health probe answers well inside the 100 ms budget (NFR-022)."""
    result = run_benchmark(app, iterations=10)
    metrics = result["metrics"]
    assert isinstance(metrics, dict)
    health = metrics["health"]
    assert isinstance(health, dict)
    assert health["p95_ms"] < 100.0


def test_benchmark_meets_the_twenty_percent_improvement_target():
    """The measured metrics satisfy the phase-3 baseline improvement target."""
    result = run_benchmark(app, iterations=10)
    comparison = compare_to_baseline(result)
    assert comparison["passed"] is True, comparison["reasons"]


def test_baseline_records_the_phase3_budget():
    """The baseline is explicit so a regression can be reasoned about."""
    assert {baseline.name for baseline in PHASE3_BASELINE} == {"health", "openapi"}
    assert TARGET_IMPROVEMENT == 0.20
    assert all(baseline.p95_ms > 0 for baseline in PHASE3_BASELINE)
